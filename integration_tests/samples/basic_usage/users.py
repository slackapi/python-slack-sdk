# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/basic_usage/users.py

import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

response = client.users_list()
