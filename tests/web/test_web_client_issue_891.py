import unittest
import warnings

from slack import WebClient
from tests.web.mock_web_api_handler import MockHandler
from tests.mock_web_api_server import setup_mock_web_api_server, cleanup_mock_web_api_server


class TestWebClient_Issue_891(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, MockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server(self)
        warnings.resetwarnings()

    def test_missing_text_warning_chat_postMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`text` argument is missing"):
            resp = client.chat_postMessage(channel="C111", blocks=[])
        self.assertIsNone(resp["error"])

    def test_missing_text_warning_chat_postEphemeral(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`text` argument is missing"):
            resp = client.chat_postEphemeral(channel="C111", user="U111", blocks=[])
        self.assertIsNone(resp["error"])

    def test_missing_text_warning_chat_scheduleMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`text` argument is missing"):
            resp = client.chat_scheduleMessage(channel="C111", post_at="299876400", text="", blocks=[])
        self.assertIsNone(resp["error"])

    def test_missing_text_warning_chat_update(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`text` argument is missing"):
            resp = client.chat_update(channel="C111", ts="111.222", blocks=[])
        self.assertIsNone(resp["error"])

    def test_missing_fallback_warning_chat_postMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`fallback` argument is missing"):
            resp = client.chat_postMessage(channel="C111", blocks=[], attachments=[{"text": "hi"}])
        self.assertIsNone(resp["error"])

    def test_missing_fallback_warning_chat_postEphemeral(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`fallback` argument is missing"):
            resp = client.chat_postEphemeral(channel="C111", user="U111", blocks=[], attachments=[{"text": "hi"}])
        self.assertIsNone(resp["error"])

    def test_missing_fallback_warning_chat_scheduleMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`fallback` argument is missing"):
            resp = client.chat_scheduleMessage(
                channel="C111",
                post_at="299876400",
                text="",
                blocks=[],
                attachments=[{"text": "hi"}],
            )
        self.assertIsNone(resp["error"])

    def test_missing_fallback_warning_chat_update(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with self.assertWarnsRegex(UserWarning, "`fallback` argument is missing"):
            resp = client.chat_update(channel="C111", ts="111.222", blocks=[], attachments=[{"text": "hi"}])
        self.assertIsNone(resp["error"])
    
    def test_no_warning_when_markdown_text_is_provided_chat_postMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always") 
            resp = client.chat_postMessage(
                channel="C111", 
                markdown_text="# hello" 
            )
        
        self.assertEqual(warning_list, [])
        self.assertIsNone(resp["error"])
    
    def test_no_warning_when_markdown_text_is_provided_chat_postEphemeral(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always") 
            resp = client.chat_postEphemeral(
                channel="C111", 
                user="U111",
                markdown_text="# hello" 
            )
        
        self.assertEqual(warning_list, [])
        self.assertIsNone(resp["error"])
    
    def test_no_warning_when_markdown_text_is_provided_chat_scheduleMessage(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always") 
            resp = client.chat_scheduleMessage(
                channel="C111", 
                post_at="299876400",
                markdown_text="# hello" 
            )
        
        self.assertEqual(warning_list, [])
        self.assertIsNone(resp["error"])
    
    def test_no_warning_when_markdown_text_is_provided_chat_update(self):
        client = WebClient(base_url="http://localhost:8888", token="xoxb-api_test")
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always") 
            resp = client.chat_update(
                channel="C111", 
                ts="111.222",
                markdown_text="# hello" 
            )
        
        self.assertEqual(warning_list, [])
        self.assertIsNone(resp["error"])

