# app/models/scrape_result.py
import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScrapeResult(Base):
    """Cached bus schedule data returned by a scrape job."""

    __tablename__ = "scrape_results"
    __table_args__ = (
        Index("idx_scrape_results_route_id", "route_id"),
        Index("idx_scrape_results_scraped_at", "scraped_at"),
        Index("idx_scrape_results_job_id", "job_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scrape_jobs.id"), nullable=False
    )
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.id"), nullable=False)
    provider_id: Mapped[int] = mapped_column(Integer, ForeignKey("providers.id"), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    price_jpy: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    available_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    booking_url: Mapped[str] = mapped_column(Text, nullable=False)
    pickup_stop: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # pickup_stop format: {"vi": "...", "en": "...", "ja": "..."}
    dropoff_stop: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    is_stale: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    job: Mapped["ScrapeJob"] = relationship("ScrapeJob", foreign_keys=[job_id], lazy="select")
    route: Mapped["Route"] = relationship("Route", foreign_keys=[route_id], lazy="select")
    provider: Mapped["Provider"] = relationship("Provider", foreign_keys=[provider_id], lazy="select")
