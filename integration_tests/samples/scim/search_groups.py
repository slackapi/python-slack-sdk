import logging

logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk.scim import SCIMClient

client = SCIMClient(token=os.environ["SLACK_SDK_TEST_GRID_ORG_ADMIN_USER_TOKEN"])

response = client.search_groups(start_index=1, count=2)
print("-----------------------")
print(response.groups)
