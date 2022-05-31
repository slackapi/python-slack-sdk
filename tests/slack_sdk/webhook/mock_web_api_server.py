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
from urllib.request import Request, urlopen

from tests.helpers import get_mock_server_mode


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    error_html_response_body = '<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<meta charset="utf-8">\n\t<title>Server Error | Slack</title>\n\t<meta name="author" content="Slack">\n\t<style></style>\n</head>\n<body>\n\t<nav class="top persistent">\n\t\t<a href="https://status.slack.com/" class="logo" data-qa="logo"></a>\n\t</nav>\n\t<div id="page">\n\t\t<div id="page_contents">\n\t\t\t<h1>\n\t\t\t\t<svg width="30px" height="27px" viewBox="0 0 60 54" class="warning_icon"><path d="" fill="#D94827"/></svg>\n\t\t\t\tServer Error\n\t\t\t</h1>\n\t\t\t<div class="card">\n\t\t\t\t<p>It seems like there’s a problem connecting to our servers, and we’re investigating the issue.</p>\n\t\t\t\t<p>Please <a href="https://status.slack.com/">check our Status page for updates</a>.</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n\t<script type="text/javascript">\n\t\tif (window.desktop) {\n\t\t\tdocument.documentElement.className = \'desktop\';\n\t\t}\n\n\t\tvar FIVE_MINS = 5 * 60 * 1000;\n\t\tvar TEN_MINS = 10 * 60 * 1000;\n\n\t\tfunction randomBetween(min, max) {\n\t\t\treturn Math.floor(Math.random() * (max - (min + 1))) + min;\n\t\t}\n\n\t\twindow.setTimeout(function () {\n\t\t\twindow.location.reload(true);\n\t\t}, randomBetween(FIVE_MINS, TEN_MINS));\n\t</script>\n</body>\n</html>'

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def set_common_headers(self):
        self.send_header("content-type", "text/plain;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    def do_GET(self):
        if self.path == "/received_requests.json":
            self.send_response(200)
            self.set_common_headers()
            self.wfile.write(json.dumps(self.received_requests).encode("utf-8"))
            return

    def do_POST(self):
        try:
            if self.path == "/remote_disconnected":
                # http.client.RemoteDisconnected
                self.finish()
                return

            if self.path == "/ratelimited":
                self.send_response(429)
                self.send_header("retry-after", 1)
                self.set_common_headers()
                self.wfile.write("".encode("utf-8"))
                return

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
                # no charset here is intentional for testing
                self.send_header("content-type", "text/html")
                self.send_header("connection", "close")
                self.end_headers()
                self.wfile.write(self.error_html_response_body.encode("utf-8"))
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
