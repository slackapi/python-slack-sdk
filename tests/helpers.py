import asyncio
import os


def async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        future = coro(*args, **kwargs)
        return asyncio.get_event_loop().run_until_complete(future)

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


def is_ci_unstable_test_skip_enabled() -> bool:
    return os.environ.get("CI_UNSTABLE_TESTS_SKIP_ENABLED") == "1"
