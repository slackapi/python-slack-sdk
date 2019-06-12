import unittest
from typing import Any, Mapping

from slack.web.classes.elements import (
    ButtonElement,
    ImageElement,
)
from slack.web.classes.objects import ConfirmObject


def basic_json_structure(
    clazz: type, kwargs: Mapping[str, Any], attributes: Mapping[str, Any] = None
) -> bool:
    test_instance = clazz(**kwargs)
    tests = {**kwargs, **attributes}
    for attr, value in tests.items():
        if not getattr(test_instance, attr) == value:
            return False
    else:
        return True


class ButtonElementTests(unittest.TestCase):
    def test_json(self):
        self.assertTrue(
            basic_json_structure(
                clazz=ButtonElement,
                kwargs={
                    "text": "button text",
                    "action_id": "some_button",
                    "value": "button_123",
                    "style": None,
                    "confirm": None,
                },
                attributes={"type": "button"},
            )
        )
        self.assertTrue(
            basic_json_structure(
                clazz=ButtonElement,
                kwargs={
                    "text": "button text",
                    "action_id": "some_button",
                    "value": "button_123",
                    "style": "primary",
                    "confirm": ConfirmObject(
                        title="confirm_title", text="confirm_text"
                    ),
                },
                attributes={"type": "button"},
            )
        )


class ImageElementTests(unittest.TestCase):
    def test_json(self):
        self.assertTrue(
            basic_json_structure(
                clazz=ImageElement,
                kwargs={
                    "image_url": "http://google.com",
                    "alt_text": "not really an image",
                },
                attributes={"type": "image"},
            )
        )
