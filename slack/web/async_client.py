# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#
#  *** DO NOT EDIT THIS FILE ***
#
#  1) Modify slack/web/client.py
#  2) Run `python scripts/codegen.py`
#  3) Run `black slack_sdk/`
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

from slack import deprecation
from slack_sdk.web.legacy_client import LegacyWebClient as WebClient  # noqa
from slack_sdk.web.async_client import AsyncWebClient  # noqa
from slack_sdk.web.async_client import AsyncSlackResponse  # noqa

deprecation.show_message(__name__, "slack_sdk.web.client")
