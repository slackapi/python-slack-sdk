import sys
import logging

sys.path.insert(1, f"{__file__}/../../..")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# export SLACK_API_TOKEN=xoxb-***
# echo 'Hello world!' > tmp.txt
# python3 tests/samples/readme/uploading_files.py

import os
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_API_TOKEN'])

try:
    filepath="./tmp.txt"
    response = client.files_upload(
        channels='#random',
        file=filepath)
    assert response["file"]  # the uploaded file
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["ok"] is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
    print(f"Got an error: {e.response['error']}")
