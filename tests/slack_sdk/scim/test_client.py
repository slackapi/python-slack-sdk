import time
import unittest

from slack_sdk.scim import SCIMClient, User, Group
from slack_sdk.scim.v1.group import GroupMember
from slack_sdk.scim.v1.user import UserName, UserEmail
from tests.slack_sdk.scim.mock_web_api_server import (
    setup_mock_web_api_server,
    cleanup_mock_web_api_server,
)


class TestSCIMClient(unittest.TestCase):
    def setUp(self):
        setup_mock_web_api_server(self)

    def tearDown(self):
        cleanup_mock_web_api_server(self)

    def test_users(self):
        client = SCIMClient(base_url="http://localhost:8888/", token="xoxp-valid")
        client.search_users(start_index=0, count=1)
        client.read_user("U111")

        now = str(time.time())[:10]
        user = User(
            user_name=f"user_{now}",
            name=UserName(given_name="Kaz", family_name="Sera"),
            emails=[UserEmail(value=f"seratch+{now}@example.com")],
            schemas=["urn:scim:schemas:core:1.0"],
        )
        client.create_user(user)
        # The mock server does not work for PATH requests
        try:
            client.patch_user("U111", partial_user=User(user_name="foo"))
        except:
            pass
        user.id = "U111"
        user.user_name = "updated"
        try:
            client.update_user(user)
        except:
            pass
        try:
            client.delete_user("U111")
        except:
            pass

    def test_groups(self):
        client = SCIMClient(base_url="http://localhost:8888/", token="xoxp-valid")
        client.search_groups(start_index=0, count=1)
        client.read_group("S111")

        now = str(time.time())[:10]
        group = Group(
            display_name=f"TestGroup_{now}",
            members=[GroupMember(value="U111")],
        )
        client.create_group(group)
        # The mock server does not work for PATH requests
        try:
            client.patch_group("S111", partial_group=Group(display_name=f"TestGroup_{now}_2"))
        except:
            pass
        group.id = "S111"
        group.display_name = "updated"
        try:
            client.update_group(group)
        except:
            pass
        try:
            client.delete_group("S111")
        except:
            pass
