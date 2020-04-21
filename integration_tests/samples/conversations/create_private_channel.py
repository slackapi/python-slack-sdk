# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/conversations/create_private_channel.py

import os
from slack import WebClient
from time import time

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

channel_name = f"my-private-channel-{round(time())}"
response = client.conversations_create(
    name=channel_name,
    is_private=True
)
channel_id = response["channel"]["id"]

response = client.conversations_info(
    channel=channel_id,
    include_num_members=1  # TODO: True
)

response = client.conversations_members(channel=channel_id)
user_ids = response["members"]
print(f"user_ids: {user_ids}")

response = client.conversations_archive(channel=channel_id)
