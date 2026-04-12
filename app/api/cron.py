"""
Cron endpoint — triggered by Render cron job (or any scheduler) daily.
Protected by Authorization: Bearer <CRON_SECRET_KEY>.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.settings import settings

router = APIRouter(prefix="/cron", tags=["cron"])
bearer = HTTPBearer()


def verify_cron_secret(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if not settings.CRON_SECRET_KEY:
        raise HTTPException(status_code=503, detail="CRON_SECRET_KEY not configured")
    if credentials.credentials != settings.CRON_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid cron secret")


@router.post("/daily-rip")
async def trigger_daily_rip(
    background_tasks: BackgroundTasks,
    _: None = Depends(verify_cron_secret),
):
    """
    Kick off the daily rip pipeline in the background.
    Pipeline implementation wired in Phase 4/5.
    """
    # TODO Phase 4/5: background_tasks.add_task(run_daily_pipeline)
    return {"status": "queued", "message": "Daily rip pipeline enqueued (pipeline not yet implemented)"}
