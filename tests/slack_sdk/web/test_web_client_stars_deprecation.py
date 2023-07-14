import os
import unittest
import pytest

from slack_sdk.web import WebClient
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    # You can enable this test to verify if the warning can be printed as expected
    @pytest.mark.skip()
    def test_stars_deprecation(self):
        env_value = os.environ.get("SLACKCLIENT_SKIP_DEPRECATION")
        try:
            os.environ.pop("SLACKCLIENT_SKIP_DEPRECATION")
            client = WebClient(base_url="http://localhost:8888")
            client.stars_list(token="xoxb-api_test")
        finally:
            if env_value is not None:
                os.environ.update({"SLACKCLIENT_SKIP_DEPRECATION": env_value})
