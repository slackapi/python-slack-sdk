import asyncio
import unittest
from unittest.mock import patch

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from tests.slack_sdk_async.helpers import async_test


class _FakeClient(AsyncBaseSocketModeClient):
    """Minimal concrete client: connect() blocks until released, like a real reconnect."""

    def __init__(self):
        self.connect_operation_lock = asyncio.Lock()
        self.trace_enabled = False
        self.wss_uri = "wss://example.com/original"
        self.connected = False
        self.connect_started = asyncio.Event()
        self.allow_connect_to_finish = asyncio.Event()

    async def is_connected(self) -> bool:
        return self.connected

    async def issue_new_wss_url(self) -> str:
        return "wss://example.com/new"

    async def connect(self):
        self.connect_started.set()
        await self.allow_connect_to_finish.wait()

    async def disconnect(self):
        pass

    async def session_id(self) -> str:
        return "test-session"


class TestAsyncClientConnectLock(unittest.TestCase):
    @async_test
    async def test_cancelled_waiter_does_not_release_another_task_lock(self):
        """A cancelled waiter must not release the reconnect that is still in progress.

        `connect()` cancels `message_receiver` and `current_session_monitor` on every
        successful reconnection, and both of those tasks call `connect_to_new_endpoint()`.
        So a task can be cancelled while it is suspended inside
        `connect_operation_lock.acquire()`. `asyncio.Lock` has no concept of ownership, so
        releasing on `locked()` alone lets that cancelled task free a lock it never held,
        which drops mutual exclusion around the reconnect.
        """
        client = _FakeClient()

        holder = asyncio.ensure_future(client.connect_to_new_endpoint(force=True))
        await asyncio.wait_for(client.connect_started.wait(), timeout=5)
        self.assertTrue(client.connect_operation_lock.locked())

        waiter = asyncio.ensure_future(client.connect_to_new_endpoint(force=True))
        await asyncio.sleep(0.1)

        waiter.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await waiter

        # The holder is still inside connect(), so the lock must still be held.
        self.assertFalse(holder.done())
        self.assertTrue(
            client.connect_operation_lock.locked(),
            "the cancelled waiter released a lock it never acquired",
        )

        client.allow_connect_to_finish.set()
        await asyncio.wait_for(holder, timeout=5)
        self.assertFalse(client.connect_operation_lock.locked())

    @async_test
    async def test_reconnect_is_skipped_when_the_lock_cannot_be_acquired(self):
        """Mirrors the sync client: acquire is bounded, and a failed acquire skips the work.

        The sync client calls acquire(blocking=True, timeout=5) and gates the reconnect on
        `acquired`, so a caller that never gets the lock does not reconnect and does not
        release a lock it does not hold.
        """
        client = _FakeClient()
        # connect() must not block here: on the unpatched client the acquire succeeds and
        # this test has to FAIL rather than hang, since a hanging control cannot be read.
        client.allow_connect_to_finish.set()

        with patch("asyncio.wait_for", side_effect=asyncio.TimeoutError):
            await client.connect_to_new_endpoint()

        self.assertFalse(client.connect_started.is_set(), "reconnected without holding the lock")
        self.assertEqual(client.wss_uri, "wss://example.com/original", "the endpoint was rotated anyway")
        self.assertFalse(client.connect_operation_lock.locked(), "released a lock it never acquired")
