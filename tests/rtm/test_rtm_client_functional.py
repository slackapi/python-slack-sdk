import asyncio
import collections
import unittest

from aiohttp import web, WSCloseCode

import slack
import slack.errors as e
from tests.helpers import async_test
from tests.rtm.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestRTMClientFunctional(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        task = asyncio.ensure_future(self.mock_server(), loop=self.loop)
        self.loop.run_until_complete(asyncio.wait_for(task, 0.1))

        self.client = slack.RTMClient(
            token="xoxb-valid",
            base_url="http://localhost:8765",
            auto_reconnect=False,
            run_async=False,
        )
        self.client._web_client = slack.WebClient(
            token="xoxb-valid",
            base_url="http://localhost:8888",
            run_async=False,
        )

    def tearDown(self):
        self.loop.run_until_complete(self.site.stop())
        cleanup_mock_web_api_server(self)
        if self.client:
            # self.client.stop()

            # If you see the following errors with #stop() method calls,  call `RTMClient#async_stop()` instead
            #
            # /python3.8/asyncio/base_events.py:641:
            #   RuntimeWarning: coroutine 'ClientWebSocketResponse.close' was never awaited self._ready.clear()
            #
            self.client._event_loop.run_until_complete(self.client.async_stop())

        slack.RTMClient._callbacks = collections.defaultdict(list)

    # -------------------------------------------

    async def mock_server(self):
        app = web.Application()
        app["websockets"] = []
        app.router.add_get("/", self.websocket_handler)
        app.on_shutdown.append(self.on_shutdown)
        runner = web.AppRunner(app)
        await runner.setup()
        self.site = web.TCPSite(runner, "localhost", 8765)
        await self.site.start()

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        request.app["websockets"].append(ws)
        try:
            async for msg in ws:
                await ws.send_json({"type": "message", "message_sent": msg.json()})
        finally:
            request.app["websockets"].remove(ws)
        return ws

    async def on_shutdown(self, app):
        for ws in set(app["websockets"]):
            await ws.close(code=WSCloseCode.GOING_AWAY, message="Server shutdown")

    # -------------------------------------------

    def test_client_auto_reconnects_if_connection_randomly_closes(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            rtm_client = payload["rtm_client"]

            if rtm_client._connection_attempts == 1:
                rtm_client._close_websocket()
            else:
                self.assertEqual(rtm_client._connection_attempts, 2)
                rtm_client.stop()

        self.client.auto_reconnect = True
        self.client.start()

    def test_client_auto_reconnects_if_an_error_is_thrown(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            rtm_client = payload["rtm_client"]

            if rtm_client._connection_attempts == 1:
                raise e.SlackApiError("Test Error", {"headers": {"Retry-After": 0.001}})
            else:
                self.assertEqual(rtm_client._connection_attempts, 2)
                rtm_client.stop()

        self.client.auto_reconnect = True
        self.client.start()

    def test_open_event_receives_expected_arguments(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertIsInstance(payload["data"], dict)
            self.assertIsInstance(payload["web_client"], slack.WebClient)
            rtm_client = payload["rtm_client"]
            self.assertIsInstance(rtm_client, slack.RTMClient)
            rtm_client.stop()

        self.client.start()

    def test_stop_closes_websocket(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertFalse(self.client._websocket.closed)

            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()
        self.assertIsNone(self.client._websocket)

    def test_start_calls_rtm_connect_by_default(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertFalse(self.client._websocket.closed)
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()

    def test_start_calls_rtm_start_when_specified(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertFalse(self.client._websocket.closed)
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.token = "xoxb-rtm.start"
        self.client.connect_method = "rtm.start"
        self.client.start()

    def test_send_over_websocket_sends_expected_message(self):
        @slack.RTMClient.run_on(event="open")
        def echo_message(**payload):
            rtm_client = payload["rtm_client"]
            message = {
                "id": 1,
                "type": "message",
                "channel": "C024BE91L",
                "text": "Hello world",
            }
            rtm_client.send_over_websocket(payload=message)

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {
                "id": 1,
                "type": "message",
                "channel": "C024BE91L",
                "text": "Hello world",
            }
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_ping_sends_expected_message(self):
        @slack.RTMClient.run_on(event="open")
        async def ping_message(**payload):
            rtm_client = payload["rtm_client"]
            await rtm_client.ping()

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "ping"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_typing_sends_expected_message(self):
        @slack.RTMClient.run_on(event="open")
        async def typing_message(**payload):
            rtm_client = payload["rtm_client"]
            await rtm_client.typing(channel="C01234567")

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "typing", "channel": "C01234567"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_on_error_callbacks(self):
        @slack.RTMClient.run_on(event="open")
        def raise_an_error(**payload):
            raise e.SlackClientNotConnectedError("Testing error handling.")

        self.called = False

        @slack.RTMClient.run_on(event="error")
        def error_callback(**payload):
            self.called = True

        with self.assertRaises(e.SlackClientNotConnectedError):
            self.client.start()
        self.assertTrue(self.called)

    def test_callback_errors_are_raised(self):
        @slack.RTMClient.run_on(event="open")
        def raise_an_error(**payload):
            raise Exception("Testing error handling.")

        with self.assertRaises(Exception) as context:
            self.client.start()

        expected_error = "Testing error handling."
        self.assertIn(expected_error, str(context.exception))

    def test_on_close_callbacks(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            payload["rtm_client"].stop()

        self.called = False

        @slack.RTMClient.run_on(event="close")
        def assert_on_close(**payload):
            self.called = True

        self.client.start()
        self.assertTrue(self.called)

    @async_test
    async def test_run_async_valid(self):
        client = slack.RTMClient(
            token="xoxb-valid",
            base_url="http://localhost:8765",
            run_async=True,
        )
        client._web_client = slack.WebClient(
            token="xoxb-valid",
            base_url="http://localhost:8888",
            run_async=True,
        )
        self.called = False

        @slack.RTMClient.run_on(event="open")
        async def handle_open_event(**payload):
            self.called = True

        client.start()  # intentionally no await here
        await asyncio.sleep(3)
        self.assertTrue(self.called)

    @async_test
    async def test_run_async_invalid(self):
        client = slack.RTMClient(
            token="xoxb-valid",
            base_url="http://localhost:8765",
            run_async=True,
        )
        client._web_client = slack.WebClient(
            token="xoxb-valid",
            base_url="http://localhost:8888",
            run_async=True,
        )
        self.called = False

        @slack.RTMClient.run_on(event="open")
        def handle_open_event(**payload):
            self.called = True

        client.start()  # intentionally no await here
        await asyncio.sleep(3)
        self.assertFalse(self.called)
