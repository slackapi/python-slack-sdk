import asyncio
import json
import logging
from queue import Queue
import re
import threading
import time
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Type, Union
from unittest import TestCase
from urllib.parse import urlparse, parse_qs


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)

    pattern_for_language = re.compile("python/(\\S+)", re.IGNORECASE)
    pattern_for_package_identifier = re.compile("slackclient/(\\S+)")

    html_response_body = '<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n<html><head>\n<title>404 Not Found</title>\n</head><body>\n<h1>Not Found</h1>\n<p>The requested URL /api/team.info was not found on this server.</p>\n</body></html>\n'

    error_html_response_body = '<!DOCTYPE html>\n<html lang="en">\n<head>\n\t<meta charset="utf-8">\n\t<title>Server Error | Slack</title>\n\t<meta name="author" content="Slack">\n\t<style></style>\n</head>\n<body>\n\t<nav class="top persistent">\n\t\t<a href="https://status.slack.com/" class="logo" data-qa="logo"></a>\n\t</nav>\n\t<div id="page">\n\t\t<div id="page_contents">\n\t\t\t<h1>\n\t\t\t\t<svg width="30px" height="27px" viewBox="0 0 60 54" class="warning_icon"><path d="" fill="#D94827"/></svg>\n\t\t\t\tServer Error\n\t\t\t</h1>\n\t\t\t<div class="card">\n\t\t\t\t<p>It seems like there’s a problem connecting to our servers, and we’re investigating the issue.</p>\n\t\t\t\t<p>Please <a href="https://status.slack.com/">check our Status page for updates</a>.</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n\t<script type="text/javascript">\n\t\tif (window.desktop) {\n\t\t\tdocument.documentElement.className = \'desktop\';\n\t\t}\n\n\t\tvar FIVE_MINS = 5 * 60 * 1000;\n\t\tvar TEN_MINS = 10 * 60 * 1000;\n\n\t\tfunction randomBetween(min, max) {\n\t\t\treturn Math.floor(Math.random() * (max - (min + 1))) + min;\n\t\t}\n\n\t\twindow.setTimeout(function () {\n\t\t\twindow.location.reload(true);\n\t\t}, randomBetween(FIVE_MINS, TEN_MINS));\n\t</script>\n</body>\n</html>'

    state = {"ratelimited_count": 0, "fatal_error_count": 0, "server_error_count": 0}

    def is_valid_user_agent(self):
        user_agent = self.headers["User-Agent"]
        return self.pattern_for_language.search(user_agent) and self.pattern_for_package_identifier.search(user_agent)

    def is_valid_token(self):
        if self.path.startswith("oauth"):
            return True
        return "Authorization" in self.headers and str(self.headers["Authorization"]).startswith("Bearer xoxb-")

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

    token_refresh = {
        "ok": True,
        "app_id": "A111",
        "authed_user": {
            "id": "W111",
            "scope": "search:read",
            "access_token": "xoxe.xoxp-1-xxx",
            "token_type": "user",
            "refresh_token": "xoxe-1-xxx",
            "expires_in": 43200,
        },
        "scope": "app_mentions:read,chat:write,commands",
        "token_type": "bot",
        "access_token": "xoxe.xoxb-1-yyy",
        "bot_user_id": "UB111",
        "refresh_token": "xoxe-1-yyy",
        "expires_in": 43201,
        "team": {"id": "T111", "name": "Testing Workspace"},
        "enterprise": {"id": "E111", "name": "Sandbox Org"},
        "is_enterprise_install": False,
    }

    def _handle(self):
        try:
            # put_nowait is common between Queue & asyncio.Queue, it does not need to be awaited
            self.server.queue.put_nowait(self.path)

            if self.path in {"/oauth.access", "/oauth.v2.access"}:
                self.send_response(200)
                self.set_common_headers()
                if self.headers["authorization"] == "Basic MTExLjIyMjpzZWNyZXQ=":
                    self.wfile.write("""{"ok":true}""".encode("utf-8"))
                    return
                elif self.headers["authorization"] == "Basic MTExLjIyMjp0b2tlbl9yb3RhdGlvbl9zZWNyZXQ=":
                    self.wfile.write(json.dumps(self.token_refresh).encode("utf-8"))
                    return
                else:
                    self.wfile.write("""{"ok":false, "error":"invalid"}""".encode("utf-8"))
                    return

            header = self.headers["Authorization"]
            if header is not None and ("xoxb-" in header or "xoxp-" in header):
                pattern = ""
                xoxb = str(header).split("xoxb-", 1)
                if len(xoxb) > 1:
                    pattern = xoxb[1]
                else:
                    xoxp = str(header).split("xoxp-", 1)
                    pattern = xoxp[1]

                if "remote_disconnected" in pattern:
                    # http.client.RemoteDisconnected
                    self.finish()
                    return

                if pattern == "ratelimited" or (pattern == "ratelimited_only_once" and self.state["ratelimited_count"] == 0):
                    self.state["ratelimited_count"] += 1
                    self.send_response(429)
                    self.send_header("retry-after", 1)
                    self.send_header("content-type", "application/json;charset=utf-8")
                    self.send_header("connection", "close")
                    self.end_headers()
                    self.wfile.write("""{"ok":false,"error":"ratelimited"}""".encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern == "fatal_error" or (pattern == "fatal_error_only_once" and self.state["fatal_error_count"] == 0):
                    self.state["fatal_error_count"] += 1
                    self.send_response(200)
                    self.set_common_headers()
                    self.wfile.write("""{"ok":false,"error":"fatal_error"}""".encode("utf-8"))
                    self.wfile.close()
                    return

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

                header = self.headers["authorization"]
                pattern = str(header).split("xoxb-", 1)[1]
                if pattern.isnumeric():
                    self.send_response(int(pattern))
                    self.set_common_headers()
                    self.wfile.write("""{"ok":false}""".encode("utf-8"))
                    return

                if pattern == "timeout":
                    time.sleep(3)
                    self.send_response(200)
                    self.set_common_headers()
                    self.wfile.write("""{"ok":true}""".encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern == "html_response":
                    self.send_response(404)
                    self.send_header("content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(self.html_response_body.encode("utf-8"))
                    self.wfile.close()
                    return

                if pattern == "error_html_response":
                    self.send_response(503)
                    # no charset here is intentional for testing
                    self.send_header("content-type", "text/html")
                    self.send_header("connection", "close")
                    self.end_headers()
                    self.wfile.write(self.error_html_response_body.encode("utf-8"))
                    self.wfile.close()
                    return
                if pattern == "server_error_only_once":
                    if self.state["server_error_count"] == 0:
                        self.state["server_error_count"] += 1
                        self.send_response(500)
                        # no charset here is intentional for testing
                        self.send_header("content-type", "text/html")
                        self.send_header("connection", "close")
                        self.end_headers()
                        self.wfile.write(self.error_html_response_body.encode("utf-8"))
                        self.wfile.close()
                        return
                    else:
                        self.send_response(200)
                        self.set_common_headers()
                        self.wfile.write("""{"ok":true}""".encode("utf-8"))
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
                                        raise Exception(f"The parameter {k} is not a comma-separated string value: {v}")
                    body = {"ok": True, "method": parsed_path.path.replace("/", "")}
                else:
                    with open(f"tests/slack_sdk_fixture/web_response_{pattern}.json") as file:
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
    def __init__(
        self, queue: Union[Queue, asyncio.Queue], test: TestCase, handler: Type[SimpleHTTPRequestHandler] = MockHandler
    ):
        threading.Thread.__init__(self)
        self.handler = handler
        self.test = test
        self.queue = queue

    def run(self):
        self.server = HTTPServer(("localhost", 8888), self.handler)
        self.server.queue = self.queue
        self.test.server_url = "http://localhost:8888"
        self.test.host, self.test.port = self.server.socket.getsockname()
        self.test.server_started.set()  # threading.Event()

        self.test = None
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        with self.server.queue.mutex:
            del self.server.queue
        self.server.shutdown()
        self.join()

    def stop_unsafe(self):
        del self.server.queue
        self.server.shutdown()
        self.join()
