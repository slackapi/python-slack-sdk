import json
import unittest

from slack_sdk.socket_mode.response import SocketModeResponse


class TestResponse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parser(self):
        text = """{"envelope_id":"1d3c79ab-0ffb-41f3-a080-d19e85f53649","payload":{"text":"Thanks!"}}"""
        body = json.loads(text)
        response = SocketModeResponse(body["envelope_id"], body["payload"])
        self.assertIsNotNone(response)
        self.assertEqual(response.envelope_id, "1d3c79ab-0ffb-41f3-a080-d19e85f53649")
        self.assertEqual(response.payload.get("text"), "Thanks!")

    def test_to_dict(self):
        response = SocketModeResponse(envelope_id="xxx", payload={"text": "hi"})
        self.assertDictEqual(response.to_dict(), {"envelope_id": "xxx", "payload": {"text": "hi"}})
