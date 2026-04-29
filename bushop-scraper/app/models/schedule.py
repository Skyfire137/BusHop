# app/models/schedule.py
import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text, Date, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    route_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("routes.id"), nullable=True
    )
    scrape_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scrape_jobs.id"), nullable=True
    )
    operator_name: Mapped[str] = mapped_column(String(200), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    arrival_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    available_seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    booking_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    travel_date: Mapped[date] = mapped_column(Date, nullable=False)

    route: Mapped["Route"] = relationship(
        "Route", foreign_keys=[route_id], lazy="select"
    )
    scrape_job: Mapped["ScrapeJob"] = relationship(
        "ScrapeJob", foreign_keys=[scrape_job_id], lazy="select"
    )
