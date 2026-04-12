"""
Reports API — retrieve daily reports and subscription documents from the archive.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid
from app.database import get_db
from app.models.user import User
from app.models.report import DailyReport, SubscriptionDocument
from app.api.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


class DailyReportOut(BaseModel):
    id: uuid.UUID
    date: date
    status: str
    archive_url: Optional[str]

    class Config:
        from_attributes = True


class SubscriptionDocumentOut(BaseModel):
    id: uuid.UUID
    subscription_id: Optional[uuid.UUID]
    document_markdown: Optional[str]
    archive_url: Optional[str]
    toc_json: Optional[dict]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[DailyReportOut])
async def list_reports(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyReport)
        .where(DailyReport.user_id == user.id)
        .order_by(DailyReport.date.desc())
        .limit(30)
    )
    return result.scalars().all()


@router.get("/{report_id}", response_model=DailyReportOut)
async def get_report(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DailyReport).where(DailyReport.id == report_id, DailyReport.user_id == user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/documents", response_model=List[SubscriptionDocumentOut])
async def get_report_documents(
    report_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SubscriptionDocument).where(
            SubscriptionDocument.daily_report_id == report_id,
            SubscriptionDocument.user_id == user.id,
        )
    )
    return result.scalars().all()
