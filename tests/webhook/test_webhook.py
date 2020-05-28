import unittest

from slack.webhook import WebhookClient, WebhookResponse
from tests.webhook.mock_web_api_server import cleanup_mock_web_api_server, setup_mock_web_api_server


class TestWebhook(unittest.TestCase):

    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_call_webhook(self):
        client = WebhookClient("http://localhost:8888")
        resp: WebhookResponse = client.send({"text": "hello!"})
        self.assertEqual(200, resp.status_code)
        self.assertEqual("ok", resp.body)
