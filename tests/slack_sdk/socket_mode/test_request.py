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
