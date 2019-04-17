# Standard Imports
import os
import collections
import unittest
from unittest import mock
import signal

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
        "data": data,
        "params": params,
        "json": json,
        "ssl": None,
    }
    return req_args


def SendMock():
    coro = mock.Mock(name="SendResult")
    coro.return_value = {
        "headers": {},
        "data": {
            "ok": True,
            "url": "ws://localhost:8765",
            "self": {"id": "U01234ABC", "name": "robotoverlord"},
            "team": {
                "domain": "exampledomain",
                "id": "T123450FP",
                "name": "ExampleName",
            },
        },
        "status_code": 200,
    }
    corofunc = mock.Mock(name="_send", side_effect=asyncio.coroutine(coro))
    corofunc.coro = coro
    return corofunc


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

    @mock.patch("slack.WebClient._send", new_callable=SendMock)
    def test_start_raises_an_error_if_rtm_ws_url_is_not_returned(self, mock_send):
        mock_send.coro.return_value = {
            "data": {"ok": True},
            "headers": {},
            "status_code": 200,
        }

        with self.assertRaises(e.SlackApiError) as context:
            slack.RTMClient(auto_reconnect=False).start()

        expected_error = "Unable to retreive RTM URL from Slack"
        self.assertIn(expected_error, str(context.exception))


@mock.patch("slack.WebClient._send", new_callable=SendMock)
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
        task = asyncio.ensure_future(self.mock_server(), loop=self.loop)
        self.loop.run_until_complete(asyncio.wait([task], timeout=0.1))

        self.client = slack.RTMClient(loop=self.loop, auto_reconnect=False)

    def tearDown(self):
        self.stop.set_result(None)
        slack.RTMClient._callbacks = collections.defaultdict(list)

    if os.name != "nt":

        def test_kill_signals_are_handled_gracefully(self, mock_send):
            @slack.RTMClient.run_on(event="open")
            def kill_on_open(**payload):
                rtm_client = payload["rtm_client"]
                self.assertFalse(rtm_client._stopped)
                os.kill(os.getpid(), signal.SIGINT)

            self.client.start()
            self.assertTrue(self.client._stopped)
            self.assertIsNone(self.client._websocket)

    def test_client_auto_reconnects_if_connection_randomly_closes(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            rtm_client = payload["rtm_client"]

            if rtm_client._connection_attempts == 1:
                rtm_client._close_websocket()
            else:
                self.assertEqual(rtm_client._connection_attempts, 2)
                rtm_client.stop()

        client = slack.RTMClient(auto_reconnect=True)
        client.start()

    def test_client_auto_reconnects_if_an_error_is_thrown(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            rtm_client = payload["rtm_client"]

            if rtm_client._connection_attempts == 1:
                raise e.SlackApiError("Test Error", {"headers": {"Retry-After": 0.001}})
            else:
                self.assertEqual(rtm_client._connection_attempts, 2)
                rtm_client.stop()

        client = slack.RTMClient(auto_reconnect=True)
        client.start()

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
            self.assertFalse(self.client._websocket.closed)

            rtm_client = payload["rtm_client"]
            rtm_client.stop()

        self.client.start()
        self.assertIsNone(self.client._websocket)

    def test_start_calls_rtm_connect_by_default(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            self.assertFalse(self.client._websocket.closed)
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
            self.assertFalse(self.client._websocket.closed)
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
        with self.assertRaises(e.SlackClientNotConnectedError):
            self.client.start()
        self.error_hanlding_mock.assert_called_once()

    def test_callback_errors_are_raised(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def raise_an_error(**payload):
            raise Exception("Testing error handling.")

        with self.assertRaises(Exception) as context:
            self.client.start()

        expected_error = "Testing error handling."
        self.assertIn(expected_error, str(context.exception))

    def test_on_close_callbacks(self, mock_send):
        @slack.RTMClient.run_on(event="open")
        def stop_on_open(**payload):
            payload["rtm_client"].stop()

        @slack.RTMClient.run_on(event="close")
        def assert_on_close(**payload):
            self.close_mock(str(payload["data"]))

        self.close_mock = mock.Mock()
        self.client.start()
        self.close_mock.assert_called_once()
