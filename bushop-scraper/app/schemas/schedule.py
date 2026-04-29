from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ScheduleResponse(BaseModel):
    id: uuid.UUID
    route_id: int
    operator_name: str
    departure_time: datetime
    arrival_time: datetime
    price: int
    scraped_at: datetime
    is_stale: bool

    model_config = ConfigDict(from_attributes=True)
