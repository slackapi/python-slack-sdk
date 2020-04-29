import os
import platform
import sys
import warnings
from typing import Dict

import slack.version as ver


# ---------------------------------------


def get_user_agent():
    """Construct the user-agent header with the package info,
    Python version and OS version.

    Returns:
        The user agent string.
        e.g. 'Python/3.6.7 slackclient/2.0.0 Darwin/17.7.0'
    """
    # __name__ returns all classes, we only want the client
    client = "{0}/{1}".format("slackclient", ver.__version__)
    python_version = "Python/{v.major}.{v.minor}.{v.micro}".format(v=sys.version_info)
    system_info = "{0}/{1}".format(platform.system(), platform.release())
    user_agent_string = " ".join([python_version, client, system_info])
    return user_agent_string


# ---------------------------------------


def _to_0_or_1_if_bool(v: any) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
    else:
        return v


def convert_bool_to_0_or_1(params: Dict[str, any]) -> Dict[str, any]:
    """Converts all bool values in dict to "0" or "1".

    Slack APIs safely accept "0"/"1" as boolean values.
    Using True/False (bool in Python) doesn't work with aiohttp.
    This method converts only the bool values in top-level of a given dict.

    :param params: params as a dict
    :return: return modified dict
    """
    if params:
        return {k: _to_0_or_1_if_bool(v) for k, v in params.items()}
    else:
        return None


# ---------------------------------------

# https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api
deprecated_method_prefixes_2020_01 = ["channels.", "groups.", "im.", "mpim."]


def show_2020_01_deprecation(method_name: str):
    skip_deprecation = os.environ.get(
        "SLACKCLIENT_SKIP_DEPRECATION"
    )  # for unit tests etc.
    if skip_deprecation:
        return
    if not method_name:
        return

    matched_prefixes = [
        prefix
        for prefix in deprecated_method_prefixes_2020_01
        if method_name.startswith(prefix)
    ]
    if len(matched_prefixes) > 0:
        message = (
            f"{method_name} is deprecated. Please use the Conversations API instead. "
            f"For more info, go to "
            f"https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api"
        )
        warnings.warn(message)
