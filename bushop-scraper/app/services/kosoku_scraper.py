# app/services/kosoku_scraper.py
"""Kosoku Bus (高速バスネット) scraper implementation.

Kosoku Bus is a Japanese highway bus aggregator: https://www.kosokubus.com

Search URL pattern:
    https://www.kosokubus.com/search/?dep={dep_name}&arr={arr_name}&date={YYYY-MM-DD}

City names are URL-encoded Japanese strings, e.g. ``dep=東京&arr=大阪``.
"""

import re
from datetime import date, datetime, timedelta, timezone, UTC
from typing import ClassVar
from urllib.parse import urlencode

from playwright.async_api import ElementHandle, Page

from app.models.route import Route
from app.services.base_scraper import BaseScraper, ScrapeResultData
from app.services.exceptions import NavigationError, ParseError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_JST = timezone(timedelta(hours=9))

_BASE_URL = "https://www.kosokubus.com/search/"

_AFFILIATE_PARAMS = "ref=kosoku&utm_source=bushop"

# Selector for the results container — wait for this before querying rows
_RESULTS_CONTAINER_SELECTOR = ".search-result"
_RESULTS_TIMEOUT_MS = 20_000

# Selector for individual result rows inside the container
_ROW_SELECTOR = ".result-row"

# Regex to strip non-digit characters from price/seat-count strings
_NON_DIGIT_RE = re.compile(r"[^\d]")


# ---------------------------------------------------------------------------
# City name mapping
# ---------------------------------------------------------------------------

# Maps BusHop city slug → Kosoku Japanese city name used in URL query params.
_KOSOKU_CITY_NAMES: dict[str, str] = {
    "tokyo": "東京",
    "osaka": "大阪",
    "kyoto": "京都",
    "nagoya": "名古屋",
    "fukuoka": "福岡",
    "sapporo": "札幌",
    "sendai": "仙台",
    "hiroshima": "広島",
    "kobe": "神戸",
    "nara": "奈良",
}


# ---------------------------------------------------------------------------
# KosokuScraper
# ---------------------------------------------------------------------------


class KosokuScraper(BaseScraper):
    """Scraper for Kosoku Bus / 高速バスネット (https://www.kosokubus.com).

    Handles JavaScript-rendered search results using Playwright's
    ``wait_for_selector`` before DOM traversal.

    Example usage::

        scraper = KosokuScraper(db_session)
        results = await scraper.scrape_with_retry(job_id, route, travel_date)
    """

    provider_code: ClassVar[str] = "kosoku"

    # ------------------------------------------------------------------
    # Public abstract method implementation
    # ------------------------------------------------------------------

    async def scrape_route(
        self,
        page: Page,
        route: Route,
        date: date,
    ) -> list[ScrapeResultData]:
        """Scrape Kosoku Bus search results for a given route and date.

        Navigates to the Kosoku search page, waits for results to render,
        then parses each result row into a ``ScrapeResultData`` object.

        Args:
            page: An open Playwright browser page.
            route: Route ORM instance containing origin_id and destination_id.
            date: Travel date.

        Returns:
            List of normalised ScrapeResultData objects.

        Raises:
            NavigationError: If city slugs are unmapped or page navigation fails.
            ParseError: If no results are found or all rows fail to parse.
        """
        url = self._build_search_url(route, date)

        try:
            await page.goto(url, wait_until="domcontentloaded")
            await page.wait_for_selector(
                _RESULTS_CONTAINER_SELECTOR,
                timeout=_RESULTS_TIMEOUT_MS,
            )
        except Exception as exc:
            raise NavigationError(
                f"Failed to load Kosoku results page: {url} — {exc}"
            ) from exc

        rows: list[ElementHandle] = await page.query_selector_all(_ROW_SELECTOR)

        if not rows:
            raise ParseError(
                f"No results found on Kosoku Bus for route "
                f"{route.origin_id} → {route.destination_id} on {date}"
            )

        results: list[ScrapeResultData] = []
        for row in rows:
            try:
                result = await self._parse_result_row(row, date)
                results.append(result)
            except ParseError:
                # Skip malformed rows; raise only if ALL rows fail
                continue

        if not results:
            raise ParseError(
                f"Parsed 0 valid results from {len(rows)} rows for "
                f"{route.origin_id} → {route.destination_id} on {date}"
            )

        return results

    # ------------------------------------------------------------------
    # Helper: URL builder
    # ------------------------------------------------------------------

    def _build_search_url(self, route: Route, travel_date: date) -> str:
        """Build the Kosoku Bus search URL for a route and date.

        Kosoku uses Japanese city name strings (URL-encoded) as query
        parameters: ``?dep=東京&arr=大阪&date=2024-06-01``.

        Args:
            route: Route with ``origin_id`` and ``destination_id`` slugs.
            travel_date: Travel date.

        Returns:
            Full search URL string.

        Raises:
            NavigationError: If either city slug has no mapping.
        """
        dep_name = self._map_city_name(route.origin_id)
        arr_name = self._map_city_name(route.destination_id)
        date_str = travel_date.strftime("%Y-%m-%d")
        params = urlencode({"dep": dep_name, "arr": arr_name, "date": date_str})
        return f"{_BASE_URL}?{params}"

    # ------------------------------------------------------------------
    # Helper: city name mapper
    # ------------------------------------------------------------------

    def _map_city_name(self, city_id: str) -> str:
        """Map a BusHop city slug to a Kosoku Japanese city name string.

        Args:
            city_id: BusHop city slug, e.g. ``"tokyo"``.

        Returns:
            Japanese city name string, e.g. ``"東京"``.

        Raises:
            NavigationError: If the city slug has no mapping.
        """
        name = _KOSOKU_CITY_NAMES.get(city_id.lower())
        if name is None:
            raise NavigationError(
                f"City '{city_id}' is not mapped to a Kosoku city name. "
                f"Available cities: {sorted(_KOSOKU_CITY_NAMES)}"
            )
        return name

    # ------------------------------------------------------------------
    # Helper: result row parser
    # ------------------------------------------------------------------

    async def _parse_result_row(
        self,
        row: ElementHandle,
        travel_date: date,
    ) -> ScrapeResultData:
        """Parse a single Kosoku result row element into ScrapeResultData.

        Expected DOM structure of ``.result-row``:
        - ``.dep-time``    — departure time text, e.g. ``"08:30"``
        - ``.arr-time``    — arrival time text, e.g. ``"23:00"``
        - ``.fare``        — price text, e.g. ``"¥4,500"`` or ``"4500円"``
        - ``.seat-type``   — seat class label, e.g. ``"通常シート"`` (optional)
        - ``.seat-count``  — remaining seats, e.g. ``"残5席"`` (optional)
        - ``.dep-stop``    — departure stop name (optional)
        - ``.arr-stop``    — arrival stop name (optional)
        - ``a.book-btn`` or ``a[href]`` — booking anchor

        All times from Kosoku are JST (UTC+9); stored as UTC-aware datetimes.

        Args:
            row: Playwright ElementHandle for a single result row.
            travel_date: Travel date used to construct full datetimes.

        Returns:
            Populated ScrapeResultData.

        Raises:
            ParseError: If required fields (dep time, arr time, price) are missing.
        """
        # --- Departure time ---
        dep_el = await row.query_selector(".dep-time")
        if dep_el is None:
            raise ParseError("Missing departure time element (.dep-time) in result row")
        dep_time_text: str = (await dep_el.inner_text()).strip()

        # --- Arrival time ---
        arr_el = await row.query_selector(".arr-time")
        if arr_el is None:
            raise ParseError("Missing arrival time element (.arr-time) in result row")
        arr_time_text: str = (await arr_el.inner_text()).strip()

        # --- Price ---
        fare_el = await row.query_selector(".fare")
        if fare_el is None:
            raise ParseError("Missing price element (.fare) in result row")
        price_text: str = (await fare_el.inner_text()).strip()

        # --- Parse and convert times to UTC ---
        departure_time = self._parse_jst_datetime(travel_date, dep_time_text)
        arrival_time = self._parse_jst_datetime(travel_date, arr_time_text)

        # Overnight service: arrival is the next day if arr <= dep
        if arrival_time <= departure_time:
            arrival_time += timedelta(days=1)

        # --- Parse price ---
        price_jpy = self._parse_price(price_text)

        # --- Seat type (optional) ---
        seat_type: str | None = None
        seat_type_el = await row.query_selector(".seat-type")
        if seat_type_el is not None:
            seat_type = (await seat_type_el.inner_text()).strip() or None

        # --- Available seats (optional) ---
        available_seats: int | None = None
        seat_count_el = await row.query_selector(".seat-count")
        if seat_count_el is not None:
            seat_count_text = (await seat_count_el.inner_text()).strip()
            # Kosoku typically shows "残N席" (N remaining) or a number
            digits = _NON_DIGIT_RE.sub("", seat_count_text)
            if digits:
                available_seats = int(digits)

        # --- Pickup stop (optional) ---
        pickup_stop: dict | None = None
        dep_stop_el = await row.query_selector(".dep-stop")
        if dep_stop_el is not None:
            stop_name = (await dep_stop_el.inner_text()).strip()
            if stop_name:
                pickup_stop = {"ja": stop_name}

        # --- Dropoff stop (optional) ---
        dropoff_stop: dict | None = None
        arr_stop_el = await row.query_selector(".arr-stop")
        if arr_stop_el is not None:
            stop_name = (await arr_stop_el.inner_text()).strip()
            if stop_name:
                dropoff_stop = {"ja": stop_name}

        # --- Booking URL ---
        booking_url = await self._extract_booking_url(row)

        # --- Raw data for debugging ---
        raw_text: str = (await row.inner_text()).strip()
        raw_data = {"raw_text": raw_text}

        return ScrapeResultData(
            departure_time=departure_time,
            arrival_time=arrival_time,
            price_jpy=price_jpy,
            seat_type=seat_type,
            available_seats=available_seats,
            booking_url=booking_url,
            pickup_stop=pickup_stop,
            dropoff_stop=dropoff_stop,
            raw_data=raw_data,
        )

    # ------------------------------------------------------------------
    # Private utilities
    # ------------------------------------------------------------------

    def _parse_jst_datetime(self, travel_date: date, time_str: str) -> datetime:
        """Parse an HH:MM time string on a given date into a UTC-aware datetime.

        Times from Kosoku are JST (UTC+9). The result is converted to UTC.

        Args:
            travel_date: Calendar date for the service.
            time_str: Time as ``"HH:MM"`` or ``"HH時MM分"`` (Japanese format).

        Returns:
            UTC-aware datetime.

        Raises:
            ParseError: If the time string cannot be parsed.
        """
        # Normalise Japanese time format "HH時MM分" → "HH:MM"
        normalised = re.sub(r"時", ":", time_str)
        normalised = re.sub(r"分.*", "", normalised).strip()

        try:
            hour, minute = (int(part) for part in normalised.split(":"))
        except (ValueError, AttributeError) as exc:
            raise ParseError(
                f"Cannot parse time string: {time_str!r}"
            ) from exc

        jst_dt = datetime(
            travel_date.year,
            travel_date.month,
            travel_date.day,
            hour,
            minute,
            tzinfo=_JST,
        )
        return jst_dt.astimezone(UTC)

    def _parse_price(self, price_text: str) -> int:
        """Strip currency symbols and commas, return integer yen amount.

        Args:
            price_text: Raw price string, e.g. ``"¥4,500"`` or ``"4500円"``.

        Returns:
            Price in JPY as integer.

        Raises:
            ParseError: If no digits are found in the price string.
        """
        digits = _NON_DIGIT_RE.sub("", price_text)
        if not digits:
            raise ParseError(f"Cannot parse price from: {price_text!r}")
        return int(digits)

    async def _extract_booking_url(self, row: ElementHandle) -> str:
        """Extract the booking URL from a result row and append affiliate params.

        Tries selectors in order:
        1. ``a.book-btn``
        2. ``a.reserve-btn``
        3. First ``a[href]`` element in the row

        Falls back to the Kosoku homepage if no anchor is found.

        Args:
            row: Playwright ElementHandle for a single result row.

        Returns:
            Absolute booking URL with affiliate query params appended.
        """
        href: str | None = None

        for selector in ("a.book-btn", "a.reserve-btn", "a[href]"):
            link_el = await row.query_selector(selector)
            if link_el is not None:
                href = await link_el.get_attribute("href")
                if href:
                    break

        if not href:
            href = "https://www.kosokubus.com"

        # Make absolute if relative
        if href.startswith("/"):
            href = f"https://www.kosokubus.com{href}"
        elif not href.startswith("http"):
            href = f"https://www.kosokubus.com/{href}"

        # Append affiliate params
        separator = "&" if "?" in href else "?"
        return f"{href}{separator}{_AFFILIATE_PARAMS}"
