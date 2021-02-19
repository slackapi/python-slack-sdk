import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/emoji_reactions.py

import os
from slack_sdk.web import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

if __name__ == "__main__":
    channel_id = "#random"
    user_id = client.users_list()["members"][0]["id"]
else:
    channel_id = "C0XXXXXX"
    user_id = "U0XXXXXXX"

response = client.chat_postMessage(channel=channel_id, text="Give me some reaction!")
# Ensure the channel_id is not a name
channel_id = response["channel"]
ts = response["message"]["ts"]

response = client.reactions_add(channel=channel_id, name="thumbsup", timestamp=ts)

response = client.reactions_remove(channel=channel_id, name="thumbsup", timestamp=ts)
