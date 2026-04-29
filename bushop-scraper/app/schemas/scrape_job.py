from __future__ import annotations
import uuid
from datetime import datetime, date
from typing import Literal
from pydantic import BaseModel, ConfigDict

ScrapeJobStatus = Literal["pending", "running", "completed", "failed"]


class ScrapeJobCreate(BaseModel):
    route_id: int
    travel_date: date


class ScrapeJobResponse(BaseModel):
    id: uuid.UUID
    status: ScrapeJobStatus
    route_id: int
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
