import uuid
from fastapi import APIRouter
from app.schemas.scrape_job import ScrapeJobCreate, ScrapeJobResponse
from app.schemas.common import DataResponse

router = APIRouter()


@router.post("", response_model=DataResponse[ScrapeJobResponse], status_code=201)
async def create_scrape_job(job_in: ScrapeJobCreate) -> DataResponse[ScrapeJobResponse]:
    """Create a scrape job. Phase 1: placeholder."""
    placeholder = ScrapeJobResponse(
        id=1,
        status="pending",
        route_id=job_in.route_id,
        created_at="2026-04-27T10:00:00Z",  # TODO: replace with real timestamp once persistence lands
        completed_at=None,
    )
    return DataResponse(data=placeholder)


@router.get("/{job_id}", response_model=DataResponse[ScrapeJobResponse])
async def get_scrape_job(job_id: uuid.UUID) -> DataResponse[ScrapeJobResponse]:
    """Get scrape job status. Phase 1: placeholder."""
    placeholder = ScrapeJobResponse(
        id=job_id,
        status="pending",
        route_id=0,
        created_at="2026-04-27T10:00:00Z",  # TODO: replace with real timestamp once persistence lands
        completed_at=None,
    )
    return DataResponse(data=placeholder)
