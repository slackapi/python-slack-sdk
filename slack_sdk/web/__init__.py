"""The Slack Web API allows you to build applications that interact with Slack.

These applications can work in more complex ways than the integrations we provide out of the box.
"""

from .client import WebClient
from .slack_response import SlackResponse

__all__ = [
    "WebClient",
    "SlackResponse",
]
