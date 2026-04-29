from fastapi import APIRouter
from app.schemas.route import RouteResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.get("", response_model=DataResponse[list[RouteResponse]])
async def get_routes() -> DataResponse[list[RouteResponse]]:
    """Returns all routes with i18n province names. Phase 1: empty list."""
    return DataResponse(data=[])
