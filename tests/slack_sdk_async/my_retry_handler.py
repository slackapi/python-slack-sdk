from typing import Optional
from aiohttp import ServerDisconnectedError, ClientOSError

from slack_sdk.http_retry.async_handler import AsyncRetryHandler
from slack_sdk.http_retry.interval_calculator import RetryIntervalCalculator
from slack_sdk.http_retry.state import RetryState
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse
from slack_sdk.http_retry.handler import default_interval_calculator


class MyRetryHandler(AsyncRetryHandler):
    def __init__(
        self,
        max_retry_count: int = 1,
        interval_calculator: RetryIntervalCalculator = default_interval_calculator,
    ):
        super().__init__(max_retry_count, interval_calculator)
        self.call_count = 0

    async def _can_retry_async(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse],
        error: Optional[Exception],
    ) -> bool:
        self.call_count += 1
        if error is None:
            return False
        for error_type in [ServerDisconnectedError, ClientOSError]:
            if isinstance(error, error_type):
                return True
        return False
