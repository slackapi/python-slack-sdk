import json
import logging
import re
import threading
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Type
from unittest import TestCase
from urllib.parse import urlparse, parse_qs


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(
            user_agent
        ) and self.pattern_for_package_identifier.search(user_agent)

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
                            request_body = {
                                k: v[0] for k, v in parse_qs(post_body).items()
                            }
                    except UnicodeDecodeError:
                        pass
                else:
                    if parsed_path and parsed_path.query:
                        request_body = {
                            k: v[0] for k, v in parse_qs(parsed_path.query).items()
                        }

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
                        "url": "wss://test-server/link/?ticket=xxx&app_id=yyy",
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


class MockServerThread(threading.Thread):
    def __init__(
        self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler
    ):
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
    test.server_started = threading.Event()
    test.thread = MockServerThread(test)
    test.thread.start()

    test.server_started.wait()


def cleanup_mock_web_api_server(test: TestCase):
    test.thread.stop()

    test.thread = None
