import random
import time
from http.client import RemoteDisconnected
from typing import Optional, List

from slack_sdk.http_retry.interval_calculator import RetryIntervalCalculator
from slack_sdk.http_retry.state import RetryState
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse
from slack_sdk.http_retry.handler import RetryHandler, default_interval_calculator


class ConnectionErrorRetryHandler(RetryHandler):
    """RetryHandler that does retries for connectivity issues."""

    def __init__(
        self,
        max_retry_count: int = 1,
        interval_calculator: RetryIntervalCalculator = default_interval_calculator,
        error_types: List[Exception] = [ConnectionResetError, RemoteDisconnected],
    ):
        super().__init__(max_retry_count, interval_calculator)
        self.error_types_to_do_retries = error_types

    def can_retry_custom(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse],
        error: Optional[Exception],
    ) -> bool:
        if error is None:
            return False

        for error_type in self.error_types_to_do_retries:
            if isinstance(error, error_type):
                return True
        return False


class ServerErrorRetryHandler(RetryHandler):
    """RetryHandler that does retries for server-side errors."""

    def can_retry_custom(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse],
        error: Optional[Exception],
    ) -> bool:
        return response is not None and response.status_code >= 500


class RateLimitErrorRetryHandler(RetryHandler):
    """RetryHandler that does retries for rate limited errors."""

    def can_retry_custom(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse],
        error: Optional[Exception],
    ) -> bool:
        if response.status_code == 429:
            return True

    def prepare_for_next_retry(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse],
        error: Optional[Exception],
    ) -> None:
        if response is None:
            raise error

        state.increment_current_attempt()
        retry_after_header_name: Optional[str] = None
        for k in response.headers.keys():
            if k.lower() == "retry-after":
                retry_after_header_name = k
                break
        duration = 1
        if retry_after_header_name is None:
            # This situation usually does not arise. Just in case.
            duration += random.random()
        else:
            duration = (
                int(response.headers.get(retry_after_header_name)[0]) + random.random()
            )
        time.sleep(duration)
