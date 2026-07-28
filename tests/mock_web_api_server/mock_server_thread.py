import asyncio
import logging
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue
from typing import Optional, Type, Union
from unittest import TestCase

logger = logging.getLogger(__name__)


class MockServerThread(threading.Thread):
    def __init__(
        self,
        test: TestCase,
        handler: Type[SimpleHTTPRequestHandler],
        queue: Optional[Union[Queue, asyncio.Queue]] = None,
        port: int = 8888,
    ):
        threading.Thread.__init__(self, daemon=True)
        self.handler = handler
        self.test = test
        self.queue = queue
        self.port = port

    def run(self):
        self.server = ThreadingHTTPServer(("localhost", self.port), self.handler)
        if self.queue is not None:
            self.server.queue = self.queue
        self.test.server_url = f"http://localhost:{self.port}"
        self.test.host, self.test.port = self.server.socket.getsockname()
        self.test.server_started.set()  # threading.Event()

        self.test = None
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()
        self.join(timeout=5)
        if self.is_alive():
            logger.warning(f"Mock web API server thread on port {self.port} did not stop within 5s")
        if getattr(self.server, "queue", None) is not None:
            del self.server.queue
