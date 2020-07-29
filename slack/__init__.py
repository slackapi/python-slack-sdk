import logging
from logging import NullHandler

from slack.web.client import WebClient  # noqa
from slack.web.async_client import AsyncWebClient  # noqa
from slack.rtm.client import RTMClient  # noqa
from slack.webhook.client import WebhookClient  # noqa
from slack.webhook.async_client import AsyncWebhookClient  # noqa

# Set default logging handler to avoid "No handler found" warnings.
logging.getLogger(__name__).addHandler(NullHandler())
