import logging
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler


class MockHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    default_request_version = "HTTP/1.1"
    logger = logging.getLogger(__name__)
    state = {"request_count": 0}

    def set_common_headers(self):
        self.send_header("content-type", "application/json;charset=utf-8")
        self.send_header("connection", "close")
        self.end_headers()

    success_response = {"ok": True}

    def _handle(self):
        self.state["request_count"] += 1
        try:
            # put_nowait is common between Queue & asyncio.Queue, it does not need to be awaited
            self.server.queue.put_nowait(self.path)
            header = self.headers["authorization"]
            pattern = str(header).split("xoxb-", 1)[1]

            if self.state["request_count"] % 2 == 1:
                if "remote_disconnected" in pattern:
                    # http.client.RemoteDisconnected
                    self.finish()
                    return

            if pattern.isnumeric():
                self.send_response(int(pattern))
                self.set_common_headers()
                self.wfile.write("""{"ok":false}""".encode("utf-8"))
                return
            if pattern == "ratelimited":
                self.send_response(429)
                self.send_header("retry-after", 1)
                self.set_common_headers()
                self.wfile.write("""{"ok":false,"error":"ratelimited"}""".encode("utf-8"))
                self.wfile.close()
                return

            if pattern == "timeout":
                time.sleep(2)
                self.send_response(200)
                self.wfile.write("""{"ok":true}""".encode("utf-8"))
                self.wfile.close()
                return

            self.send_response(HTTPStatus.OK)
            self.set_common_headers()
            self.wfile.write("""{"ok":true}""".encode("utf-8"))
            self.wfile.close()

        except Exception as e:
            self.logger.error(str(e), exc_info=True)
            raise

    def do_GET(self):
        self._handle()

    def do_POST(self):
        self._handle()
