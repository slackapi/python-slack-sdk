import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/readme/sending_messages.py

import os
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

try:
    response = client.chat_postMessage(channel="#random", text="Hello world!")
    assert response["message"]["text"] == "Hello world!"
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
