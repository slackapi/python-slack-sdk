import asyncio
import os


def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        future = coro(*args, **kwargs)
        return loop.run_until_complete(future)

    return wrapper


def remove_os_env_temporarily() -> dict:
    old_env = os.environ.copy()
    os.environ.clear()
    for key, value in old_env.items():
        if key.startswith("PYTHON_SLACK_SDK_"):
            os.environ[key] = value
    return old_env


def restore_os_env(old_env: dict) -> None:
    os.environ.update(old_env)
