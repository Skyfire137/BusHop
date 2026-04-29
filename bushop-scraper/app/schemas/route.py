from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class ProvinceI18n(BaseModel):
    vi: str
    en: str
    ja: str


class RouteResponse(BaseModel):
    id: int
    slug: str
    origin_id: int | None = None
    destination_id: int | None = None
    origin_name: ProvinceI18n
    destination_name: ProvinceI18n

    model_config = ConfigDict(from_attributes=True)
