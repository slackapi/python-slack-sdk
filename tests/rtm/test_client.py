# Standard Imports
import collections
import unittest
from unittest import mock

# ThirdParty Imports
import asyncio
import websockets
import json

# Internal Imports
import slack
import slack.errors as e


class TestRTMClient(unittest.TestCase):
    def setUp(self):
        self.client = slack.RTMClient()

    def tearDown(self):
        slack.RTMClient._callbacks = collections.defaultdict(list)

    def test_run_on_annotation_sets_callbacks(self):
        @slack.RTMClient.run_on(event="message")
        def say_run_on(**payload):
            pass

        self.assertTrue(self.client._callbacks["message"][0].__name__ == "say_run_on")

    def test_on_sets_callbacks(self):
        def say_on(**payload):
            pass

        self.client.on(event="message", callback=say_on)
        self.assertTrue(self.client._callbacks["message"][0].__name__ == "say_on")

    def test_on_raises_when_not_callable(self):
        invalid_callback = "a"

        with self.assertRaises(e.SlackClientError) as context:
            self.client.on(event="message", callback=invalid_callback)

        expected_error = "The specified callback 'a' is not callable."
        error = str(context.exception)
        self.assertEqual(error, expected_error)

    def test_on_raises_when_kwargs_not_accepted(self):
        def invalid_cb():
            pass

        with self.assertRaises(e.SlackClientError) as context:
            self.client.on(event="message", callback=invalid_cb)

        expected_error = (
            "The callback 'invalid_cb' must accept keyword arguments (**kwargs)."
        )
        error = str(context.exception)
        self.assertEqual(error, expected_error)

    def test_send_over_websocket_raises_when_not_connected(self):
        with self.assertRaises(e.SlackClientError) as context:
            self.client.send_over_websocket({})

        expected_error = "Websocket connection is closed."
        error = str(context.exception)
        self.assertEqual(error, expected_error)


class TestConnectedRTMClient(unittest.TestCase):
    async def echo(self, ws, path):
        async for message in ws:
            await ws.send(
                json.dumps({"type": "message", "message_sent": json.loads(message)})
            )

    async def mock_server(self):
        async with websockets.serve(self.echo, "localhost", 8765):
            await self.stop

    def setUp(self):
        self.loop = asyncio.get_event_loop()
        self.stop = self.loop.create_future()
        task = asyncio.ensure_future(self.mock_server())
        self.loop.run_until_complete(asyncio.wait([task], timeout=0.1))

        self.client = slack.RTMClient(loop=self.loop)
        mock_retreive_websocket_info = mock.MagicMock(name="_retreive_websocket_info")
        mock_retreive_websocket_info.return_value = "ws://localhost:8765", {}
        self.client._retreive_websocket_info = mock_retreive_websocket_info

    def tearDown(self):
        self.stop.set_result(None)
        slack.RTMClient._callbacks = collections.defaultdict(list)

    def test_stop_closes_websocket(self):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertEqual(
                self.client._websocket.state, websockets.protocol.State.OPEN
            )
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()
        self.assertIsNone(self.client._websocket)

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
            rtm_client.send_over_websocket(message)

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
        def echo_message(**payload):
            rtm_client = payload["rtm_client"]
            rtm_client.ping()

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "ping"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_typing_sends_expected_message(self):
        @slack.RTMClient.run_on(event="open")
        def echo_message(**payload):
            rtm_client = payload["rtm_client"]
            rtm_client.typing(channel="C01234567")

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "typing", "channel": "C01234567"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()


# when start is called...

# It retreives the URL from the correct Start Method.

# it raises SlackApiError if url isn't included response from RTM connect method and auto_reconnect is false.

# Test that an open event is dispatched once connected. It should include RTM payload, web and rtm client.  self._dispatch_event(event='open', data=data)

# Test that message events are dispatched. It should include the message payload, web and rtm client. self._dispatch_event(event, data=payload)

# It waits and reconnects when an exception is thrown if auto_reconnect is specified.

# the stop method is called when these signals are triggered. (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

# Test that a close event is dispatched once everything is torn down. i.e. self._dispatch_event(event='close')
