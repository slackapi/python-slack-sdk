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


def mock_req_args(data=None, params={}, json=None):
    req_args = {
        "headers": {
            "user-agent": slack.WebClient._get_user_agent(),
            "Authorization": "Bearer None",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
        "files": None,
        "data": data,
        "params": params,
        "json": json,
    }
    return req_args


class TestRTMClient(unittest.TestCase):
    def setUp(self):
        self.client = slack.RTMClient(auto_reconnect=False)

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

    def test_on_accepts_a_list_of_callbacks(self):
        def say_on(**payload):
            pass

        def say_off(**payload):
            pass

        self.client.on(event="message", callback=[say_on, say_off])
        self.assertEqual(len(self.client._callbacks["message"]), 2)

    def test_on_raises_when_not_callable(self):
        invalid_callback = "a"

        with self.assertRaises(e.SlackClientError) as context:
            self.client.on(event="message", callback=invalid_callback)

        expected_error = "The specified callback 'a' is not callable."
        error = str(context.exception)
        self.assertIn(expected_error, error)

    def test_on_raises_when_kwargs_not_accepted(self):
        def invalid_cb():
            pass

        with self.assertRaises(e.SlackClientError) as context:
            self.client.on(event="message", callback=invalid_cb)

        expected_error = (
            "The callback 'invalid_cb' must accept keyword arguments (**kwargs)."
        )
        error = str(context.exception)
        self.assertIn(expected_error, error)

    def test_send_over_websocket_raises_when_not_connected(self):
        with self.assertRaises(e.SlackClientError) as context:
            self.client.send_over_websocket({})

        expected_error = "Websocket connection is closed."
        error = str(context.exception)
        self.assertIn(expected_error, error)

    @mock.patch("slack.WebClient._send", return_value=({"ok": True}, {}, 200))
    def test_start_raises_an_error_if_rtm_ws_url_is_not_returned(self, mock_send):
        with self.assertRaises(e.SlackApiError) as context:
            slack.RTMClient(auto_reconnect=False).start()

        expected_error = "Unable to retreive RTM URL from Slack"
        self.assertIn(expected_error, str(context.exception))


# It waits and reconnects when an exception is thrown if auto_reconnect is specified. via @mock.patch('', side_effect=mock_side_effect)
# Test that it uses the Retry-After if passed.
# We likely should mock out asyncio.sleep.

# the stop method is called when these signals are triggered. (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
# Mock out self._websocket.close() and ensure it gets called when the signal is killed.

# Test when sending messages over the websocket it autoincrements the message id. e.g. _next_msg_id


@mock.patch(
    "slack.WebClient._send",
    return_value=(
        {
            "ok": True,
            "url": "ws://localhost:8765",
            "self": {"id": "U01234ABC", "name": "robotoverlord"},
            "team": {
                "domain": "exampledomain",
                "id": "T123450FP",
                "name": "ExampleName",
            },
        },
        {"header": "fake"},
        200,
    ),
)
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

        self.client = slack.RTMClient(loop=self.loop, auto_reconnect=False)

    def tearDown(self):
        self.stop.set_result(None)
        slack.RTMClient._callbacks = collections.defaultdict(list)

    def test_open_event_receives_expected_arguments(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertIsInstance(payload["data"], dict)
            self.assertIsInstance(payload["web_client"], slack.WebClient)
            rtm_client = payload["rtm_client"]
            self.assertIsInstance(rtm_client, slack.RTMClient)
            rtm_client.stop()

        self.client.start()

    def test_stop_closes_websocket(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertEqual(
                self.client._websocket.state, websockets.protocol.State.OPEN
            )
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()
        self.assertIsNone(self.client._websocket)

    def test_start_calls_rtm_connect_by_default(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertEqual(
                self.client._websocket.state, websockets.protocol.State.OPEN
            )
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()
        mock_send.assert_called_once_with(
            http_verb="GET",
            api_url="https://www.slack.com/api/rtm.connect",
            req_args=mock_req_args(),
        )

    def test_start_calls_rtm_start_when_specified(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertEqual(
                self.client._websocket.state, websockets.protocol.State.OPEN
            )
            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.connect_method = "rtm.start"
        self.client.start()
        mock_send.assert_called_once_with(
            http_verb="GET",
            api_url="https://www.slack.com/api/rtm.start",
            req_args=mock_req_args(),
        )

    def test_send_over_websocket_sends_expected_message(self, mock_send):
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

    def test_ping_sends_expected_message(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def ping_message(**payload):
            rtm_client = payload["rtm_client"]
            rtm_client.ping()

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "ping"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_typing_sends_expected_message(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def typing_message(**payload):
            rtm_client = payload["rtm_client"]
            rtm_client.typing(channel="C01234567")

        @slack.RTMClient.run_on(event="message")
        def check_message(**payload):
            message = {"id": 1, "type": "typing", "channel": "C01234567"}
            rtm_client = payload["rtm_client"]
            self.assertDictEqual(payload["data"]["message_sent"], message)
            rtm_client.stop()

        self.client.start()

    def test_on_error_callbacks(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def raise_an_error(**payload):
            raise e.SlackClientNotConnectedError("Testing error handling.")

        @slack.RTMClient.run_on(event="error")
        def error_callback(**payload):
            self.error_hanlding_mock(str(payload["data"]))

        self.error_hanlding_mock = mock.Mock()
        with self.assertRaises(e.CallbackError):
            self.client.start()
        self.error_hanlding_mock.assert_called_once()

    def test_callback_errors_are_raised(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def raise_an_error(**payload):
            raise Exception("Testing error handling.")

        with self.assertRaises(Exception) as context:
            self.client.start()

        expected_error = (
            "When calling '#raise_an_error()' in the 'test_client' module the"
            " following error was raised: Testing error handling."
        )
        self.assertIn(expected_error, str(context.exception))

