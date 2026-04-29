# app/models/route.py
from datetime import datetime

from sqlalchemy import Boolean, String, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Route(Base):
    """Bus route between two cities, identified by slug strings."""

    __tablename__ = "routes"
    __table_args__ = (UniqueConstraint("origin_id", "destination_id", name="uq_routes_origin_destination"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    origin_id: Mapped[str] = mapped_column(String(50), nullable=False)
    destination_id: Mapped[str] = mapped_column(String(50), nullable=False)
    origin_name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # origin_name format: {"vi": "Tokyo", "en": "Tokyo", "ja": "東京"}
    destination_name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_popular: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
