# Standard Imports
import collections
import unittest
from unittest import mock

# Internal Imports
import slack
import slack.errors as e
from tests.helpers import mock_rtm_response


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

    @mock.patch("slack.WebClient._send", new_callable=mock_rtm_response)
    def test_start_raises_an_error_if_rtm_ws_url_is_not_returned(
        self, mock_rtm_response
    ):
        mock_rtm_response.coro.return_value = {
            "data": {"ok": True},
            "headers": {},
            "status_code": 200,
        }

        with self.assertRaises(e.SlackApiError) as context:
            slack.RTMClient(auto_reconnect=False).start()

        expected_error = "Unable to retreive RTM URL from Slack"
        self.assertIn(expected_error, str(context.exception))
