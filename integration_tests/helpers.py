import asyncio
from asyncio.events import AbstractEventLoop


def async_test(coro):
    loop: AbstractEventLoop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        current_loop: AbstractEventLoop = asyncio.get_event_loop()
        return current_loop.run_until_complete(coro(*args, **kwargs))

    return wrapper
