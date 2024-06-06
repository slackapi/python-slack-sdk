import unittest
import pytest

from slack_sdk.web import WebClient
from tests.helpers import remove_os_env_temporarily, restore_os_env
from tests.slack_sdk.web.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestWebClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)
        self.env_values = remove_os_env_temporarily()

    def tearDown(self):
        cleanup_mock_web_api_server(self)
        restore_os_env(self.env_values)

    # You can enable this test to verify if the warning can be printed as expected
    @pytest.mark.skip()
    def test_workflow_step_completed_deprecation(self):
        client = WebClient(base_url="http://localhost:8888")
        client.workflows_stepCompleted(token="xoxb-api_test", workflow_step_execute_id="W1234")

    @pytest.mark.skip()
    def test_workflow_step_failed_deprecation(self):
        client = WebClient(base_url="http://localhost:8888")
        client.workflows_stepFailed(token="xoxb-api_test", workflow_step_execute_id="W1234", error={})

    @pytest.mark.skip()
    def test_workflow_update_step_deprecation(self):
        client = WebClient(base_url="http://localhost:8888")
        client.workflows_updateStep(token="xoxb-api_test", workflow_step_edit_id="W1234", inputs={}, outputs={})
