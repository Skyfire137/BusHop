# app/models/province.py
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # name format: {"vi": "Hà Nội", "en": "Hanoi", "ja": "ハノイ"}
