# app/services/circuit_breaker.py
import asyncio
from datetime import UTC, datetime, timedelta


class CircuitBreaker:
    """Per-provider in-memory circuit breaker.

    Opens after :attr:`FAILURE_THRESHOLD` consecutive failures and
    auto-resets after :attr:`RESET_TIMEOUT_MINUTES` minutes.

    State is not persisted — a process restart clears all circuits.
    """

    FAILURE_THRESHOLD: int = 3
    RESET_TIMEOUT_MINUTES: int = 30

    def __init__(self) -> None:
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, datetime] = {}

    def is_open(self, provider_code: str) -> bool:
        """Return True if the circuit is open and the provider should be skipped.

        If the reset timeout has elapsed, the circuit is automatically closed
        before returning False.

        Args:
            provider_code: Unique provider identifier (e.g. ``"willer"``).

        Returns:
            ``True`` when the provider should be skipped, ``False`` otherwise.
        """
        opened = self._opened_at.get(provider_code)
        if opened is None:
            return False

        timeout = timedelta(minutes=self.RESET_TIMEOUT_MINUTES)
        if datetime.now(UTC) - opened >= timeout:
            # Auto-reset after timeout
            self._failures.pop(provider_code, None)
            self._opened_at.pop(provider_code, None)
            return False

        return True

    def record_failure(
        self,
        provider_code: str,
        route_id: int = 0,
        error: str = "",
    ) -> None:
        """Increment failure count and open the circuit if threshold is reached.

        When the circuit transitions to open (failure count first reaches
        :attr:`FAILURE_THRESHOLD`), a webhook alert is fired asynchronously
        via :mod:`app.services.alert_service` if an event loop is running.

        Args:
            provider_code: Unique provider identifier.
            route_id: Route database ID associated with the failure (for alert context).
            error: Last error message (for alert context).
        """
        count = self._failures.get(provider_code, 0) + 1
        self._failures[provider_code] = count
        if count >= self.FAILURE_THRESHOLD and provider_code not in self._opened_at:
            self._opened_at[provider_code] = datetime.now(UTC)
            # Fire-and-forget async alert — import here to avoid circular imports
            from app.services.alert_service import alert_service  # noqa: PLC0415

            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(
                        alert_service.send_scraper_failure_alert(
                            provider_code=provider_code,
                            route_id=route_id,
                            error_message=error,
                            failure_count=count,
                        )
                    )
            except RuntimeError:
                pass  # No event loop available — skip alert in sync context

    def record_success(self, provider_code: str) -> None:
        """Reset failure count and close the circuit on success.

        Args:
            provider_code: Unique provider identifier.
        """
        self._failures.pop(provider_code, None)
        self._opened_at.pop(provider_code, None)


# Module-level singleton — imported directly by other services.
circuit_breaker = CircuitBreaker()
