import asyncio
import inspect
import sys
from asyncio.events import AbstractEventLoop


def async_test(coro):
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        current_loop: AbstractEventLoop = asyncio.get_event_loop()
        return current_loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


def is_not_specified() -> bool:
    # get the caller's filepath
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filepath: str = module.__file__

    # python setup.py run_all_tests --integration-test-target=web/test_issue_560.py
    test_target: str = sys.argv[3]  # e.g., web/test_issue_560.py
    return not test_target or \
           not filepath.endswith(test_target)
