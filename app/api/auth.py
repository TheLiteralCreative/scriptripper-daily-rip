from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.settings import settings
import httpx

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.get("/google/login")
async def google_login():
    """Return Google OAuth URL for client-side redirect."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.CORS_ORIGINS.split(',')[0]}/auth/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    from urllib.parse import urlencode
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return {"auth_url": url}


@router.post("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """Exchange Google auth code for tokens, create/fetch user, return JWT."""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": f"{settings.CORS_ORIGINS.split(',')[0]}/auth/callback",
                "grant_type": "authorization_code",
            },
        )
    token_data = token_resp.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=token_data["error"])

    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
    userinfo = userinfo_resp.json()

    result = await db.execute(select(User).where(User.email == userinfo["email"]))
    user = result.scalar_one_or_none()

    if not user:
        user = User(email=userinfo["email"], google_id=userinfo.get("sub"))
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"access_token": create_access_token(str(user.id)), "token_type": "bearer"}
