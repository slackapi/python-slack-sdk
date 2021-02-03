from typing import Optional, Union

from .default_arg import DefaultArg, NotGiven
from .internal_utils import _to_dict_without_not_given


class TypeAndValue:
    primary: Union[Optional[bool], DefaultArg]
    type: Union[Optional[str], DefaultArg]
    value: Union[Optional[str], DefaultArg]

    def __init__(
        self,
        *,
        primary: Union[Optional[bool], DefaultArg] = NotGiven,
        type: Union[Optional[str], DefaultArg] = NotGiven,
        value: Union[Optional[str], DefaultArg] = NotGiven,
    ) -> None:
        self.primary = primary
        self.type = type
        self.value = value

    def to_dict(self) -> dict:
        return _to_dict_without_not_given(self)
