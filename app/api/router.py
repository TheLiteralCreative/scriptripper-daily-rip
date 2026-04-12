from fastapi import APIRouter
from app.api import auth, subscriptions, rips, reports, cron

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(subscriptions.router)
api_router.include_router(rips.router)
api_router.include_router(reports.router)
api_router.include_router(cron.router)
