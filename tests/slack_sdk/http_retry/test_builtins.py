import unittest

from slack_sdk.http_retry import FixedValueRetryIntervalCalculator
from tests.slack_sdk.audit_logs.mock_web_api_server import (
    cleanup_mock_web_api_server,
    setup_mock_web_api_server,
)


class TestBuiltins(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_fixed_value_retry_interval_calculator(self):
        for fixed_value in [0.1, 0.2]:
            calculator = FixedValueRetryIntervalCalculator(fixed_internal=fixed_value)
            for i in range(10):
                self.assertEqual(fixed_value, calculator.calculate_sleep_duration(i))
