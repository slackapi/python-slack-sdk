import asyncio
import time
import unittest

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.web.async_client import AsyncWebClient
from tests.slack_sdk.socket_mode.mock_web_api_handler import MockHandler
from tests.slack_sdk_async.helpers import async_test
from tests.mock_web_api_server import setup_mock_web_api_server_async, cleanup_mock_web_api_server_async


class ControlledClientSession:
    def __init__(self):
        self.closed = False
        self.attempts = 0
        self.attempt_started = asyncio.Event()
        self.closed_event = asyncio.Event()

    async def ws_connect(self, *args, **kwargs):
        self.attempts += 1
        self.attempt_started.set()
        await self.closed_event.wait()
        raise RuntimeError("Session is closed")

    async def close(self):
        self.closed = True
        self.closed_event.set()


class CompletingClientSession:
    def __init__(self):
        self.closed = False
        self.attempts = 0
        self.attempt_started = asyncio.Event()
        self.closed_event = asyncio.Event()
        self.websocket = ConnectedWebSocket()

    async def ws_connect(self, *args, **kwargs):
        self.attempts += 1
        self.attempt_started.set()
        await self.closed_event.wait()
        return self.websocket

    async def close(self):
        self.closed = True
        self.closed_event.set()


class ConnectedWebSocket:
    def __init__(self):
        self.closed = False
        self.receive_forever = asyncio.Event()

    async def close(self):
        self.closed = True

    async def ping(self, data):
        pass

    async def receive(self):
        await self.receive_forever.wait()


class RetryingClientSession:
    def __init__(self):
        self.closed = False
        self.attempt_times = []
        self.websocket = ConnectedWebSocket()

    async def ws_connect(self, *args, **kwargs):
        self.attempt_times.append(time.monotonic())
        if len(self.attempt_times) == 1:
            raise ConnectionError("temporary failure")
        return self.websocket

    async def close(self):
        self.closed = True


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
    async def test_connect_returns_when_client_is_already_closed(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        client.wss_uri = "ws://127.0.0.1:1/link"

        await client.close()
        await asyncio.wait_for(client.connect(), timeout=0.05)

        self.assertTrue(client.closed)
        self.assertTrue(client.aiohttp_client_session.closed)

    @async_test
    async def test_connect_stops_when_close_lands_during_an_attempt(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        await client.aiohttp_client_session.close()
        controlled_session = ControlledClientSession()
        client.aiohttp_client_session = controlled_session
        client.wss_uri = "ws://127.0.0.1:1/link"

        connect_task = asyncio.create_task(client.connect())
        await controlled_session.attempt_started.wait()
        await client.close()

        await asyncio.wait_for(asyncio.shield(connect_task), timeout=0.05)
        self.assertTrue(connect_task.done())
        self.assertEqual(1, controlled_session.attempts)
        self.assertTrue(controlled_session.closed)

    @async_test
    async def test_connect_discards_session_completed_after_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.01,
        )
        await client.aiohttp_client_session.close()
        completing_session = CompletingClientSession()
        client.aiohttp_client_session = completing_session
        client.wss_uri = "ws://127.0.0.1:1/link"

        connect_task = asyncio.create_task(client.connect())
        await completing_session.attempt_started.wait()
        await client.close()
        await asyncio.wait_for(connect_task, timeout=0.05)

        self.assertTrue(completing_session.websocket.closed)
        self.assertIsNone(client.current_session)
        self.assertIsNone(client.current_session_monitor)
        self.assertIsNone(client.message_receiver)

    @async_test
    async def test_connect_preserves_ping_interval_backoff_for_live_client(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
            ping_interval=0.03,
        )
        await client.aiohttp_client_session.close()
        retrying_session = RetryingClientSession()
        client.aiohttp_client_session = retrying_session
        client.wss_uri = "ws://127.0.0.1:1/link"

        try:
            await client.connect()
            self.assertEqual(2, len(retrying_session.attempt_times))
            self.assertGreaterEqual(
                retrying_session.attempt_times[1] - retrying_session.attempt_times[0],
                client.ping_interval,
            )
        finally:
            await client.close()

    @async_test
    async def test_close_awaits_owned_task_settlement_before_session_close(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        client.message_processor.cancel()
        await asyncio.gather(client.message_processor, return_exceptions=True)
        await client.aiohttp_client_session.close()
        controlled_session = ControlledClientSession()
        client.aiohttp_client_session = controlled_session

        started = [asyncio.Event() for _ in range(3)]
        cancelling = [asyncio.Event() for _ in range(3)]
        release_cleanup = asyncio.Event()

        async def owned_task(index):
            started[index].set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                cancelling[index].set()
                await release_cleanup.wait()
                raise

        owned_tasks = [asyncio.create_task(owned_task(index)) for index in range(3)]
        client.message_processor, client.current_session_monitor, client.message_receiver = owned_tasks
        for event in started:
            await event.wait()

        close_task = asyncio.create_task(client.close())
        for event in cancelling:
            await event.wait()

        self.assertFalse(close_task.done())
        self.assertFalse(controlled_session.closed)

        release_cleanup.set()
        await asyncio.wait_for(close_task, timeout=0.05)

        self.assertTrue(controlled_session.closed)
        self.assertTrue(all(task.done() for task in owned_tasks))
        self.assertTrue(all(task.cancelled() for task in owned_tasks))

    @async_test
    async def test_close_does_not_cancel_or_await_current_reconnect_owner(self):
        client = SocketModeClient(
            app_token="xapp-A111-222-xyz",
            web_client=self.web_client,
            auto_reconnect_enabled=False,
        )
        client.message_processor.cancel()
        await asyncio.gather(client.message_processor, return_exceptions=True)
        await client.aiohttp_client_session.close()
        controlled_session = ControlledClientSession()
        client.aiohttp_client_session = controlled_session

        async def settled_task():
            pass

        settled = asyncio.create_task(settled_task())
        await settled
        client.message_processor = settled
        client.message_receiver = settled

        async def reconnect_owner():
            client.current_session_monitor = asyncio.current_task()
            await client.close()

        owner_task = asyncio.create_task(reconnect_owner())
        await asyncio.wait_for(asyncio.shield(owner_task), timeout=0.05)

        self.assertTrue(owner_task.done())
        self.assertFalse(owner_task.cancelled())
        self.assertTrue(controlled_session.closed)

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
