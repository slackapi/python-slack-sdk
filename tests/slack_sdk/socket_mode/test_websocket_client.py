import unittest
from unittest.mock import MagicMock

from websocket import WebSocketException

from slack_sdk.socket_mode.websocket_client import SocketModeClient


class TestWebSocketClientLibrary(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init_close(self):
        client = SocketModeClient(app_token="xapp-A111-222-xyz")
        try:
            self.assertIsNotNone(client)
            self.assertFalse(client.is_connected())
        finally:
            client.close()

    def test_send_message_raises_the_send_error_when_the_session_is_gone(self):
        client = SocketModeClient(app_token="xapp-A111-222-xyz")
        try:
            error = WebSocketException("connection replaced")
            client.current_session = MagicMock(sock=None, send=MagicMock(side_effect=error))
            with self.assertLogs(client.logger, level="WARNING"):
                with self.assertRaises(WebSocketException) as raised:
                    client.send_message("foo")
            self.assertIs(raised.exception, error)
        finally:
            client.current_session = None
            client.close()
