import logging
import os
import unittest
from unittest.mock import Mock, patch
from threading import Lock

from slack_sdk.proxy_env_variable_loader import load_http_proxy_from_env
from slack_sdk.socket_mode.builtin.internals import _establish_new_socket_connection
from tests.helpers import remove_os_env_temporarily, restore_os_env


class TestProxyEnvVariableLoader(unittest.TestCase):
    def setUp(self):
        self.old_env = remove_os_env_temporarily()

    def tearDown(self):
        os.environ.clear()
        restore_os_env(self.old_env)

    def test_load_lower_case(self):
        os.environ["https_proxy"] = "http://localhost:9999"
        url = load_http_proxy_from_env()
        self.assertEqual(url, "http://localhost:9999")

    def test_load_upper_case(self):
        os.environ["HTTPS_PROXY"] = "http://localhost:9999"
        url = load_http_proxy_from_env()
        self.assertEqual(url, "http://localhost:9999")

    def test_load_all_empty_case(self):
        os.environ["HTTP_PROXY"] = ""
        os.environ["http_proxy"] = ""
        os.environ["HTTPS_PROXY"] = ""
        os.environ["https_proxy"] = ""
        url = load_http_proxy_from_env()
        self.assertEqual(url, None)

    def test_proxy_url_is_none_case(self):
        os.environ.pop("HTTPS_PROXY", None)
        os.environ.pop("https_proxy", None)
        os.environ.pop("HTTP_PROXY", None)
        os.environ.pop("http_proxy", None)
        url = load_http_proxy_from_env()
        self.assertEqual(url, None)

    def test_credentials_are_not_logged(self):
        os.environ["HTTPS_PROXY"] = "http://bob:secret@example.com:8080"
        logger = logging.getLogger("test_proxy_env_variable_loader")
        with self.assertLogs(logger, level="DEBUG") as logs:
            url = load_http_proxy_from_env(logger)
        # the proxy URL itself is returned unchanged
        self.assertEqual(url, "http://bob:secret@example.com:8080")
        output = "\n".join(logs.output)
        self.assertNotIn("bob", output)
        self.assertNotIn("secret", output)
        self.assertIn("http://***@example.com:8080", output)

    def test_url_without_credentials_is_logged_as_is(self):
        os.environ["HTTPS_PROXY"] = "http://localhost:9999"
        logger = logging.getLogger("test_proxy_env_variable_loader")
        with self.assertLogs(logger, level="DEBUG") as logs:
            load_http_proxy_from_env(logger)
        self.assertIn("http://localhost:9999", "\n".join(logs.output))

    def test_credentials_in_unusual_proxy_urls_are_not_logged(self):
        for value in (
            "bob:secret@proxy.example.com:3128",
            "http://bob:pa/ss@proxy.example.com:3128",
            "http://bob:pa#ss@proxy.example.com:3128",
            "http://bob:pa?ss@proxy.example.com:3128",
            "http://token@proxy.example.com:3128",
            "http://bob:pa@ss@proxy.example.com:3128",
        ):
            with self.subTest(value=value):
                os.environ["HTTPS_PROXY"] = value
                logger = logging.getLogger("test_proxy_env_variable_loader")
                with self.assertLogs(logger, level="DEBUG") as logs:
                    self.assertEqual(load_http_proxy_from_env(logger), value)
                expected = (
                    "http://***@proxy.example.com:3128" if value.startswith("http://") else "***@proxy.example.com:3128"
                )
                self.assertEqual(
                    logs.records[0].getMessage(), "HTTP proxy URL has been loaded from an env variable: " + expected
                )

    def test_unparsable_proxy_url_is_not_logged(self):
        os.environ["HTTPS_PROXY"] = "http://[invalid"
        logger = logging.getLogger("test_proxy_env_variable_loader")
        with self.assertLogs(logger, level="DEBUG") as logs:
            self.assertEqual(load_http_proxy_from_env(logger), "http://[invalid")
        self.assertIn("(unparsable URL)", logs.output[0])
        self.assertNotIn("[invalid", logs.output[0])

    def test_socket_mode_proxy_error_redacts_credentials(self):
        with patch("slack_sdk.socket_mode.builtin.internals.socket.create_connection"), patch(
            "slack_sdk.socket_mode.builtin.internals._parse_connect_response",
            return_value=(407, "Proxy Authentication Required"),
        ):
            with self.assertRaises(Exception) as error:
                _establish_new_socket_connection(
                    session_id="test",
                    server_hostname="example.com",
                    server_port=443,
                    logger=Mock(),
                    sock_send_lock=Lock(),
                    receive_timeout=1,
                    proxy="http://bob:secret@proxy.example.com:3128",
                    proxy_headers=None,
                    trace_enabled=False,
                    ssl_context=Mock(),
                )
        self.assertNotIn("bob", str(error.exception))
        self.assertNotIn("secret", str(error.exception))
        self.assertIn("http://***@proxy.example.com:3128", str(error.exception))
        self.assertIn("407", str(error.exception))
