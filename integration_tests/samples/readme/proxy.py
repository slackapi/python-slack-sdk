# ------------------
# Only for running this script here
import logging
import sys
from os.path import dirname

sys.path.insert(1, f"{dirname(__file__)}/../../..")
logging.basicConfig(level=logging.DEBUG)
# ------------------

# export SLACK_API_TOKEN=xoxb-***
# python3 integration_tests/samples/readme/proxy.py

import os
from slack import WebClient
from ssl import SSLContext

sslcert = SSLContext()
# pip3 install proxy.py
# proxy --port 9000 --log-level d
proxyinfo = "http://localhost:9000"

client = WebClient(
    token=os.environ['SLACK_API_TOKEN'],
    ssl=sslcert,
    proxy=proxyinfo
)
response = client.chat_postMessage(
    channel="#random",
    text="Hello World!")
print(response)
