"""
Rip Library API — browse available rip tasks, manage favorites.
Rip task definitions live in app/services/rip_library.py (Phase 4).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import List
import uuid
from app.database import get_db
from app.models.user import User, FavoriteRip
from app.api.auth import get_current_user

router = APIRouter(prefix="/rips", tags=["rips"])

# Placeholder rip library — will be replaced by dynamic load in Phase 4
RIP_LIBRARY: List[dict] = [
    {"task_name": "overview", "title": "Overview", "description": "High-level summary of the full piece."},
    {"task_name": "key_points", "title": "Key Points", "description": "Bullet list of the most important points."},
    {"task_name": "action_items", "title": "Action Items", "description": "Concrete next steps and to-dos."},
    {"task_name": "quotes", "title": "Notable Quotes", "description": "Memorable or significant quotes."},
    {"task_name": "how_to", "title": "How-To Breakdown", "description": "Step-by-step instructions extracted from the content."},
    {"task_name": "ideas", "title": "Ideas & Inspiration", "description": "Creative or innovative ideas mentioned."},
    {"task_name": "research", "title": "Research & References", "description": "Data points, studies, and sources cited."},
]


@router.get("/library")
async def get_rip_library():
    return RIP_LIBRARY


@router.get("/favorites", response_model=List[str])
async def get_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FavoriteRip).where(FavoriteRip.user_id == user.id))
    return [r.task_name for r in result.scalars().all()]


@router.post("/favorites/{task_name}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    task_name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not any(r["task_name"] == task_name for r in RIP_LIBRARY):
        raise HTTPException(status_code=404, detail="Unknown rip task")
    existing = await db.execute(
        select(FavoriteRip).where(FavoriteRip.user_id == user.id, FavoriteRip.task_name == task_name)
    )
    if existing.scalar_one_or_none():
        return {"status": "already_favorited"}
    db.add(FavoriteRip(user_id=user.id, task_name=task_name))
    await db.commit()
    return {"status": "added"}


@router.delete("/favorites/{task_name}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    task_name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        delete(FavoriteRip).where(FavoriteRip.user_id == user.id, FavoriteRip.task_name == task_name)
    )
    await db.commit()
