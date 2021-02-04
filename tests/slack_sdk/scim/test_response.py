import json
import unittest

from slack_sdk.scim import SearchUsersResponse, SCIMResponse
from slack_sdk.scim.v1.internal_utils import _to_snake_cased


class TEstInternals(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_snake_cased(self):
        response_body = """{
  "totalResults": 441,
  "itemsPerPage": 1,
  "startIndex": 1,
  "schemas": [
    "urn:scim:schemas:core:1.0"
  ],
  "Resources": [
    {
      "schemas": [
        "urn:scim:schemas:core:1.0"
      ],
      "id": "W111",
      "externalId": "",
      "meta": {
        "created": "2020-08-13T04:15:35-07:00",
        "location": "https://api.slack.com/scim/v1/Users/W111",
        "newAttribute": "this should be just accepted as unknown attribute"
      },
      "userName": "test-app",
      "nickName": "test-app",
      "name": {
        "givenName": "",
        "familyName": "",
        "newAttribute": "this should be just accepted as unknown attribute"
      },
      "displayName": "",
      "profileUrl": "https://test-test-test.enterprise.slack.com/team/test-app",
      "title": "",
      "timezone": "America/Los_Angeles",
      "active": true,
      "emails": [
        {
          "value": "botuser@slack-bots.com",
          "primary": true,
          "newAttribute": "this should be just accepted as unknown attribute"
        }
      ],
      "photos": [
        {
          "value": "https://secure.gravatar.com/avatar/xxx.jpg",
          "type": "photo",
          "newAttribute": "this should be just accepted as unknown attribute"
        }
      ],
      "groups": [],
      "newAttribute": "this should be just accepted as unknown attribute"
    }
  ],
  "newAttribute": "this should be just accepted as unknown attribute"
}
"""
        response = SearchUsersResponse(
            SCIMResponse(
                url="https://www.example.com",
                status_code=200,
                raw_body=response_body,
                headers={},
            )
        )
        user = response.users[0]
        self.assertIsNotNone(user.unknown_fields.get("new_attribute"))
        # the unknown fields need to be also camel-cased
        self.assertIsNotNone(user.to_dict().get("newAttribute"))
