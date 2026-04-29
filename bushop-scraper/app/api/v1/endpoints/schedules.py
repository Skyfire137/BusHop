from datetime import date as date_type

from fastapi import APIRouter, Query
from app.schemas.schedule import ScheduleResponse
from app.schemas.common import DataResponse, MetaResponse

router = APIRouter()


@router.get("", response_model=DataResponse[list[ScheduleResponse]])
async def get_schedules(
    origin_id: int = Query(..., description="ID of departure province"),
    destination_id: int = Query(..., description="ID of destination province"),
    date: date_type = Query(..., description="Travel date (YYYY-MM-DD)"),
) -> DataResponse[list[ScheduleResponse]]:
    """Search bus schedules. Phase 1: empty list."""
    return DataResponse(data=[], meta=MetaResponse(scraped_at=None))
