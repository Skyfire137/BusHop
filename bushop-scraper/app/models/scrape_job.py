# app/models/scrape_job.py
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScrapeJob(Base):
    """Tracks each scrape attempt for a route/provider pair."""

    __tablename__ = "scrape_jobs"
    __table_args__ = (
        Index("idx_scrape_jobs_status", "status"),
        Index("idx_scrape_jobs_route_id", "route_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    provider_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("providers.id"), nullable=True
    )
    # NULL provider_id means scrape all providers
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="pending")
    triggered_by: Mapped[str] = mapped_column(String(20), nullable=False, server_default="scheduler")
    started_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    route: Mapped["Route"] = relationship("Route", foreign_keys=[route_id], lazy="select")
    provider: Mapped["Provider"] = relationship("Provider", foreign_keys=[provider_id], lazy="select")
