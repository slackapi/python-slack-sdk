import unittest

from slack_sdk.http_retry import (
    FixedValueRetryIntervalCalculator,
    default_retry_handlers,
    all_builtin_retry_handlers,
)


class TestBuiltins(unittest.TestCase):
    def test_default_ones(self):
        list = default_retry_handlers()
        self.assertEqual(1, len(list))
        list.clear()
        self.assertEqual(0, len(list))
        list = default_retry_handlers()
        self.assertEqual(1, len(list))

        list = all_builtin_retry_handlers()
        self.assertEqual(2, len(list))
        list.clear()
        self.assertEqual(0, len(list))
        list = all_builtin_retry_handlers()
        self.assertEqual(2, len(list))

    def test_fixed_value_retry_interval_calculator(self):
        for fixed_value in [0.1, 0.2]:
            calculator = FixedValueRetryIntervalCalculator(fixed_internal=fixed_value)
            for i in range(10):
                self.assertEqual(fixed_value, calculator.calculate_sleep_duration(i))
