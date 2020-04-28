import platform
import sys
import warnings

import slack.version as ver


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


# https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api
deprecated_method_prefixes_2020_01 = ["channels.", "groups.", "im.", "mpim."]


def show_2020_01_deprecation(method_name: str):
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
