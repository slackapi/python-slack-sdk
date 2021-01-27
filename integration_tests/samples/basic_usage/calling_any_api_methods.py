# ------------------
# Only for running this script here
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
# ------------------

import logging

logging.basicConfig(level=logging.DEBUG)

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/calling_any_api_methods.py

import os
from slack_sdk.web import WebClient

client = WebClient(token=os.environ['SLACK_API_TOKEN'])
response = client.api_call(
  api_method='chat.postMessage',
  json={'channel': '#random','text': "Hello world!"}
)
assert response["message"]["text"] == "Hello world!"