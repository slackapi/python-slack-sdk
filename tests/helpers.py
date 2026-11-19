import asyncio
import copy
import os
import sys
from typing import Any


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


def create_copy(original: Any) -> Any:
    if sys.version_info.major == 3 and sys.version_info.minor <= 6:
        # NOTE: Unfortunately, copy.deepcopy doesn't work in Python 3.6.5.
        # --------------------
        # >     rv = reductor(4)
        # E     TypeError: can't pickle _thread.RLock objects
        # ../../.pyenv/versions/3.6.10/lib/python3.6/copy.py:169: TypeError
        # --------------------
        # As a workaround, this operation uses shallow copies in Python 3.6.
        # If your code modifies the shared data in threads / async functions, race conditions may arise.
        # Please consider upgrading Python major version to 3.7+ if you encounter some issues due to this.
        return copy.copy(original)
    else:
        return copy.deepcopy(original)
