import logging
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler


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
        return "Authorization" in self.headers and str(self.headers["Authorization"]).startswith("Bearer xoxp-")

    def set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    def _handle(self):
        try:
            # put_nowait is common between Queue & asyncio.Queue, it does not need to be awaited
            self.server.queue.put_nowait(self.path)
            header = self.headers["Authorization"]
            if header is not None and "xoxp-" in header:
                pattern = str(header).split("xoxp-", 1)[1]
                if "remote_disconnected" in pattern:
                    # http.client.RemoteDisconnected
                    self.finish()
                    return
                if "ratelimited" in pattern:
                    self.send_response(429)
                    self.send_header("retry-after", 1)
                    self.set_common_headers()
                    self.wfile.write("""{"ok": false, "error": "ratelimited"}""".encode("utf-8"))
                    return

            if self.is_valid_token() and self.is_valid_user_agent():
                self.send_response(HTTPStatus.OK)
                self.set_common_headers()
                self.wfile.close()
            else:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.set_common_headers()
                self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()
