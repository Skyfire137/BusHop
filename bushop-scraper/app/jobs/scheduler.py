# app/jobs/scheduler.py
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.models.route import Route
from app.models.scrape_job import ScrapeJob
from app.services.circuit_breaker import circuit_breaker
from app.services.kosoku_scraper import KosokuScraper
from app.services.willer_scraper import WillerScraper

logger = get_logger(__name__)

# Maps provider_code -> scraper class
_SCRAPERS = {
    "willer": WillerScraper,
    "kosoku": KosokuScraper,
}

scheduler = AsyncIOScheduler(timezone="UTC")


async def pre_scrape_popular_routes() -> None:
    """Scrape all popular routes for today + next 3 days, all providers.

    Runs as an APScheduler job at 21:00, 04:00, and 11:00 UTC
    (06:00, 13:00, 20:00 JST).

    - Creates a ScrapeJob record per (route, date, provider) combination.
    - Skips providers whose circuit breaker is open.
    - Errors on individual jobs are caught so one failure does not halt others.
    """
    run_start = datetime.now(UTC)
    logger.info(
        "pre_scrape_popular_routes started",
        extra={"status": "started"},
    )

    today = date.today()
    dates = [today + timedelta(days=i) for i in range(4)]

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Route).where(Route.is_popular.is_(True))
        )
        popular_routes: list[Route] = list(result.scalars().all())

    if not popular_routes:
        logger.info("No popular routes found, skipping pre-scrape")
        return

    total = len(popular_routes) * len(dates) * len(_SCRAPERS)
    completed = 0
    failed = 0

    for route in popular_routes:
        for travel_date in dates:
            for provider_code, scraper_cls in _SCRAPERS.items():
                if circuit_breaker.is_open(provider_code):
                    logger.info(
                        "Circuit open, skipping provider",
                        extra={"provider": provider_code, "route_id": route.id},
                    )
                    continue

                job_id: str | None = None
                try:
                    async with AsyncSessionLocal() as db:
                        job = ScrapeJob(
                            route_id=route.id,
                            status="pending",
                            triggered_by="scheduler",
                        )
                        db.add(job)
                        await db.flush()  # populate job.id from server default
                        await db.refresh(job)
                        job_id = str(job.id)
                        await db.commit()

                    async with AsyncSessionLocal() as db:
                        scraper = scraper_cls(db)
                        await scraper.scrape_with_retry(
                            job_id=job_id,
                            route=route,
                            date=travel_date,
                        )

                    circuit_breaker.record_success(provider_code)
                    completed += 1
                    logger.info(
                        "Scrape completed",
                        extra={
                            "job_id": job_id,
                            "provider": provider_code,
                            "route_id": route.id,
                            "status": "completed",
                        },
                    )

                except Exception as exc:
                    circuit_breaker.record_failure(
                        provider_code, route_id=route.id, error=str(exc)
                    )
                    failed += 1
                    logger.error(
                        "Scrape failed",
                        extra={
                            "job_id": job_id,
                            "provider": provider_code,
                            "route_id": route.id,
                            "error": str(exc),
                            "status": "failed",
                        },
                    )

    duration_ms = int((datetime.now(UTC) - run_start).total_seconds() * 1000)
    logger.info(
        "pre_scrape_popular_routes finished",
        extra={
            "status": "finished",
            "duration_ms": duration_ms,
        },
    )
    logger.info(
        f"Pre-scrape summary: total={total}, completed={completed}, failed={failed}"
    )


def start_scheduler() -> None:
    """Register jobs and start the APScheduler instance.

    Call this once during application startup.
    """
    # 06:00 JST = 21:00 UTC (previous day, but cron wraps midnight correctly)
    # 13:00 JST = 04:00 UTC
    # 20:00 JST = 11:00 UTC
    scheduler.add_job(
        pre_scrape_popular_routes,
        CronTrigger(hour=21, minute=0, timezone="UTC"),
        id="pre_scrape_0600jst",
        replace_existing=True,
    )
    scheduler.add_job(
        pre_scrape_popular_routes,
        CronTrigger(hour=4, minute=0, timezone="UTC"),
        id="pre_scrape_1300jst",
        replace_existing=True,
    )
    scheduler.add_job(
        pre_scrape_popular_routes,
        CronTrigger(hour=11, minute=0, timezone="UTC"),
        id="pre_scrape_2000jst",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started with 3 daily pre-scrape jobs")


def stop_scheduler() -> None:
    """Gracefully shut down the scheduler.

    Call this during application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
