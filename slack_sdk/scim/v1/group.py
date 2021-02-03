from typing import Optional, List, Union

from .default_arg import DefaultArg, NotGiven
from .internal_utils import _to_dict_without_not_given, _is_iterable


class GroupMember:
    display: Union[Optional[str], DefaultArg]
    value: Union[Optional[str], DefaultArg]

    def __init__(
        self,
        *,
        display: Union[Optional[str], DefaultArg] = NotGiven,
        value: Union[Optional[str], DefaultArg] = NotGiven,
    ) -> None:
        self.display = display
        self.value = value

    def to_dict(self):
        return _to_dict_without_not_given(self)


class GroupMeta:
    created: Union[Optional[str], DefaultArg]
    location: Union[Optional[str], DefaultArg]

    def __init__(
        self,
        *,
        created: Union[Optional[str], DefaultArg] = NotGiven,
        location: Union[Optional[str], DefaultArg] = NotGiven,
    ) -> None:
        self.created = created
        self.location = location

    def to_dict(self):
        return _to_dict_without_not_given(self)


class Group:
    display_name: Union[Optional[str], DefaultArg]
    id: Union[Optional[str], DefaultArg]
    members: Union[Optional[List[GroupMember]], DefaultArg]
    meta: Union[Optional[GroupMeta], DefaultArg]
    schemas: Union[Optional[List[str]], DefaultArg]

    def __init__(
        self,
        *,
        display_name: Union[Optional[str], DefaultArg] = NotGiven,
        id: Union[Optional[str], DefaultArg] = NotGiven,
        members: Union[Optional[List[GroupMember]], DefaultArg] = NotGiven,
        meta: Union[Optional[GroupMeta], DefaultArg] = NotGiven,
        schemas: Union[Optional[List[str]], DefaultArg] = NotGiven,
    ) -> None:
        self.display_name = display_name
        self.id = id
        self.members = (
            [a if isinstance(a, GroupMember) else GroupMember(**a) for a in members]
            if _is_iterable(members)
            else members
        )
        self.meta = (
            GroupMeta(**meta) if meta is not None and isinstance(meta, dict) else meta
        )
        self.schemas = schemas

    def to_dict(self):
        return _to_dict_without_not_given(self)

    def __repr__(self):
        return f"<slack_sdk.scim.{self.__class__.__name__}: {self.to_dict()}>"
