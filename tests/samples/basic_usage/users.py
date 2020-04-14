import sys
import logging

sys.path.insert(1, f"{__file__}/../../..")
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# export SLACK_API_TOKEN=xoxb-***
# python3 tests/samples/basic_usage/users.py

import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

response = client.users_list()
