"""Circuit breaker pattern for resilience against external service failures"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Failing, reject requests
    HALF_OPEN = "half_open"    # Testing recovery


class CircuitBreaker:
    """Circuit breaker for protecting against cascading failures"""

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
    ):
        """Initialize circuit breaker

        Args:
            name: Name of the circuit (for logging)
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        logger.info(f"Circuit breaker '{name}' initialized")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection

        Args:
            func: Async function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: Original exception or circuit breaker exception
        """
        # Check state transitions
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"[{self.name}] Circuit entering HALF_OPEN state")
            else:
                time_until_retry = self._time_until_retry()
                raise Exception(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Retry after {time_until_retry}s"
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Called when request succeeds"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info(f"[{self.name}] Circuit CLOSED - service recovered")

    def _on_failure(self):
        """Called when request fails"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        logger.warning(
            f"[{self.name}] Failure {self.failure_count}/{self.failure_threshold}"
        )

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"[{self.name}] Circuit OPEN - too many failures, "
                f"rejecting requests for {self.recovery_timeout}s"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try recovery"""
        return (
            self.last_failure_time is not None
            and datetime.now() - self.last_failure_time
            > timedelta(seconds=self.recovery_timeout)
        )

    def _time_until_retry(self) -> int:
        """Seconds until circuit breaker resets"""
        if self.last_failure_time is None:
            return 0
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, int(self.recovery_timeout - elapsed))

    def reset(self):
        """Manually reset circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        logger.info(f"[{self.name}] Circuit manually reset")
