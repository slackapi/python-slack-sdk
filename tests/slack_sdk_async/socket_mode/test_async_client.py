import asyncio
import unittest
from unittest.mock import patch

from slack_sdk.socket_mode.async_client import AsyncBaseSocketModeClient
from tests.slack_sdk_async.helpers import async_test


class _FakeSocketModeClient(AsyncBaseSocketModeClient):
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


class TestAsyncBaseSocketModeClient(unittest.TestCase):
    @async_test
    async def test_cancelled_waiter_does_not_release_another_task_lock(self):
        client = _FakeSocketModeClient()

        holder = asyncio.ensure_future(client.connect_to_new_endpoint(force=True))
        await asyncio.wait_for(client.connect_started.wait(), timeout=5)
        self.assertTrue(
            client.connect_operation_lock.locked(),
            "the holder never acquired the connect lock before entering connect()",
        )

        waiter = asyncio.ensure_future(client.connect_to_new_endpoint())
        await asyncio.sleep(0.1)

        waiter.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await waiter

        self.assertFalse(
            holder.done(),
            "the holder finished before connect() was allowed to complete",
        )
        self.assertTrue(
            client.connect_operation_lock.locked(),
            "the cancelled waiter released a lock it never acquired",
        )

        client.allow_connect_to_finish.set()
        await asyncio.wait_for(holder, timeout=5)
        self.assertFalse(
            client.connect_operation_lock.locked(),
            "the holder did not release the connect lock after connect() finished",
        )

    @async_test
    async def test_reconnect_is_skipped_when_the_lock_cannot_be_acquired(self):
        client = _FakeSocketModeClient()
        # connect() must not block here: on the unpatched client the acquire succeeds and
        # this test has to FAIL rather than hang, since a hanging control cannot be read.
        client.allow_connect_to_finish.set()

        with patch.object(asyncio, "wait_for", side_effect=asyncio.TimeoutError):
            await client.connect_to_new_endpoint()

        self.assertFalse(client.connect_started.is_set(), "reconnected without holding the lock")
        self.assertEqual(client.wss_uri, "wss://example.com/original", "the endpoint was rotated anyway")
        self.assertFalse(client.connect_operation_lock.locked(), "released a lock it never acquired")

    @async_test
    async def test_force_reconnects_even_when_the_lock_cannot_be_acquired(self):
        client = _FakeSocketModeClient()
        # connect() must not block: force drives the reconnect even though the acquire timed out.
        client.allow_connect_to_finish.set()

        with patch.object(asyncio, "wait_for", side_effect=asyncio.TimeoutError):
            await client.connect_to_new_endpoint(force=True)

        self.assertTrue(client.connect_started.is_set(), "force did not reconnect after the acquire timed out")
        self.assertEqual(client.wss_uri, "wss://example.com/new", "force did not rotate the endpoint")
        self.assertFalse(
            client.connect_operation_lock.locked(),
            "held or released a lock it never acquired",
        )

    @async_test
    async def test_reconnect_skipped_when_already_connected(self):
        client = _FakeSocketModeClient()
        client.connected = True
        client.allow_connect_to_finish.set()

        await client.connect_to_new_endpoint()
        self.assertFalse(client.connect_started.is_set(), "reconnected while already connected without force")
        self.assertEqual(client.wss_uri, "wss://example.com/original", "rotated the endpoint without force")
        self.assertFalse(
            client.connect_operation_lock.locked(),
            "the connect lock was not released after skipping the reconnect",
        )

    @async_test
    async def test_force_reconnects_even_when_already_connected(self):
        client = _FakeSocketModeClient()
        client.connected = True
        client.allow_connect_to_finish.set()

        await client.connect_to_new_endpoint(force=True)
        self.assertTrue(client.connect_started.is_set(), "force did not trigger a reconnect")
        self.assertEqual(client.wss_uri, "wss://example.com/new", "force did not rotate the endpoint")
        self.assertFalse(
            client.connect_operation_lock.locked(),
            "the connect lock was not released after a forced reconnect",
        )
