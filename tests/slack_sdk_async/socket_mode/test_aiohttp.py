import asyncio
import logging
import unittest
from unittest.mock import MagicMock

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.slack_sdk_async.helpers import async_test
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async


class TestAiohttp(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server_async(self, MockHandler)
        self.web_client = AsyncWebClient(
            token="xoxb-api_test",
            base_url="http://localhost:8888",
        )

    def tearDown(self):
        cleanup_mock_web_api_server_async(self)

    @async_test
    async def test_init_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_connect_returns_when_closed(self):
        # Regression test for #1913: connect() must not loop forever once the client is closed.
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.wss_uri = "ws://localhost:8888/link"
        await client.close()
        await asyncio.wait_for(client.connect(), timeout=1.0)
        self.assertTrue(client.closed)

    @async_test
    async def test_connect_returns_when_exception_raised_after_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.logger = MagicMock()
        client.logger.level = logging.DEBUG

        async def close_then_raise(*args, **kwargs):
            await client.close()
            raise RuntimeError("Session is closed")

        client.issue_new_wss_url = close_then_raise

        await asyncio.wait_for(client.connect(), timeout=1.0)
        self.assertTrue(client.closed)
        client.logger.exception.assert_not_called()

    @async_test
    async def test_init_with_loop(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            loop=asyncio.get_event_loop(),
        )
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_issue_new_wss_url(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        try:
            url = await client.issue_new_wss_url()
            self.assertTrue(url.startswith("ws://"))
        finally:
            await client.close()

    # TODO: valid test to connect
    # @async_test
    # async def test_connect_to_new_endpoint(self):
    #     client = SocketModeClient(
    #         app_token="xapp-A111-222-xyz",
    #         web_client=self.web_client,
    #         auto_reconnect_enabled=False,
    #     )
    #     try:
    #         await client.connect_to_new_endpoint()
    #     except Exception as e:
    #         pass
    #     finally:
    #         await client.close()

    @async_test
    async def test_enqueue_message(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            trace_enabled=True,
            on_message_listeners=[lambda msg: None],
        )
        client.message_listeners.append(listener)
        try:
            await client.enqueue_message("hello")
            await client.process_message()

            await client.enqueue_message(
                """{"type":"hello","num_connections":1,"debug_info":{"host":"applink-111-222","build_number":10,"approximate_connection_time":18060},"connection_info":{"app_id":"A111"}}"""
            )
            await client.process_message()
        finally:
            await client.disconnect()
            await client.close()


async def listener(self, message, raw_message):
    pass


class _LockProbeClient(SocketModeClient):
    """Just enough state for send_message(), with no real connection."""

    def __init__(self):
        self.connect_operation_lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        self.closed = False
        self.current_session = MagicMock()

    async def is_connected(self) -> bool:
        return True

    @classmethod
    def build_session_id(cls, session) -> str:
        return "test-session"

    async def session_id(self) -> str:
        return "test-session"


class TestAiohttpSendMessageLock(unittest.TestCase):
    @async_test
    async def test_send_message_leaves_another_tasks_lock_alone(self):
        client = _LockProbeClient()

        async def send_str(message):
            raise ConnectionError("the underlying connection was replaced")

        client.current_session.send_str = send_str

        # Stand in for a reconnect holding the lock for the whole call.
        await client.connect_operation_lock.acquire()

        task = asyncio.ensure_future(client.send_message("hello"))
        await asyncio.sleep(0.1)

        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, ConnectionError):
            pass

        self.assertTrue(
            client.connect_operation_lock.locked(),
            "send_message() released the connect lock held by another task",
        )
        client.connect_operation_lock.release()
