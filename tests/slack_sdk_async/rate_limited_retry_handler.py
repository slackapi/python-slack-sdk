from typing import Optional

from slack_sdk.http_retry.async_handler import AsyncRetryHandler
from slack_sdk.http_retry.builtin_interval_calculators import FixedValueRetryIntervalCalculator
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse
from slack_sdk.http_retry.state import RetryState


class RateLimitedRetryHandler(AsyncRetryHandler):
    def __init__(self, max_retry_count: int):
        super().__init__(max_retry_count, FixedValueRetryIntervalCalculator(0))
        self.retry_count = 0

    async def _can_retry_async(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse] = None,
        error: Optional[Exception] = None,
    ) -> bool:
        return response is not None and response.status_code == 429

    async def prepare_for_next_attempt_async(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse] = None,
        error: Optional[Exception] = None,
    ) -> None:
        self.retry_count += 1
        await super().prepare_for_next_attempt_async(state=state, request=request, response=response, error=error)
