import unittest

from slack_sdk.socket_mode.logger.messages import debug_redacted_message_string


class TestRequest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_debug_redacted_message_string(self):
        message = """{"envelope_id":"abc-123","payload":{"token":"xxx","team_id":"T123","api_app_id":"A123","event":{"type":"function_executed","function":{"id":"Fn123","callback_id":"sample_function","title":"Sample function","description":"","type":"app","input_parameters":[],"output_parameters":[],"app_id":"A123","date_created":1719416102,"date_released":0,"date_updated":1719426759,"date_deleted":0,"form_enabled":false},"inputs":{"user_id":"U123"},"function_execution_id":"Fx123","workflow_execution_id":"Wx079QN9CT8E","event_ts":"1719427571.129426","bot_access_token":"xwfp-123-abc"},"type":"event_callback","event_id":"Ev123","event_time":1719427571},"type":"events_api","accepts_response_payload":false,"retry_attempt":0,"retry_reason":""}"""
        redacted_message = debug_redacted_message_string(message)
        self.assertEqual(redacted_message.count('"bot_access_token":[[REDACTED]]'), 1)

    def test_debug_redacted_message_string_no_changes(self):
        message = """{"envelope_id":"abc-123","payload":{"token":"xxx","team_id":"T123","api_app_id":"A123","event":{"type":"function_executed","function":{"id":"Fn123","callback_id":"sample_function","title":"Sample function","description":"","type":"app","input_parameters":[],"output_parameters":[],"app_id":"A123","date_created":1719416102,"date_released":0,"date_updated":1719426759,"date_deleted":0,"form_enabled":false},"inputs":{"user_id":"U123"},"function_execution_id":"Fx123","workflow_execution_id":"Wx079QN9CT8E","event_ts":"1719427571.129426"},"type":"event_callback","event_id":"Ev123","event_time":1719427571},"type":"events_api","accepts_response_payload":false,"retry_attempt":0,"retry_reason":""}"""
        redacted_message = debug_redacted_message_string(message)
        self.assertEqual(redacted_message.count('"bot_access_token":[[REDACTED]]'), 0)

    def test_debug_redacted_message_string_simple(self):
        message = '"bot_access_token": "xwfp-123-abc"'
        redacted_message = debug_redacted_message_string(message)
        self.assertEqual(redacted_message.count('"bot_access_token": [[REDACTED]]'), 1)
