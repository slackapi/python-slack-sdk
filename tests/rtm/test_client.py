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


class TestConnectedRTMClient(unittest.TestCase):
    async def echo(self, ws, path):
        async for message in ws:
            await ws.send(
                json.dumps({"type": "message", "message_sent": json.loads(message)})
            )

    def setUp(self):
        asyncio.ensure_future(websockets.serve(self.echo, "localhost", 8765))
        self.client = slack.RTMClient()
        mock_retreive_websocket_info = mock.MagicMock(name="_retreive_websocket_info")
        mock_retreive_websocket_info.return_value = "ws://localhost:8765", {}
        self.client._retreive_websocket_info = mock_retreive_websocket_info

    def tearDown(self):
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

    def test_send_over_websocket(self):
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
