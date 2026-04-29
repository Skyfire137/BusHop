# app/services/willer_scraper.py
"""Willer Express scraper implementation.

Willer search URL pattern:
    https://travel.willer.co.jp/tour/bus/?dep={dep_code}&arr={arr_code}&date={YYYYMMDD}
"""

import re
from datetime import date, datetime, timedelta, timezone, UTC
from typing import ClassVar

from playwright.async_api import ElementHandle, Page

from app.models.route import Route
from app.services.base_scraper import BaseScraper, ScrapeResultData
from app.services.exceptions import NavigationError, ParseError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_JST = timezone(timedelta(hours=9))

_BASE_URL = "https://travel.willer.co.jp/tour/bus/"

_AFFILIATE_PARAMS = "ref=willer&utm_source=bushop"

# Milliseconds to wait for JS-rendered result list
_RESULTS_SELECTOR = ".result-list__item"
_RESULTS_TIMEOUT_MS = 20_000

# Regex to strip non-digit characters from price strings (e.g. "¥4,500" → 4500)
_PRICE_RE = re.compile(r"[^\d]")


# ---------------------------------------------------------------------------
# City code mapping
# ---------------------------------------------------------------------------

# Maps BusHop city slug → Willer numeric code used in dep/arr query params.
# Source: Willer Express city code reference (observed from their search URLs).
_WILLER_CITY_CODES: dict[str, str] = {
    "tokyo": "08",
    "osaka": "27",
    "kyoto": "26",
    "nagoya": "23",
    "fukuoka": "40",
    "sapporo": "01",
    "sendai": "04",
    "hiroshima": "34",
    "kobe": "28",
    "nara": "29",
}


# ---------------------------------------------------------------------------
# WillerScraper
# ---------------------------------------------------------------------------


class WillerScraper(BaseScraper):
    """Scraper for Willer Express (https://travel.willer.co.jp).

    Handles JavaScript-rendered search results using Playwright's
    ``wait_for_selector`` before DOM traversal.
    """

    provider_code: ClassVar[str] = "willer"

    # ------------------------------------------------------------------
    # Public abstract method implementation
    # ------------------------------------------------------------------

    async def scrape_route(
        self,
        page: Page,
        route: Route,
        date: date,
    ) -> list[ScrapeResultData]:
        """Scrape Willer Express search results for a given route and date.

        Args:
            page: An open Playwright browser page.
            route: Route ORM instance containing origin_id and destination_id.
            date: Travel date.

        Returns:
            List of normalised ScrapeResultData objects.

        Raises:
            NavigationError: If city codes are not mapped or page navigation fails.
            ParseError: If no results are found or DOM parsing fails.
        """
        url = self._build_search_url(route, date)

        try:
            await page.goto(url, wait_until="domcontentloaded")
            # Willer uses JS rendering — wait for result cards to appear
            await page.wait_for_selector(
                _RESULTS_SELECTOR,
                timeout=_RESULTS_TIMEOUT_MS,
            )
        except Exception as exc:
            raise NavigationError(
                f"Failed to load Willer results page: {url} — {exc}"
            ) from exc

        cards: list[ElementHandle] = await page.query_selector_all(_RESULTS_SELECTOR)

        if not cards:
            raise ParseError(
                f"No results found on Willer for route "
                f"{route.origin_id} → {route.destination_id} on {date}"
            )

        results: list[ScrapeResultData] = []
        for card in cards:
            try:
                result = await self._parse_result_card(card, url)
                results.append(result)
            except ParseError:
                # Skip cards that cannot be parsed; raise only if ALL fail
                continue

        if not results:
            raise ParseError(
                f"Parsed 0 valid results from {len(cards)} cards for "
                f"{route.origin_id} → {route.destination_id} on {date}"
            )

        return results

    # ------------------------------------------------------------------
    # Helper: URL builder
    # ------------------------------------------------------------------

    def _build_search_url(self, route: Route, travel_date: date) -> str:
        """Build the Willer Express search URL for a route and date.

        Args:
            route: Route with origin_id and destination_id slugs.
            travel_date: Travel date.

        Returns:
            Full search URL string.

        Raises:
            NavigationError: If either city slug is not in the mapping.
        """
        dep_code = self._map_city_code(route.origin_id)
        arr_code = self._map_city_code(route.destination_id)
        date_str = travel_date.strftime("%Y%m%d")
        return f"{_BASE_URL}?dep={dep_code}&arr={arr_code}&date={date_str}"

    # ------------------------------------------------------------------
    # Helper: city code mapper
    # ------------------------------------------------------------------

    def _map_city_code(self, city_id: str) -> str:
        """Map a BusHop city slug to a Willer Express city code.

        Args:
            city_id: BusHop city slug, e.g. ``"tokyo"``.

        Returns:
            Willer numeric city code string.

        Raises:
            NavigationError: If the city slug has no mapping.
        """
        code = _WILLER_CITY_CODES.get(city_id.lower())
        if code is None:
            raise NavigationError(
                f"City '{city_id}' is not mapped to a Willer city code. "
                f"Available cities: {sorted(_WILLER_CITY_CODES)}"
            )
        return code

    # ------------------------------------------------------------------
    # Helper: result card parser
    # ------------------------------------------------------------------

    async def _parse_result_card(
        self,
        card: ElementHandle,
        page_url: str,
    ) -> ScrapeResultData:
        """Parse a single Willer result card element into ScrapeResultData.

        Expected DOM structure of ``.result-list__item``:
        - ``.bus-time__dep`` — departure time text, e.g. "08:30"
        - ``.bus-time__arr`` — arrival time text, e.g. "23:00"
        - ``.price__amount`` — price text, e.g. "¥4,500"
        - ``.seat-type__name`` — seat class label, e.g. "Standard"
        - ``.seat-availability`` — seat count text, e.g. "残5席" (optional)
        - ``.stops__dep`` — departure stop name (optional)
        - ``.stops__arr`` — arrival stop name (optional)
        - ``.result-list__item a.booking-btn`` or ``a[href]`` — booking link
        - ``[data-dep-date]`` — date attribute on the card, e.g. "20240601"

        All times from Willer are JST (UTC+9); stored as UTC-aware datetimes.

        Args:
            card: Playwright ElementHandle for a single result card.
            page_url: The search page URL, used to resolve relative booking links.

        Returns:
            Populated ScrapeResultData.

        Raises:
            ParseError: If required fields (dep time, arr time, price) are missing.
        """
        # --- Departure date (from data attribute or inferred from page URL) ---
        dep_date_attr: str | None = await card.get_attribute("data-dep-date")
        if dep_date_attr is None:
            # Fall back: extract date from the search URL (?date=YYYYMMDD)
            m = re.search(r"date=(\d{8})", page_url)
            dep_date_attr = m.group(1) if m else None

        # --- Departure time ---
        dep_el = await card.query_selector(".bus-time__dep")
        if dep_el is None:
            raise ParseError("Missing departure time element in result card")
        dep_time_text: str = (await dep_el.inner_text()).strip()

        # --- Arrival time ---
        arr_el = await card.query_selector(".bus-time__arr")
        if arr_el is None:
            raise ParseError("Missing arrival time element in result card")
        arr_time_text: str = (await arr_el.inner_text()).strip()

        # --- Price ---
        price_el = await card.query_selector(".price__amount")
        if price_el is None:
            raise ParseError("Missing price element in result card")
        price_text: str = (await price_el.inner_text()).strip()

        # --- Parse and convert times ---
        departure_time = self._parse_jst_datetime(dep_date_attr, dep_time_text)
        arrival_time = self._parse_jst_datetime(dep_date_attr, arr_time_text)

        # Arrival may be the next day if arr_time < dep_time
        if arrival_time <= departure_time:
            arrival_time += timedelta(days=1)

        # --- Parse price ---
        price_jpy = self._parse_price(price_text)

        # --- Seat type (optional) ---
        seat_type: str | None = None
        seat_el = await card.query_selector(".seat-type__name")
        if seat_el is not None:
            seat_type = (await seat_el.inner_text()).strip() or None

        # --- Available seats (optional) ---
        available_seats: int | None = None
        avail_el = await card.query_selector(".seat-availability")
        if avail_el is not None:
            avail_text = (await avail_el.inner_text()).strip()
            # Willer shows "残N席" (N seats remaining) or "○" (available) / "×" (full)
            digits = _PRICE_RE.sub("", avail_text)
            if digits:
                available_seats = int(digits)

        # --- Pickup / dropoff stops (optional) ---
        pickup_stop: dict | None = None
        dep_stop_el = await card.query_selector(".stops__dep")
        if dep_stop_el is not None:
            stop_name = (await dep_stop_el.inner_text()).strip()
            if stop_name:
                pickup_stop = {"ja": stop_name}

        dropoff_stop: dict | None = None
        arr_stop_el = await card.query_selector(".stops__arr")
        if arr_stop_el is not None:
            stop_name = (await arr_stop_el.inner_text()).strip()
            if stop_name:
                dropoff_stop = {"ja": stop_name}

        # --- Booking URL ---
        booking_url = await self._extract_booking_url(card, page_url)

        # --- Raw data for debugging ---
        raw_text: str = (await card.inner_text()).strip()
        raw_data = {"raw_text": raw_text, "page_url": page_url}

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

    def _parse_jst_datetime(self, date_str: str | None, time_str: str) -> datetime:
        """Parse a date string and HH:MM time string into a UTC-aware datetime.

        Willer times are in JST (UTC+9). The result is converted to UTC.

        Args:
            date_str: Date as ``"YYYYMMDD"`` or ``None`` (uses today in JST).
            time_str: Time as ``"HH:MM"`` or ``"HH時MM分"`` (Japanese format).

        Returns:
            UTC-aware datetime.

        Raises:
            ParseError: If the time string cannot be parsed.
        """
        # Normalise Japanese time format to HH:MM
        time_str = re.sub(r"時", ":", time_str)
        time_str = re.sub(r"分.*", "", time_str).strip()

        try:
            hour, minute = (int(p) for p in time_str.split(":"))
        except (ValueError, AttributeError) as exc:
            raise ParseError(f"Cannot parse time string: {time_str!r}") from exc

        if date_str:
            try:
                travel_date = datetime.strptime(date_str, "%Y%m%d").date()
            except ValueError as exc:
                raise ParseError(f"Cannot parse date string: {date_str!r}") from exc
        else:
            travel_date = datetime.now(_JST).date()

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
        digits = _PRICE_RE.sub("", price_text)
        if not digits:
            raise ParseError(f"Cannot parse price from: {price_text!r}")
        return int(digits)

    async def _extract_booking_url(
        self,
        card: ElementHandle,
        page_url: str,
    ) -> str:
        """Extract the booking URL from a result card and append affiliate params.

        Tries selectors in order:
        1. ``a.booking-btn``
        2. ``a.reserve-btn``
        3. First ``a[href]`` element in the card

        Args:
            card: Playwright ElementHandle for the result card.
            page_url: Search page URL, used as fallback if no anchor found.

        Returns:
            Absolute booking URL with affiliate query params appended.
        """
        href: str | None = None

        for selector in ("a.booking-btn", "a.reserve-btn", "a[href]"):
            link_el = await card.query_selector(selector)
            if link_el is not None:
                href = await link_el.get_attribute("href")
                if href:
                    break

        if not href:
            # Fall back to the search URL itself so we always return something bookable
            href = page_url

        # Make absolute if relative
        if href.startswith("/"):
            href = f"https://travel.willer.co.jp{href}"
        elif not href.startswith("http"):
            href = f"https://travel.willer.co.jp/{href}"

        # Append affiliate params
        separator = "&" if "?" in href else "?"
        return f"{href}{separator}{_AFFILIATE_PARAMS}"
