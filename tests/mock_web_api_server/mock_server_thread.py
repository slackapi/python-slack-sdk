from asyncio import Queue
import asyncio
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
from typing import Type, Union
from unittest import TestCase


class MockServerThread(threading.Thread):
    def __init__(
        self, queue: Union[Queue, asyncio.Queue], test: TestCase, handler: Type[SimpleHTTPRequestHandler], port: int = 8888
    ):
        threading.Thread.__init__(self)
        self.handler = handler
        self.test = test
        self.queue = queue
        self.port = port

    def run(self):
        self.server = HTTPServer(("localhost", self.port), self.handler)
        self.server.queue = self.queue
        self.test.server_url = f"http://localhost:{str(self.port)}"
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
