from typing import List, Optional

from aiohttp import ClientResponseError

from slack_sdk.http_retry.builtin_async_handlers import AsyncServerErrorRetryHandler
from slack_sdk.http_retry.builtin_interval_calculators import FixedValueRetryIntervalCalculator
from slack_sdk.http_retry.state import RetryState
from slack_sdk.http_retry.request import HttpRequest
from slack_sdk.http_retry.response import HttpResponse


class ErrorRecordingRetryHandler(AsyncServerErrorRetryHandler):
    def __init__(self):
        super().__init__(max_retry_count=1, interval_calculator=FixedValueRetryIntervalCalculator(0))
        self.can_retry_errors: List[Optional[Exception]] = []
        self.prepare_errors: List[Optional[Exception]] = []

    async def _can_retry_async(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse] = None,
        error: Optional[Exception] = None,
    ) -> bool:
        self.can_retry_errors.append(error)
        return await super()._can_retry_async(state=state, request=request, response=response, error=error)

    async def prepare_for_next_attempt_async(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse] = None,
        error: Optional[Exception] = None,
    ) -> None:
        self.prepare_errors.append(error)
        await super().prepare_for_next_attempt_async(state=state, request=request, response=response, error=error)


def error_statuses(errors: List[Optional[Exception]]) -> List[object]:
    return [error.status if isinstance(error, ClientResponseError) else error for error in errors]
