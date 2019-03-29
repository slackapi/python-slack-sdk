import logging
from logging import NullHandler

from slack.web.client import WebClient
from slack.rtm.client import RTMClient

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())


def web_client(token=None):
    return WebClient(token)


def rtm_client(token=None):
    return RTMClient(token)
