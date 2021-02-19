import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/channels.py

import os
from slack_sdk.web import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

response = client.conversations_list(exclude_archived=1)

channel_id = response["channels"][0]["id"]

response = client.conversations_info(channel=channel_id)

response = client.conversations_join(channel=channel_id)

response = client.conversations_leave(channel=channel_id)

response = client.conversations_join(channel=channel_id)
