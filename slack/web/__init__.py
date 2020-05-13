from typing import Dict


# ---------------------------------------


def _to_0_or_1_if_bool(v: any) -> str:
    if isinstance(v, bool):
        return "1" if v else "0"
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
    return None
