import unittest

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
