import os
import warnings

from typing import Dict


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
            "For more info, go to "
            "https://api.slack.com/changelog/2020-01-deprecating-antecedents-to-the-conversations-api"
        )
        warnings.warn(message)
