import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# echo 'Hello world!' > tmp.txt
# python3 integration_tests/samples/readme/uploading_files.py

import os
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

try:
    filepath = "./tmp.txt"
    response = client.files_upload(channels="#random", file=filepath)
    assert response["file"]  # the uploaded file
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
