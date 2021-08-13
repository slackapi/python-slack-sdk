from typing import List

from .handler import RetryHandler  # noqa
from .builtin_handlers import (
    ConnectionErrorRetryHandler,  # noqa
    RateLimitErrorRetryHandler,  # noqa
)  # noqa
from .interval_calculator import RetryIntervalCalculator  # noqa
from .builtin_interval_calculators import (  # noqa
    FixedValueRetryIntervalCalculator,  # noqa
    BackoffRetryIntervalCalculator,  # noqa
)  # noqa
from .jitter import Jitter  # noqa
from .request import HttpRequest  # noqa
from .response import HttpResponse  # noqa
from .state import RetryState  # noqa

connect_error_retry_handler = ConnectionErrorRetryHandler()  # noqa
rate_limit_error_retry_handler = RateLimitErrorRetryHandler()  # noqa


def default_retry_handlers() -> List[RetryHandler]:
    return [connect_error_retry_handler]


def all_builtin_retry_handlers() -> List[RetryHandler]:
    return [
        connect_error_retry_handler,
        rate_limit_error_retry_handler,
    ]
