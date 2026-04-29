# app/services/base_scraper.py
import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, UTC
from typing import ClassVar

from playwright.async_api import async_playwright, Page
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.provider import Provider
from app.models.route import Route
from app.models.scrape_job import ScrapeJob
from app.models.scrape_result import ScrapeResult
from app.services.exceptions import ScraperError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RETRY_DELAYS: list[int] = [2, 4, 8]  # seconds, exponential backoff

_USER_AGENTS: tuple[str, ...] = (
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
)

_BROWSER_ARGS: list[str] = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
]

_NAVIGATION_TIMEOUT_MS: int = 30_000

_MAX_RETRIES: int = 3


# ---------------------------------------------------------------------------
# Data transfer object
# ---------------------------------------------------------------------------


class ScrapeResultData(BaseModel):
    """Typed container for one bus schedule row returned by a provider scraper.

    This is a pure Pydantic model — not persisted directly. BaseScraper
    translates instances into ScrapeResult ORM rows via _save_results().
    """

    departure_time: datetime
    arrival_time: datetime
    price_jpy: int
    seat_type: str | None = None
    available_seats: int | None = None
    booking_url: str
    pickup_stop: dict | None = None
    # pickup_stop format: {"vi": "...", "en": "...", "ja": "..."}
    dropoff_stop: dict | None = None
    raw_data: dict | None = None


# ---------------------------------------------------------------------------
# Abstract base scraper
# ---------------------------------------------------------------------------


class BaseScraper(ABC):
    """Abstract base class for all provider scrapers.

    Subclasses must:
    - Set class attribute ``provider_code`` to match Provider.code in DB.
    - Implement ``scrape_route()``.

    Usage::

        class WillerScraper(BaseScraper):
            provider_code = "willer"

            async def scrape_route(self, page, route, date):
                ...
                return [ScrapeResultData(...)]
    """

    provider_code: ClassVar[str]  # set by subclass

    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session
        self._provider_id: int | None = None  # resolved lazily on first use

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def scrape_with_retry(
        self,
        job_id: str,
        route: Route,
        date: date,
    ) -> list[ScrapeResultData]:
        """Orchestrate scraping with retry logic.

        Marks the job as ``running`` on the first attempt, updates
        ``retry_count`` on each failure, and finally marks the job
        ``completed`` or ``failed``.

        Args:
            job_id: UUID string of the ScrapeJob record.
            route: Route ORM instance to scrape.
            date: Travel date.

        Returns:
            List of normalised result data objects.

        Raises:
            ScraperError: When all retries are exhausted.
        """
        await self._update_job_status(
            job_id,
            status="running",
            started_at=datetime.now(UTC),
        )

        last_error: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                results = await self._run_single_attempt(route, date, attempt)

                provider_id = await self._get_provider_id()
                await self._save_results(
                    job_id=job_id,
                    route_id=route.id,
                    provider_id=provider_id,
                    results=results,
                    route=route,
                )
                await self._update_job_status(
                    job_id,
                    status="completed",
                    completed_at=datetime.now(UTC),
                )
                return results

            except Exception as exc:
                last_error = exc
                await self._update_job_status(
                    job_id,
                    status="running",
                    retry_count=attempt + 1,
                )
                if attempt < _MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAYS[attempt])

        await self._update_job_status(
            job_id,
            status="failed",
            error=str(last_error),
        )
        raise ScraperError(
            f"Scrape failed after {_MAX_RETRIES} retries: {last_error}"
        ) from last_error

    # ------------------------------------------------------------------
    # Abstract method — subclass implements this
    # ------------------------------------------------------------------

    @abstractmethod
    async def scrape_route(
        self,
        page: Page,
        route: Route,
        date: date,
    ) -> list[ScrapeResultData]:
        """Provider-specific scraping logic.

        Receives a Playwright ``Page`` ready for interaction.
        Must return a list of ``ScrapeResultData`` instances.

        Args:
            page: An open Playwright browser page.
            route: Route to scrape.
            date: Travel date.

        Returns:
            Raw extracted schedule data.
        """
        ...

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _run_single_attempt(
        self,
        route: Route,
        travel_date: date,
        attempt: int,
    ) -> list[ScrapeResultData]:
        """Open a fresh browser, run scrape_route(), close browser.

        A new browser is created for every attempt so that failed attempts
        do not leave stale browser state behind.

        Args:
            route: Route to scrape.
            travel_date: Travel date.
            attempt: Zero-based attempt index, used to select user-agent.

        Returns:
            List of scraped result data.
        """
        user_agent = _USER_AGENTS[attempt % len(_USER_AGENTS)]

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=_BROWSER_ARGS,
            )
            try:
                page = await browser.new_page(user_agent=user_agent)
                page.set_default_timeout(_NAVIGATION_TIMEOUT_MS)
                return await self.scrape_route(page, route, travel_date)
            finally:
                await browser.close()

    async def _get_provider_id(self) -> int:
        """Resolve Provider.id from provider_code, caching the result.

        Returns:
            Integer primary key of the matching Provider row.

        Raises:
            ScraperError: When no Provider with matching code exists.
        """
        if self._provider_id is not None:
            return self._provider_id

        result = await self._db.execute(
            select(Provider.id).where(Provider.code == self.provider_code)
        )
        provider_id: int | None = result.scalar_one_or_none()
        if provider_id is None:
            raise ScraperError(
                f"Provider with code '{self.provider_code}' not found in database."
            )
        self._provider_id = provider_id
        return provider_id

    async def _update_job_status(
        self,
        job_id: str,
        status: str,
        error: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        retry_count: int | None = None,
    ) -> None:
        """Update ScrapeJob columns in place.

        Only the fields explicitly passed (non-None) are written, so callers
        do not need to know the full row state.

        Args:
            job_id: UUID string of the ScrapeJob.
            status: New status string (``running``, ``completed``, ``failed``).
            error: Error message to store in ``error_message`` (optional).
            started_at: Timestamp to set for ``started_at`` (optional).
            completed_at: Timestamp to set for ``completed_at`` (optional).
            retry_count: Value to set for ``retry_count`` (optional).
        """
        values: dict = {"status": status}
        if error is not None:
            values["error_message"] = error
        if started_at is not None:
            values["started_at"] = started_at
        if completed_at is not None:
            values["completed_at"] = completed_at
        if retry_count is not None:
            values["retry_count"] = retry_count

        await self._db.execute(
            update(ScrapeJob)
            .where(ScrapeJob.id == uuid.UUID(job_id))
            .values(**values)
        )
        await self._db.commit()

    async def _save_results(
        self,
        job_id: str,
        route_id: int,
        provider_id: int,
        results: list[ScrapeResultData],
        route: Route | None = None,
    ) -> None:
        """Persist ScrapeResult rows to the database.

        Runs results through the normalization pipeline before insertion.
        Invalid or duplicate records are silently dropped by the pipeline.

        Args:
            job_id: UUID string of the parent ScrapeJob.
            route_id: Integer FK to the route.
            provider_id: Integer FK to the provider.
            results: List of data transfer objects to persist.
            route: Route ORM instance used by the normalization pipeline for
                context logging. Optional; normalization is skipped when None.
        """
        if route is not None:
            from app.services.normalization import normalization_pipeline
            results = normalization_pipeline.normalize_batch(
                results, self.provider_code, route
            )

        job_uuid = uuid.UUID(job_id)
        orm_rows = [
            ScrapeResult(
                job_id=job_uuid,
                route_id=route_id,
                provider_id=provider_id,
                departure_time=r.departure_time,
                arrival_time=r.arrival_time,
                price_jpy=r.price_jpy,
                seat_type=r.seat_type,
                available_seats=r.available_seats,
                booking_url=r.booking_url,
                pickup_stop=r.pickup_stop,
                dropoff_stop=r.dropoff_stop,
                raw_data=r.raw_data,
            )
            for r in results
        ]
        self._db.add_all(orm_rows)
        await self._db.commit()
