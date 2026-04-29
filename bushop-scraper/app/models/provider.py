# app/models/provider.py
from datetime import datetime

from sqlalchemy import Boolean, String, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Provider(Base):
    """Bus operator (e.g. Willer Express, Kosoku Bus)."""

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # name format: {"vi": "Willer Express", "en": "Willer Express", "ja": "ウィラーエクスプレス"}
    base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
