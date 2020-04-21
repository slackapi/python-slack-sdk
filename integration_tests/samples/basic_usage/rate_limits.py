# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/rate_limits.py

import os
import time
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_API_TOKEN"])


# Simple wrapper for sending a Slack message
def send_slack_message(channel, message):
    return client.chat_postMessage(
        channel=channel,
        text=message
    )


# Make the API call and save results to `response`
channel = "#random"
message = "Hello, from Python!"

# Do until being rate limited
while True:
    try:
        response = send_slack_message(channel, message)
    except SlackApiError as e:
        if e.response["error"] == "ratelimited":
            # The `Retry-After` header will tell you how long to wait before retrying
            delay = int(e.response.headers['Retry-After'])
            print(f"Rate limited. Retrying in {delay} seconds")
            time.sleep(delay)
            response = send_slack_message(channel, message)
        else:
            # other errors
            raise e
