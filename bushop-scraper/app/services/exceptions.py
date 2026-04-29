# app/services/exceptions.py


class ScraperError(Exception):
    """Base exception for all scraper failures."""


class ParseError(ScraperError):
    """Raised when scraped HTML/data cannot be parsed into expected structure."""


class NavigationError(ScraperError):
    """Raised when Playwright fails to navigate to the target page."""
