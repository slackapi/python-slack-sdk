import asyncio
import logging
import unittest
from unittest.mock import MagicMock

from websockets.exceptions import WebSocketException

from slack_sdk.socket_mode.websockets import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async
from tests.slack_sdk_async.helpers import async_test


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
        client = SocketModeClient(app_token="xapp-A111-222-xyz")
        try:
            self.assertIsNotNone(client)
        finally:
            await client.close()

    @async_test
    async def test_issue_new_wss_url(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        try:
            url = await client.issue_new_wss_url()
            self.assertTrue(url.startswith("ws://"))
        finally:
            await client.close()

    @async_test
    async def test_connect_to_new_endpoint(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
        )
        try:
            await client.connect_to_new_endpoint()
        except Exception as e:
            # TODO: valida test to connect
            pass
        finally:
            await client.close()

    @async_test
    async def test_enqueue_message(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
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
            await client.close()


async def listener(message, raw_message):
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


class TestWebsocketsSendMessageLock(unittest.TestCase):
    @async_test
    async def test_send_message_leaves_another_tasks_lock_alone(self):
        client = _LockProbeClient()

        async def send(message):
            raise WebSocketException("the underlying connection was replaced")

        client.current_session.send = send

        # Stand in for a reconnect holding the lock for the whole call.
        await client.connect_operation_lock.acquire()

        task = asyncio.ensure_future(client.send_message("hello"))
        await asyncio.sleep(0.1)

        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, WebSocketException):
            pass

        self.assertTrue(
            client.connect_operation_lock.locked(),
            "send_message() released the connect lock held by another task",
        )
        client.connect_operation_lock.release()
