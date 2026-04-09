import logging
import ssl
import unittest
from threading import Lock
from unittest.mock import patch, MagicMock, create_autospec

from slack_sdk.socket_mode.client import BaseSocketModeClient
from slack_sdk.socket_mode.builtin.internals import (
    _parse_handshake_response,
    _fetch_messages,
)


class TestSocketModeClient(unittest.TestCase):
    logger = logging.getLogger(__name__)

    def test_connect_to_new_endpoint_does_not_release_lock_on_acquisition_timeout(self):
        client = BaseSocketModeClient.__new__(BaseSocketModeClient)
        client.logger = self.logger
        client.connect_operation_lock = create_autospec(Lock(), acquire=MagicMock(return_value=False))

        client.connect_to_new_endpoint()

        client.connect_operation_lock.release.assert_not_called()

    def test_connect_to_new_endpoint_releases_lock_on_successful_acquisition(self):
        client = BaseSocketModeClient.__new__(BaseSocketModeClient)
        client.logger = self.logger
        client.connect_operation_lock = Lock()

        with patch.object(client, client.is_connected.__name__, return_value=True):
            client.connect_to_new_endpoint()

        acquired = client.connect_operation_lock.acquire(blocking=False)
        self.assertTrue(acquired)
        client.connect_operation_lock.release()

    def test_parse_handshake_response_preserves_colons_in_header_values(self):
        lines = [
            "HTTP/1.1 101 Switching Protocols",
            "Upgrade: websocket",
            "Location: https://example.com:8080/path",
            "",
        ]
        with patch(
            "slack_sdk.socket_mode.builtin.internals._read_http_response_line",
            side_effect=lines,
        ):
            status, headers, _ = _parse_handshake_response(MagicMock(spec=ssl.SSLSocket))

        self.assertEqual(status, 101)
        self.assertEqual(headers["upgrade"], "websocket")
        self.assertEqual(headers["location"], "https://example.com:8080/path")

    def test_parse_handshake_response_parses_standard_headers(self):
        lines = [
            "HTTP/1.1 200 OK",
            "Content-Type: text/html",
            "",
        ]
        with patch(
            "slack_sdk.socket_mode.builtin.internals._read_http_response_line",
            side_effect=lines,
        ):
            status, headers, _ = _parse_handshake_response(MagicMock(spec=ssl.SSLSocket))

        self.assertEqual(status, 200)
        self.assertEqual(headers["content-type"], "text/html")
