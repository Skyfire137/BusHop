import uuid
from datetime import datetime, date

import pytest

from app.schemas.scrape_job import ScrapeJobCreate, ScrapeJobResponse
from app.schemas.schedule import ScheduleResponse


def test_scrape_job_create_requires_travel_date():
    job = ScrapeJobCreate(route_id=1, travel_date=date(2026, 5, 1))
    assert job.travel_date == date(2026, 5, 1)


def test_scrape_job_create_missing_travel_date_raises():
    with pytest.raises(Exception):  # pydantic ValidationError
        ScrapeJobCreate(route_id=1)


def test_scrape_job_response_id_is_uuid():
    # ScrapeJobResponse does not include travel_date — only fields defined in schema
    job = ScrapeJobResponse(
        id=uuid.uuid4(),
        status="pending",
        route_id=1,
        created_at=datetime.now(),
        completed_at=None,
    )
    assert isinstance(job.id, uuid.UUID)


def test_schedule_response_datetimes():
    now = datetime.now()
    s = ScheduleResponse(
        id=uuid.uuid4(),
        route_id=1,
        operator_name="Willer",
        departure_time=now,
        arrival_time=now,
        price=3000,
        scraped_at=now,
        is_stale=False,
    )
    assert isinstance(s.departure_time, datetime)
