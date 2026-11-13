import json
import logging
import unittest

from slack_sdk import WebClient
from slack_sdk.errors import SlackRequestError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler, ServerErrorRetryHandler
from slack_sdk.web.internal_utils import _upload_file_via_v2_url
from tests.mock_web_api_server import (
    assert_received_request_count,
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)
from tests.slack_sdk.web.mock_web_api_handler import MockHandler


class FailingUploadMockHandler(MockHandler):
    def _handle(self):
        self.server.queue.put_nowait(self.path)
        self.rfile.read(int(self.headers.get("Content-Length") or 0))

        if self.path == "/files.getUploadURLExternal":
            upload_url = f"http://localhost:{self.server.server_address[1]}/upload/v1/abc"
            self.send_response(200)
            self.set_common_headers()
            self.wfile.write(json.dumps({"ok": True, "file_id": "F111", "upload_url": upload_url}).encode("utf-8"))
            return

        self.send_response(500)
        self.send_header("content-type", "text/plain; charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()
        self.wfile.write("upload failed".encode("utf-8"))


class TestWebClientFilesUploadV2(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self, FailingUploadMockHandler)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_upload_file_via_v2_url_returns_the_error_response(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        with self.assertLogs(logger, logging.DEBUG) as logs:
            result = _upload_file_via_v2_url(
                url=f"{self.server_url}/upload/v1/abc",
                data=b"hello",
                timeout=5,
                logger=logger,
            )

        self.assertEqual(result["status"], 500)
        self.assertEqual(result["body"], "upload failed")
        self.assertIn("Received the following response - status: 500", logs.output[-1])
        self.assertIn("body: upload failed", logs.output[-1])

    def test_files_upload_v2_raises_slack_request_error_without_retrying_the_upload(self):
        client = WebClient(
            token="xoxb-api_test",
            base_url=self.server_url,
            retry_handlers=[ServerErrorRetryHandler(), RateLimitErrorRetryHandler()],
        )

        with self.assertRaises(SlackRequestError) as context:
            client.files_upload_v2(content="hello", filename="hello.txt")

        self.assertIn("status: 500", str(context.exception))
        self.assertIn("body: upload failed", str(context.exception))
        assert_received_request_count(self, "/upload/v1/abc", 1)
