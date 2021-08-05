from typing import Optional, List

from aiohttp import ServerDisconnectedError, ServerConnectionError, ClientOSError

from slack_sdk.http_retry.interval_calculator import RetryIntervalCalculator
from slack_sdk.http_retry.state import RetryState
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse
from slack_sdk.http_retry.handler import RetryHandler, default_interval_calculator


class AsyncConnectionErrorRetryHandler(RetryHandler):
    """RetryHandler that does retries for connectivity issues."""

    def __init__(
        self,
        max_retry_count: int = 1,
        interval_calculator: RetryIntervalCalculator = default_interval_calculator,
        error_types: List[Exception] = [
            ServerConnectionError,
            ServerDisconnectedError,
            # ClientOSError: [Errno 104] Connection reset by peer
            ClientOSError,
        ],
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


async_default_handlers = [AsyncConnectionErrorRetryHandler()]
