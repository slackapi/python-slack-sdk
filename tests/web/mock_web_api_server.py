import json
import logging
import re
import threading
import time
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

    html_response_body = '<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\n<html><head>\n<title>404 Not Found</title>\n</head><body>\n<h1>Not Found</h1>\n<p>The requested URL /api/team.info was not found on this server.</p>\n</body></html>\n'

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) \
               and self.pattern_for_package_identifier.search(user_agent)

    def is_valid_token(self):
        if self.path.startswith("oauth"):
            return True
        return "Authorization" in self.headers \
               and str(self.headers["Authorization"]).startswith("Bearer xoxb-")

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
            if self.path in {"/oauth.access", "/oauth.v2.access"}:
                self.send_response(200)
                self.set_common_headers()
                if self.headers["authorization"] == "Basic MTExLjIyMjpzZWNyZXQ=":
                    self.wfile.write("""{"ok":true}""".encode("utf-8"))
                    return
                else:
                    self.wfile.write("""{"ok":false, "error":"invalid"}""".encode("utf-8"))
                    return

            if self.is_valid_token() and self.is_valid_user_agent():
                parsed_path = urlparse(self.path)

                len_header = self.headers.get('Content-Length') or 0
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

                header = self.headers["authorization"]
                pattern = str(header).split("xoxb-", 1)[1]
                if pattern.isnumeric():
                    self.send_response(int(pattern))
                    self.set_common_headers()
                    self.wfile.write("""{"ok":false}""".encode("utf-8"))
                    return
                if pattern == "rate_limited":
                    self.send_response(429)
                    self.send_header("Retry-After", 30)
                    self.set_common_headers()
                    self.wfile.write("""{"ok":false,"error":"rate_limited"}""".encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern == "timeout":
                    time.sleep(2)
                    self.send_response(200)
                    self.wfile.write("""{"ok":true}""".encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern == "html_response":
                    self.send_response(404)
                    self.set_common_headers()
                    self.wfile.write(self.html_response_body.encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern.startswith("user-agent"):
                    elements = pattern.split(" ")
                    prefix, suffix = elements[1], elements[-1]
                    ua: str = self.headers["User-Agent"]
                    if ua.startswith(prefix) and ua.endswith(suffix):
                        self.send_response(200)
                        self.set_common_headers()
                        self.wfile.write("""{"ok":true}""".encode("utf-8"))
                        self.wfile.close()
                        return
                    else:
                        self.send_response(400)
                        self.set_common_headers()
                        self.wfile.write("""{"ok":false, "error":"invalid_user_agent"}""".encode("utf-8"))
                        self.wfile.close()
                        return

                if request_body and "cursor" in request_body:
                    page = request_body["cursor"]
                    pattern = f"{pattern}_{page}"
                if pattern == "coverage":
                    if self.path.startswith("/calls."):
                        for k, v in request_body.items():
                            if k == "users":
                                users = json.loads(v)
                                for u in users:
                                    if "slack_id" not in u and "external_id" not in u:
                                        raise Exception(f"User ({u}) is invalid value")
                    else:
                        ids = ["channels", "users", "channel_ids"]
                        if request_body:
                            for k, v in request_body.items():
                                if k in ids:
                                    if not re.compile(r"^[^,\[\]]+?,[^,\[\]]+$").match(v):
                                        raise Exception(
                                            f"The parameter {k} is not a comma-separated string value: {v}"
                                        )
                    body = {"ok": True, "method": parsed_path.path.replace("/", "")}
                else:
                    with open(f"tests/data/web_response_{pattern}.json") as file:
                        body = json.load(file)

                    if self.path == "/api.test" and request_body:
                        body["args"] = request_body

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

    def __init__(self, test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler):
        threading.Thread.__init__(self)
        self.handler = handler
        self.test = test

    def run(self):
        self.server = HTTPServer(('localhost', 8888), self.handler)
        self.test.server_url = "http://localhost:8888"
        self.test.host, self.test.port = self.server.socket.getsockname()
        self.test.server_started.set()  # threading.Event()

        self.test = None
        try:
            self.server.serve_forever(0.05)
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
