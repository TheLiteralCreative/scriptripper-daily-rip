import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (
        # Idempotency: one URL per subscription — same URL in two subscriptions is allowed
        UniqueConstraint("subscription_id", "source_url", name="uq_subscription_source_url"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # pending | transcribing | ripping | done | error
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subscription: Mapped["Subscription"] = relationship(back_populates="content_items")
    rip_results: Mapped[List["RipResult"]] = relationship(back_populates="content_item", cascade="all, delete-orphan")


class RipResult(Base):
    __tablename__ = "rip_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("content_items.id", ondelete="CASCADE"), nullable=False, index=True)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    result_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    content_item: Mapped["ContentItem"] = relationship(back_populates="rip_results")
