import unittest
import warnings

from slack_sdk import WebClient
from tests.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClientUnknownKwargsWarnings(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_warns_on_thread_id_typo_chat_postMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`thread_id` argument is not a recognized parameter"):
            resp = client.chat_postMessage(
                channel="C111",
                text="hi",
                thread_id="1750000000.0001",
            )
        self.assertIsNone(resp["error"])

    def test_warns_on_unfurl_link_typo_chat_postMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`unfurl_link` argument is not a recognized parameter"):
            resp = client.chat_postMessage(
                channel="C111",
                text="hi",
                unfurl_link=False,
            )
        self.assertIsNone(resp["error"])

    def test_no_warning_for_known_thread_ts(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            resp = client.chat_postMessage(
                channel="C111",
                text="hi",
                thread_ts="1750000000.0001",
            )
        unknown = [w for w in warning_list if "not a recognized parameter" in str(w.message)]
        self.assertEqual(unknown, [])
        self.assertIsNone(resp["error"])
