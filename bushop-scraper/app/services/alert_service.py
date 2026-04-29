# app/services/alert_service.py
from datetime import UTC, datetime

import httpx

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_WEBHOOK_TIMEOUT_SECONDS = 5


class AlertService:
    """Sends webhook alerts when scraper encounters critical failures.

    Supports Slack webhook format (POST JSON with "text" field).
    Generic webhooks that accept the same payload are also supported.

    Alert delivery is best-effort: failures are logged but never raised.
    """

    async def send_scraper_failure_alert(
        self,
        provider_code: str,
        route_id: int,
        error_message: str,
        failure_count: int,
    ) -> bool:
        """Send alert if ALERT_WEBHOOK_URL is configured.

        Args:
            provider_code: Provider identifier (e.g. ``"willer"``).
            route_id: Database ID of the route that failed.
            error_message: Last exception message.
            failure_count: Number of consecutive failures recorded.

        Returns:
            ``True`` if the webhook was sent successfully, ``False`` otherwise.
            Does NOT raise — alert failure must never crash the scraper.
        """
        if not settings.alert_webhook_url:
            logger.debug(
                "ALERT_WEBHOOK_URL not configured, skipping alert",
                extra={"provider": provider_code, "route_id": route_id},
            )
            return False

        text = self._format_message(provider_code, route_id, error_message, failure_count)
        return await self._send_webhook({"text": text})

    async def _send_webhook(self, payload: dict) -> bool:
        """POST payload to ALERT_WEBHOOK_URL.

        Args:
            payload: JSON-serialisable dict to POST.

        Returns:
            ``True`` on HTTP 2xx, ``False`` on any error.
        """
        url: str = settings.alert_webhook_url  # type: ignore[assignment]  # guarded by caller
        try:
            async with httpx.AsyncClient(timeout=_WEBHOOK_TIMEOUT_SECONDS) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            logger.info(
                "Alert webhook sent",
                extra={"status": "sent", "http_status": response.status_code},
            )
            return True
        except httpx.TimeoutException:
            logger.warning(
                "Alert webhook timed out",
                extra={"url": url},
            )
            return False
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Alert webhook failed",
                extra={"url": url, "error": str(exc)},
            )
            return False

    def _format_message(
        self,
        provider_code: str,
        route_id: int,
        error_message: str,
        failure_count: int,
    ) -> str:
        """Format a human-readable alert message.

        Args:
            provider_code: Provider identifier.
            route_id: Route database ID.
            error_message: Last exception message.
            failure_count: Consecutive failure count.

        Returns:
            Formatted alert string.
        """
        timestamp = datetime.now(UTC).isoformat()
        return (
            f"[BusHop Alert] Scraper '{provider_code}' failed {failure_count} consecutive times"
            f" on route_id={route_id}.\n"
            f"Last error: {error_message}\n"
            f"Timestamp: {timestamp}"
        )


# Module-level singleton
alert_service = AlertService()
