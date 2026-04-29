from __future__ import annotations
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MetaResponse(BaseModel):
    scraped_at: str | None = None  # ISO 8601, e.g. "2026-04-27T10:00:00Z"


class DataResponse(BaseModel, Generic[T]):
    data: T
    meta: MetaResponse = Field(default_factory=MetaResponse)
