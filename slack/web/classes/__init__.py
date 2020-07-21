import logging
from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import Callable, Iterable, List, Set, Union, Dict, Any

from ...errors import SlackObjectFormationError


class BaseObject:
    def __str__(self):
        return f"<slack.{self.__class__.__name__}>"


class JsonObject(BaseObject, metaclass=ABCMeta):
    @property
    @abstractmethod
    def attributes(self) -> Set[str]:
        """Provide a set of attributes of this object that will make up its JSON structure"""
        return set()

    def validate_json(self) -> None:
        """
        Raises:
          SlackObjectFormationError if the object was not valid
        """
        for attribute in (func for func in dir(self) if not func.startswith("__")):
            method = getattr(self, attribute, None)
            if callable(method) and hasattr(method, "validator"):
                method()

    def get_non_null_attributes(self) -> dict:
        """
        Construct a dictionary out of non-null keys (from attributes property)
        present on this object
        """

        def to_dict_compatible(value: Union[dict, list, object]) -> Union[dict, list]:
            if isinstance(value, list):  # skipcq: PYL-R1705
                return [to_dict_compatible(v) for v in value]
            else:
                to_dict = getattr(value, "to_dict", None)
                if to_dict and callable(to_dict):  # skipcq: PYL-R1705
                    return {
                        k: to_dict_compatible(v) for k, v in value.to_dict().items()
                    }
                else:
                    return value

        def is_not_empty(self, key: str) -> bool:
            value = getattr(self, key, None)
            if value is None:
                return False
            has_len = getattr(value, "__len__", None) is not None
            if has_len:  # skipcq: PYL-R1705
                return len(value) > 0
            else:
                return value is not None

        return {
            key: to_dict_compatible(getattr(self, key, None))
            for key in sorted(self.attributes)
            if is_not_empty(self, key)
        }

    def to_dict(self, *args) -> dict:
        """
        Extract this object as a JSON-compatible, Slack-API-valid dictionary

        Args:
          *args: Any specific formatting args (rare; generally not required)

        Raises:
          SlackObjectFormationError if the object was not valid
        """
        self.validate_json()
        return self.get_non_null_attributes()

    def __repr__(self):
        dict_value = self.get_non_null_attributes()
        if dict_value:  # skipcq: PYL-R1705
            return f"<slack.{self.__class__.__name__}: {dict_value}>"
        else:
            return self.__str__()


class JsonValidator:
    def __init__(self, message: str):
        """
        Decorate a method on a class to mark it as a JSON validator. Validation
            functions should return true if valid, false if not.

        Args:
            message: Message to be attached to the thrown SlackObjectFormationError
        """
        self.message = message

    def __call__(self, func: Callable) -> Callable[..., None]:
        @wraps(func)
        def wrapped_f(*args, **kwargs):
            if not func(*args, **kwargs):
                raise SlackObjectFormationError(self.message)

        wrapped_f.validator = True
        return wrapped_f


class EnumValidator(JsonValidator):
    def __init__(self, attribute: str, enum: Iterable[str]):
        super().__init__(
            f"{attribute} attribute must be one of the following values: "
            f"{', '.join(enum)}"
        )


# NOTE: used only for legacy components - don't use this for Block Kit
def extract_json(
    item_or_items: Union[JsonObject, List[JsonObject]], *format_args
) -> Union[Dict[Any, Any], List[Dict[Any, Any]]]:
    """
    Given a sequence (or single item), attempt to call the to_dict() method on each
    item and return a plain list. If item is not the expected type, return it
    unmodified, in case it's already a plain dict or some other user created class.

    Args:
      item_or_items: item(s) to go through
      format_args: Any formatting specifiers to pass into the object's to_dict
            method
    """
    try:
        return [
            elem.to_dict(*format_args) if isinstance(elem, JsonObject) else elem
            for elem in item_or_items
        ]
    except TypeError:  # not iterable, so try returning it as a single item
        return (
            item_or_items.to_dict(*format_args)
            if isinstance(item_or_items, JsonObject)
            else item_or_items
        )


def show_unknown_key_warning(name: Union[str, object], others: dict):
    """Prints a warning message if the given 'others' is not empty.

    :param name: the object's name
    :param others: unknown fields
    :return: None
    """
    if "type" in others:
        others.pop("type")
    if len(others) > 0:
        keys = ", ".join(others.keys())
        logger = logging.getLogger(__name__)
        if isinstance(name, object):
            name = name.__class__.__name__
        logger.debug(
            f"!!! {name}'s constructor args ({keys}) were ignored."
            f"If they should be supported by this library, report this issue to the project :bow: "
            f"https://github.com/slackapi/python-slackclient/issues"
        )
