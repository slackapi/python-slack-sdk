import asyncio
import json
import logging
import re
import sys
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from multiprocessing.context import Process
from typing import Type
from unittest import TestCase
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen

from tests.helpers import get_mock_server_mode


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def is_valid_token(self):
        if self.path.startswith("oauth"):
            return True
        return "Authorization" in self.headers and (
            str(self.headers["Authorization"]).startswith("Bearer xoxb-")
            or str(self.headers["Authorization"]).startswith("Bearer xapp-")
        )

    def set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    invalid_auth = {
        "ok": False,
        "error": "invalid_auth",
    }

    not_found = {
        "ok": False,
        "error": "test_data_not_found",
    }

    def _handle(self):
        try:
            if self.is_valid_token() and self.is_valid_user_agent():
                parsed_path = urlparse(self.path)

                len_header = self.headers.get("Content-Length") or 0
                content_len = int(len_header)
                post_body = self.rfile.read(content_len)
                request_body = None
                if post_body:
                    try:
                        post_body = post_body.decode("utf-8")
                        if post_body.startswith("{"):
                            request_body = json.loads(post_body)
                        else:
                            request_body = {k: v[0] for k, v in parse_qs(post_body).items()}
                    except UnicodeDecodeError:
                        pass
                else:
                    if parsed_path and parsed_path.query:
                        request_body = {k: v[0] for k, v in parse_qs(parsed_path.query).items()}

                body = {"ok": False, "error": "internal_error"}
                if self.path == "/auth.test":
                    body = {
                        "ok": True,
                        "url": "https://xyz.slack.com/",
                        "team": "Testing Workspace",
                        "user": "bot-user",
                        "team_id": "T111",
                        "user_id": "W11",
                        "bot_id": "B111",
                        "enterprise_id": "E111",
                        "is_enterprise_install": False,
                    }
                if self.path == "/apps.connections.open":
                    body = {
                        "ok": True,
                        "url": "ws://0.0.0.0:3001/link",
                    }
                if self.path == "/api.test" and request_body:
                    body = {"ok": True, "args": request_body}
            else:
                body = self.invalid_auth

            if not body:
                body = self.not_found

            self.send_response(HTTPStatus.OK)
            self.set_common_headers()
            self.wfile.write(json.dumps(body).encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()

    def do_CONNECT(self):
        self.wfile.write("HTTP/1.1 200 Connection established\r\n\r\n".encode("utf-8"))
        self.wfile.close()


class MockServerProcessTarget:
    def __init__(self, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        self.handler = handler

    def run(self):
        self.handler.received_requests = {}
        self.server = HTTPServer(("localhost", 8888), self.handler)
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        self.handler.received_requests = {}
        self.server.shutdown()
        self.join()


class MonitorThread(threading.Thread):
    def __init__(self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        threading.Thread.__init__(self, daemon=True)
        self.handler = handler
        self.test = test
        self.test.mock_received_requests = None
        self.is_running = True

    def run(self) -> None:
        while self.is_running:
            try:
                req = Request(f"{self.test.server_url}/received_requests.json")
                resp = urlopen(req, timeout=1)
                self.test.mock_received_requests = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                # skip logging for the initial request
                if self.test.mock_received_requests is not None:
                    logging.getLogger(__name__).exception(e)
            time.sleep(0.01)

    def stop(self):
        self.is_running = False
        self.join()


class MockServerThread(threading.Thread):
    def __init__(self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        threading.Thread.__init__(self)
        self.handler = handler
        self.test = test

    def run(self):
        self.server = HTTPServer(("localhost", 8888), self.handler)
        self.test.server_url = "http://localhost:8888"
        self.test.host, self.test.port = self.server.socket.getsockname()
        self.test.server_started.set()  # threading.Event()

        self.test = None
        try:
            self.server.serve_forever()
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()
        self.join()


def setup_mock_web_api_server(test: TestCase):
    if get_mock_server_mode() == "threading":
        test.server_started = threading.Event()
        test.thread = MockServerThread(test)
        test.thread.start()
        test.server_started.wait()
    else:
        # start a mock server as another process
        target = MockServerProcessTarget()
        test.server_url = "http://localhost:8888"
        test.host, test.port = "localhost", 8888
        test.process = Process(target=target.run, daemon=True)
        test.process.start()

        time.sleep(0.1)

        # start a thread in the current process
        # this thread fetches mock_received_requests from the remote process
        test.monitor_thread = MonitorThread(test)
        test.monitor_thread.start()
        count = 0
        # wait until the first successful data retrieval
        while test.mock_received_requests is None:
            time.sleep(0.01)
            count += 1
            if count >= 100:
                raise Exception("The mock server is not yet running!")


def cleanup_mock_web_api_server(test: TestCase):
    if get_mock_server_mode() == "threading":
        test.thread.stop()
        test.thread = None
    else:
        # stop the thread to fetch mock_received_requests from the remote process
        test.monitor_thread.stop()

        retry_count = 0
        # terminate the process
        while test.process.is_alive():
            test.process.terminate()
            time.sleep(0.01)
            retry_count += 1
            if retry_count >= 100:
                raise Exception("Failed to stop the mock server!")

        # Python 3.6 does not have this method
        if sys.version_info.major == 3 and sys.version_info.minor > 6:
            # cleanup the process's resources
            test.process.close()

        test.process = None


def assert_auth_test_count(test: TestCase, expected_count: int):
    time.sleep(0.1)
    retry_count = 0
    error = None
    while retry_count < 3:
        try:
            test.mock_received_requests["/auth.test"] == expected_count
            break
        except Exception as e:
            error = e
            retry_count += 1
            # waiting for mock_received_requests updates
            time.sleep(0.1)

    if error is not None:
        raise error


async def assert_auth_test_count_async(test: TestCase, expected_count: int):
    await asyncio.sleep(0.1)
    retry_count = 0
    error = None
    while retry_count < 3:
        try:
            test.mock_received_requests["/auth.test"] == expected_count
            break
        except Exception as e:
            error = e
            retry_count += 1
            # waiting for mock_received_requests updates
            await asyncio.sleep(0.1)

    if error is not None:
        raise error
