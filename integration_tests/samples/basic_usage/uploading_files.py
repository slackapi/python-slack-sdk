import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# echo 'Hello world!' > tmp.txt
# python3 integration_tests/samples/basic_usage/uploading_files.py

import os
from slack_sdk.web import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

channels = ",".join(["#random"])
filepath = "./tmp.txt"
response = client.files_upload(channels=channels, file=filepath)
response = client.files_upload_v2(channel=response.get("file").get("channels")[0], file=filepath)
