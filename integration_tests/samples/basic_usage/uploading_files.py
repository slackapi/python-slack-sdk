# ------------------
# Only for running this script here
from os.path import dirname
import sys
import logging

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# echo 'Hello world!' > tmp.txt
# python3 integration_tests/samples/basic_usage/uploading_files.py

import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

channels = ",".join(["#random"])
filepath = "./tmp.txt"
response = client.files_upload(channels=channels, file=filepath)
