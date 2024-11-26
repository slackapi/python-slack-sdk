import asyncio
from http.server import SimpleHTTPRequestHandler
from queue import Queue
import threading
import time
from typing import Type
from unittest import TestCase

from tests.mock_web_api_server.received_requests import ReceivedRequests
from tests.mock_web_api_server.mock_server_thread import MockServerThread


def setup_mock_web_api_server(test: TestCase, handler: Type[SimpleHTTPRequestHandler], port: int = 8888):
    test.server_started = threading.Event()
    test.received_requests = ReceivedRequests(Queue())
    test.thread = MockServerThread(queue=test.received_requests.queue, test=test, handler=handler, port=port)
    test.thread.start()
    test.server_started.wait()


def cleanup_mock_web_api_server(test: TestCase):
    test.thread.stop()
    test.thread = None


def assert_received_request_count(test: TestCase, path: str, min_count: int, timeout: float = 1):
    start_time = time.time()
    error = None
    while time.time() - start_time < timeout:
        try:
            received_count = test.received_requests.get(path, 0)
            assert (
                received_count == min_count
            ), f"Expected {min_count} '{path}' {'requests' if min_count > 1 else 'request'}, but got {received_count}!"
            return
        except Exception as e:
            error = e
            # waiting for some requests to be received
            time.sleep(0.05)

    if error is not None:
        raise error


def assert_auth_test_count(test: TestCase, expected_count: int):
    assert_received_request_count(test, "/auth.test", expected_count, 0.5)


#########
# async #
#########


def setup_mock_web_api_server_async(test: TestCase, handler: Type[SimpleHTTPRequestHandler], port: int = 8888):
    test.server_started = threading.Event()
    test.received_requests = ReceivedRequests(asyncio.Queue())
    test.thread = MockServerThread(queue=test.received_requests.queue, test=test, handler=handler, port=port)
    test.thread.start()
    test.server_started.wait()


def cleanup_mock_web_api_server_async(test: TestCase):
    test.thread.stop_unsafe()
    test.thread = None


async def assert_received_request_count_async(test: TestCase, path: str, min_count: int, timeout: float = 1):
    start_time = time.time()
    error = None
    while time.time() - start_time < timeout:
        try:
            received_count = await test.received_requests.get_async(path, 0)
            assert (
                received_count == min_count
            ), f"Expected {min_count} '{path}' {'requests' if min_count > 1 else 'request'}, but got {received_count}!"
            return
        except Exception as e:
            error = e
            # waiting for mock_received_requests updates
            await asyncio.sleep(0.05)

    if error is not None:
        raise error


async def assert_auth_test_count_async(test: TestCase, expected_count: int):
    await assert_received_request_count_async(test, "/auth.test", expected_count, 0.5)
