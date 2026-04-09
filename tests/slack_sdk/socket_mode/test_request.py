import json
import unittest

from slack_sdk.socket_mode.request import SocketModeRequest


class TestRequest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        body = json.loads(
            """{"envelope_id":"1d3c79ab-0ffb-41f3-a080-d19e85f53649","payload":{"token":"xxx","team_id":"T111","team_domain":"xxx","channel_id":"C03E94MKU","channel_name":"random","user_id":"U111","user_name":"seratch","command":"/hello-socket-mode","text":"","api_app_id":"A111","response_url":"https://hooks.slack.com/commands/T111/111/xxx","trigger_id":"111.222.xxx"},"type":"slash_commands","accepts_response_payload":true}"""
        )
        req = SocketModeRequest.from_dict(body)
        self.assertIsNotNone(req)
        self.assertEqual(req.envelope_id, "1d3c79ab-0ffb-41f3-a080-d19e85f53649")

    def test_to_dict(self):
        req = SocketModeRequest(
            type="slash_commands",
            envelope_id="abc-123",
            payload={"text": "hello"},
        )
        self.assertDictEqual(
            req.to_dict(), {"type": "slash_commands", "envelope_id": "abc-123", "payload": {"text": "hello"}}
        )

    def test_to_dict_from_dict_round_trip(self):
        expected = SocketModeRequest(
            type="slash_commands",
            envelope_id="1d3c79ab-0ffb-41f3-a080-d19e85f53649",
            payload={"token": "xxx", "team_id": "T111", "command": "/hello"},
            accepts_response_payload=True,
            retry_attempt=2,
            retry_reason="timeout",
        )
        actual = SocketModeRequest.from_dict(expected.to_dict())
        self.assertIsNotNone(actual)
        self.assertEqual(actual.type, expected.type)
        self.assertEqual(actual.envelope_id, expected.envelope_id)
        self.assertEqual(actual.payload, expected.payload)
