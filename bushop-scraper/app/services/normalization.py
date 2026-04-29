# app/services/normalization.py
"""Data normalization pipeline for BusHop scraper results.

Validates and standardizes :class:`~app.services.base_scraper.ScrapeResultData`
objects from any provider into a unified schema ready for DB insertion.
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.models.route import Route
from app.services.base_scraper import ScrapeResultData

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_JST = timezone(timedelta(hours=9))
_UTC = timezone.utc

_MAX_PRICE_JPY: int = 100_000

_PROVIDER_BASE_URLS: dict[str, str] = {
    "willer": "https://travel.willer.co.jp",
    "kosoku": "https://www.kosokubus.com",
}

_AFFILIATE_REF_KEY = "ref"
_AFFILIATE_UTM_KEY = "utm_source"
_AFFILIATE_UTM_VALUE = "bushop"

_NON_DIGIT_RE = re.compile(r"[^\d]")

_STOP_LANG_KEYS = ("vi", "en", "ja")


# ---------------------------------------------------------------------------
# NormalizationPipeline
# ---------------------------------------------------------------------------


class NormalizationPipeline:
    """Validates and normalizes ScrapeResultData from any provider.

    Runs a sequence of normalization steps:

    1. Validate required fields
    2. Normalize price (ensure positive integer, sanity cap)
    3. Normalize times (ensure UTC-aware datetimes)
    4. Normalize booking_url (absolute URL + affiliate params)
    5. Normalize stop dicts (ensure vi/en/ja keys)
    6. Deduplicate (same departure_time + price_jpy within batch)
    """

    def normalize_batch(
        self,
        results: list[ScrapeResultData],
        provider_code: str,
        route: Route,
    ) -> list[ScrapeResultData]:
        """Normalize a batch of results, dropping invalid records silently.

        Each item passes through the normalization chain in order. Records that
        fail validation at any step are logged and excluded from the output.
        Survivors are deduplicated before being returned.

        Args:
            results: Raw list of ScrapeResultData from a provider scraper.
            provider_code: Provider identifier string (e.g. ``"willer"``).
            route: Route ORM instance for context (logged on drop).

        Returns:
            Cleaned and deduplicated list of ScrapeResultData.
        """
        cleaned: list[ScrapeResultData] = []

        for item in results:
            try:
                if not self._validate(item):
                    logger.warning(
                        "Dropping invalid result [provider=%s route=%s]: %s",
                        provider_code,
                        route.id,
                        item,
                    )
                    continue

                item = self._normalize_price(item)
                if item is None:
                    logger.warning(
                        "Dropping result with invalid price [provider=%s route=%s]",
                        provider_code,
                        route.id,
                    )
                    continue

                item = self._normalize_times(item)
                item = self._normalize_booking_url(item, provider_code)
                item = self._normalize_stops(item)

                cleaned.append(item)

            except Exception:
                logger.exception(
                    "Unexpected error normalizing result [provider=%s route=%s]",
                    provider_code,
                    route.id,
                )

        return self._deduplicate(cleaned)

    # ------------------------------------------------------------------
    # Step 1 — Validation
    # ------------------------------------------------------------------

    def _validate(self, item: ScrapeResultData) -> bool:
        """Return False if the record is structurally invalid and should be dropped.

        Required conditions:
        - ``departure_time`` is not None
        - ``arrival_time`` is not None
        - ``price_jpy`` is a positive integer
        - ``booking_url`` is a non-empty string

        Args:
            item: ScrapeResultData to inspect.

        Returns:
            ``True`` if the record is valid, ``False`` otherwise.
        """
        if item.departure_time is None:
            return False
        if item.arrival_time is None:
            return False
        if not isinstance(item.price_jpy, int) or item.price_jpy <= 0:
            return False
        if not item.booking_url or not item.booking_url.strip():
            return False
        return True

    # ------------------------------------------------------------------
    # Step 2 — Price normalization
    # ------------------------------------------------------------------

    def _normalize_price(self, item: ScrapeResultData) -> ScrapeResultData | None:
        """Ensure price_jpy is a positive integer within the sanity cap.

        If price_jpy is somehow stored as a string-like value (e.g. ``"¥5,000"``),
        strip non-digit characters and convert. Returns ``None`` if the resulting
        value is <= 0 or >= ``_MAX_PRICE_JPY``.

        Args:
            item: ScrapeResultData to normalize.

        Returns:
            Updated ScrapeResultData, or ``None`` if price is out of range.
        """
        price = item.price_jpy

        # Guard: Pydantic coerces int fields, but handle string edge case
        if not isinstance(price, int):
            digits = _NON_DIGIT_RE.sub("", str(price))
            if not digits:
                return None
            price = int(digits)

        if price <= 0 or price >= _MAX_PRICE_JPY:
            return None

        if price == item.price_jpy:
            return item
        return item.model_copy(update={"price_jpy": price})

    # ------------------------------------------------------------------
    # Step 3 — Time normalization
    # ------------------------------------------------------------------

    def _normalize_times(self, item: ScrapeResultData) -> ScrapeResultData:
        """Ensure departure_time and arrival_time are UTC-aware datetimes.

        Naive datetimes (no tzinfo) are assumed to be JST (UTC+9) and converted
        to UTC. Already UTC-aware datetimes pass through unchanged.

        Args:
            item: ScrapeResultData to normalize.

        Returns:
            ScrapeResultData with UTC-aware departure_time and arrival_time.
        """
        dep = _to_utc(item.departure_time)
        arr = _to_utc(item.arrival_time)

        if dep is item.departure_time and arr is item.arrival_time:
            return item
        return item.model_copy(update={"departure_time": dep, "arrival_time": arr})

    # ------------------------------------------------------------------
    # Step 4 — Booking URL normalization
    # ------------------------------------------------------------------

    def _normalize_booking_url(
        self,
        item: ScrapeResultData,
        provider_code: str,
    ) -> ScrapeResultData:
        """Ensure booking_url is absolute and carries affiliate query params.

        - Relative paths (starting with ``/``) are resolved against the known
          provider base URL.
        - ``?ref={provider_code}&utm_source=bushop`` is appended if not already
          present.

        Args:
            item: ScrapeResultData to normalize.
            provider_code: Used both as a base-URL lookup key and as the
                ``ref`` param value.

        Returns:
            ScrapeResultData with an absolute, affiliate-tagged booking_url.
        """
        url = item.booking_url.strip()
        base = _PROVIDER_BASE_URLS.get(provider_code, "")

        # Make absolute
        if url.startswith("/"):
            url = f"{base}{url}"
        elif not url.startswith("http"):
            url = f"{base}/{url}"

        # Append affiliate params if missing
        parsed = urlparse(url)
        qs = parse_qs(parsed.query, keep_blank_values=True)

        changed = False
        if _AFFILIATE_REF_KEY not in qs:
            qs[_AFFILIATE_REF_KEY] = [provider_code]
            changed = True
        if _AFFILIATE_UTM_KEY not in qs:
            qs[_AFFILIATE_UTM_KEY] = [_AFFILIATE_UTM_VALUE]
            changed = True

        if changed or url != item.booking_url:
            new_query = urlencode(qs, doseq=True)
            url = urlunparse(parsed._replace(query=new_query))
            return item.model_copy(update={"booking_url": url})

        return item

    # ------------------------------------------------------------------
    # Step 5 — Stop dict normalization
    # ------------------------------------------------------------------

    def _normalize_stop(self, stop: dict | None) -> dict | None:
        """Ensure a stop dict has ``vi``, ``en``, and ``ja`` keys.

        Rules:
        - ``None`` → returned as-is.
        - Dict with only ``"ja"`` → ``"en"`` and ``"vi"`` filled with same value.
        - Any other missing key among ``vi / en / ja`` → filled with ``""``.

        Args:
            stop: Raw stop dict or None.

        Returns:
            Normalized stop dict or None.
        """
        if stop is None:
            return None

        present = {k: stop[k] for k in _STOP_LANG_KEYS if k in stop}
        missing_keys = [k for k in _STOP_LANG_KEYS if k not in stop]

        if not missing_keys:
            return stop  # already complete

        # If only "ja" key is present, propagate its value to the others
        if list(present.keys()) == ["ja"]:
            ja_value = present["ja"]
            return {"vi": ja_value, "en": ja_value, "ja": ja_value}

        # Fill any missing keys with empty string
        normalized = dict(stop)
        for key in missing_keys:
            normalized[key] = ""
        return normalized

    def _normalize_stops(self, item: ScrapeResultData) -> ScrapeResultData:
        """Apply _normalize_stop to both pickup_stop and dropoff_stop.

        Args:
            item: ScrapeResultData to normalize.

        Returns:
            ScrapeResultData with normalized stop dicts.
        """
        pickup = self._normalize_stop(item.pickup_stop)
        dropoff = self._normalize_stop(item.dropoff_stop)

        if pickup is item.pickup_stop and dropoff is item.dropoff_stop:
            return item
        return item.model_copy(update={"pickup_stop": pickup, "dropoff_stop": dropoff})

    # ------------------------------------------------------------------
    # Step 6 — Deduplication
    # ------------------------------------------------------------------

    def _deduplicate(self, results: list[ScrapeResultData]) -> list[ScrapeResultData]:
        """Remove duplicate records within the batch.

        Two records are considered duplicates when they share the same
        ``(departure_time, price_jpy)`` pair. The first occurrence is kept.

        Args:
            results: List of already-normalized ScrapeResultData.

        Returns:
            Deduplicated list preserving original order.
        """
        seen: set[tuple[datetime, int]] = set()
        unique: list[ScrapeResultData] = []

        for item in results:
            key = (item.departure_time, item.price_jpy)
            if key not in seen:
                seen.add(key)
                unique.append(item)
            else:
                logger.debug(
                    "Dropping duplicate result: departure_time=%s price_jpy=%s",
                    item.departure_time,
                    item.price_jpy,
                )

        return unique


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _to_utc(dt: datetime) -> datetime:
    """Convert a datetime to UTC-aware, assuming JST if naive.

    Args:
        dt: Input datetime, possibly naive.

    Returns:
        UTC-aware datetime.
    """
    if dt.tzinfo is None:
        # Assume JST
        return dt.replace(tzinfo=_JST).astimezone(_UTC)
    return dt.astimezone(_UTC)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

normalization_pipeline = NormalizationPipeline()
