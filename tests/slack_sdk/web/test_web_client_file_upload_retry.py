import logging
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError

from slack_sdk.http_retry import RetryHandler
from slack_sdk.http_retry.handler import default_interval_calculator
from slack_sdk.http_retry.interval_calculator import RetryIntervalCalculator
from slack_sdk.web import WebClient


class GatewayErrorRetryHandler(RetryHandler):
    """Retry 5xx responses from the files.slack.com upload POST."""

    def __init__(
        self,
        max_retry_count: int = 2,
        interval_calculator: RetryIntervalCalculator = default_interval_calculator,
    ):
        super().__init__(max_retry_count, interval_calculator)
        self.call_count = 0

    def _can_retry(
        self,
        *,
        state,
        request,
        response,
        error,
    ) -> bool:
        self.call_count += 1
        return response is not None and response.status_code >= 500


class _UploadHandler(BaseHTTPRequestHandler):
    attempts = 0
    fail_times = 1
    fail_status = 504

    def do_POST(self):
        _UploadHandler.attempts += 1
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        if _UploadHandler.attempts <= _UploadHandler.fail_times:
            self.send_response(_UploadHandler.fail_status)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"gateway timeout")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format, *args):
        pass


class TestWebClient_FileUploadRetry(unittest.TestCase):
    def setUp(self):
        _UploadHandler.attempts = 0
        _UploadHandler.fail_times = 1
        _UploadHandler.fail_status = 504
        self.server = HTTPServer(("127.0.0.1", 0), _UploadHandler)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        host, port = self.server.server_address
        self.upload_url = f"http://127.0.0.1:{port}/upload"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _upload(self, client: WebClient):
        return client._upload_file(
            url=self.upload_url,
            data=b"hello file",
            logger=logging.getLogger(__name__),
            timeout=5,
            proxy=None,
            ssl=None,
        )

    def test_upload_retries_gateway_error_with_handler(self):
        retry_handler = GatewayErrorRetryHandler(max_retry_count=2)
        client = WebClient(token="xoxb-test", retry_handlers=[retry_handler])
        result = self._upload(client)
        self.assertEqual(200, result.status)
        self.assertEqual("ok", result.body)
        self.assertEqual(2, _UploadHandler.attempts)
        self.assertGreaterEqual(retry_handler.call_count, 1)

    def test_upload_without_matching_handler_surfaces_error(self):
        client = WebClient(token="xoxb-test", retry_handlers=[])
        with self.assertRaises(HTTPError) as cm:
            self._upload(client)
        self.assertEqual(504, cm.exception.code)
        self.assertEqual(1, _UploadHandler.attempts)
