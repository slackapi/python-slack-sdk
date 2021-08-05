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

default_retry_handlers = [  # noqa
    connect_error_retry_handler,  # noqa
]  # noqa

all_builtin_retry_handlers = [  # noqa
    connect_error_retry_handler,  # noqa
    rate_limit_error_retry_handler,  # noqa
]  # noqa
