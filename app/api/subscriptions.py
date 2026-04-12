from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
import uuid
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.api.auth import get_current_user

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


class SubscriptionCreate(BaseModel):
    name: str
    source_type: str  # rss | youtube | article
    source_url: str
    rip_profile: Optional[List[str]] = None


class SubscriptionUpdate(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None
    rip_profile: Optional[List[str]] = None


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    source_url: str
    active: bool
    rip_profile: Optional[List[str]]
    last_checked_at: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SubscriptionOut])
async def list_subscriptions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    return result.scalars().all()


@router.post("/", response_model=SubscriptionOut, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    data: SubscriptionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = Subscription(user_id=user.id, **data.model_dump())
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.patch("/{sub_id}", response_model=SubscriptionOut)
async def update_subscription(
    sub_id: uuid.UUID,
    data: SubscriptionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.id == sub_id, Subscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(sub, field, value)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.delete("/{sub_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    sub_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription).where(Subscription.id == sub_id, Subscription.user_id == user.id)
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    await db.delete(sub)
    await db.commit()
