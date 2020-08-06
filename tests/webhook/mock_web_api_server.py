import logging
import re
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Type
from unittest import TestCase


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) \
               and self.pattern_for_package_identifier.search(user_agent)

    def set_common_headers(self):
        self.send_header("content-type", "text/plain;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    def do_POST(self):
        try:
            if self.path == "/timeout":
                time.sleep(2)

            # user-agent-this_is-test
            if self.path.startswith("/user-agent-"):
                elements = self.path.split("-")
                prefix, suffix = elements[2], elements[-1]
                ua: str = self.headers["User-Agent"]
                if ua.startswith(prefix) and ua.endswith(suffix):
                    self.send_response(HTTPStatus.OK)
                    self.set_common_headers()
                    self.wfile.write("ok".encode("utf-8"))
                    self.wfile.close()
                    return
                else:
                    self.send_response(HTTPStatus.BAD_REQUEST)
                    self.set_common_headers()
                    self.wfile.write("invalid user agent".encode("utf-8"))
                    self.wfile.close()
                    return

            if self.path == "/error":
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.set_common_headers()
                self.wfile.write("error".encode("utf-8"))
                self.wfile.close()
                return

            body = "ok"

            self.send_response(HTTPStatus.OK)
            self.set_common_headers()
            self.wfile.write(body.encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise


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
