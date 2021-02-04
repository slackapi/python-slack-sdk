import json
import unittest

from slack_sdk.scim.v1.internal_utils import _to_snake_cased


class TEstInternals(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_snake_cased(self):
        response_body = """{"totalResults":441,"itemsPerPage":1,"startIndex":1,"schemas":["urn:scim:schemas:core:1.0"],"Resources":[{"schemas":["urn:scim:schemas:core:1.0"],"id":"W111","externalId":"","meta":{"created":"2020-08-13T04:15:35-07:00","location":"https://api.slack.com/scim/v1/Users/W111"},"userName":"test-app","nickName":"test-app","name":{"givenName":"","familyName":""},"displayName":"","profileUrl":"https://test-test-test.enterprise.slack.com/team/test-app","title":"","timezone":"America/Los_Angeles","active":true,"emails":[{"value":"botuser@slack-bots.com","primary":true}],"photos":[{"value":"https://secure.gravatar.com/avatar/xxx.jpg","type":"photo"}],"groups":[]}]}"""
        result = _to_snake_cased(json.loads(response_body))
        self.assertEqual(result["start_index"], 1)
        self.assertIsNotNone(result["resources"][0]["id"])
