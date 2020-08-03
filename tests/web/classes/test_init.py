import unittest

from slack.web.classes import extract_json
from slack.web.classes.objects import PlainTextObject, MarkdownTextObject


class TestInit(unittest.TestCase):
    def test_from_list_of_json_objects(self):
        json_objects = [
            PlainTextObject.from_str("foo"),
            MarkdownTextObject.from_str("bar"),
        ]
        output = extract_json(json_objects)
        expected = {
            "result": [
                {"type": "plain_text", "text": "foo", "emoji": True},
                {"type": "mrkdwn", "text": "bar"},
            ]
        }
        self.assertDictEqual(expected, {"result": output})

    def test_from_single_json_object(self):
        single_json_object = PlainTextObject.from_str("foo")
        output = extract_json(single_json_object)
        expected = {"result": {"type": "plain_text", "text": "foo", "emoji": True}}
        self.assertDictEqual(expected, {"result": output})
