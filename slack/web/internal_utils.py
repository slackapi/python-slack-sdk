import json
from typing import Union, Dict, List

from slack.errors import SlackRequestError
from slack.web.classes.attachments import Attachment
from slack.web.classes.blocks import Block


def _parse_web_class_objects(kwargs) -> None:
    def to_dict(obj: Union[Dict, Block, Attachment]):
        if isinstance(obj, Block):
            return obj.to_dict()
        if isinstance(obj, Attachment):
            return obj.to_dict()
        return obj

    blocks = kwargs.get("blocks", None)
    if blocks is not None and isinstance(blocks, list):
        dict_blocks = [to_dict(b) for b in blocks]
        kwargs.update({"blocks": dict_blocks})

    attachments = kwargs.get("attachments", None)
    if attachments is not None and isinstance(attachments, list):
        dict_attachments = [to_dict(a) for a in attachments]
        kwargs.update({"attachments": dict_attachments})


def _update_call_participants(kwargs, users: Union[str, List[Dict[str, str]]]):
    if users is None:
        return

    if isinstance(users, list):
        kwargs.update({"users": json.dumps(users)})
    elif isinstance(users, str):
        kwargs.update({"users": users})
    else:
        raise SlackRequestError("users must be either str or List[Dict[str, str]]")
