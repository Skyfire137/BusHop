# app/services/cache_service.py
from datetime import UTC, date, datetime, timedelta
from enum import Enum

from sqlalchemy import cast, delete, func, select, update
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scrape_result import ScrapeResult


class CacheStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    MISSING = "missing"


class CacheService:
    """Manages cache freshness checks and invalidation for scrape results.

    Uses PostgreSQL as the cache layer. No Redis.

    TTL rules:
    - FRESH: most recent ``scraped_at`` < 6 hours ago
    - STALE: most recent ``scraped_at`` between 6 and 24 hours ago
    - MISSING: no non-stale rows, or most recent ``scraped_at`` > 24 hours ago
    """

    FRESH_TTL_HOURS: int = 6
    STALE_HOURS: int = 24

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_cached_results(
        self,
        route_id: int,
        travel_date: date,
    ) -> tuple[list[ScrapeResult], CacheStatus]:
        """Return cached results and their freshness status.

        Args:
            route_id: FK to the route.
            travel_date: The departure date to look up.

        Returns:
            A tuple of (results, status) where status is one of
            :attr:`CacheStatus.FRESH`, :attr:`CacheStatus.STALE`, or
            :attr:`CacheStatus.MISSING`.
        """
        stmt = select(ScrapeResult).where(
            ScrapeResult.route_id == route_id,
            cast(ScrapeResult.departure_time, DATE) == travel_date,
            ScrapeResult.is_stale.is_(False),
        )
        rows = (await self._db.execute(stmt)).scalars().all()

        if not rows:
            return [], CacheStatus.MISSING

        most_recent_scraped_at: datetime = max(r.scraped_at for r in rows)
        # Ensure timezone-aware comparison
        if most_recent_scraped_at.tzinfo is None:
            most_recent_scraped_at = most_recent_scraped_at.replace(tzinfo=UTC)

        now = datetime.now(UTC)
        age = now - most_recent_scraped_at

        if age <= timedelta(hours=self.FRESH_TTL_HOURS):
            return list(rows), CacheStatus.FRESH
        if age <= timedelta(hours=self.STALE_HOURS):
            return list(rows), CacheStatus.STALE
        return [], CacheStatus.MISSING

    async def mark_stale(self, route_id: int) -> int:
        """Mark all results for a route older than 24 hours as stale.

        Args:
            route_id: FK to the route.

        Returns:
            Number of rows updated.
        """
        cutoff = datetime.now(UTC) - timedelta(hours=self.STALE_HOURS)
        result = await self._db.execute(
            update(ScrapeResult)
            .where(
                ScrapeResult.route_id == route_id,
                ScrapeResult.scraped_at < cutoff,
                ScrapeResult.is_stale.is_(False),
            )
            .values(is_stale=True)
        )
        await self._db.commit()
        return result.rowcount  # type: ignore[return-value]

    async def invalidate(self, route_id: int, travel_date: date) -> None:
        """Delete cached results for a route+date combination.

        Called before a fresh scrape so stale rows do not pollute results.

        Args:
            route_id: FK to the route.
            travel_date: The departure date whose rows should be removed.
        """
        await self._db.execute(
            delete(ScrapeResult).where(
                ScrapeResult.route_id == route_id,
                cast(ScrapeResult.departure_time, DATE) == travel_date,
            )
        )
        await self._db.commit()
