import json
import logging
import unittest

from slack.errors import SlackObjectFormationError
from slack.web.classes.blocks import InputBlock, SectionBlock, DividerBlock, ActionsBlock, ContextBlock
from slack.web.classes.elements import PlainTextInputElement, RadioButtonsElement, CheckboxesElement, ButtonElement, \
    ImageElement
from slack.web.classes.objects import PlainTextObject, Option, MarkdownTextObject
from slack.web.classes.views import View, ViewState, ViewStateValue


class ViewTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.logger = logging.getLogger(__name__)

    def verify_loaded_view_object(self, file):
        input = json.load(file)
        view = View(**input)
        self.assertDictEqual(input, view.to_dict())

    # --------------------------------
    # Modals
    # --------------------------------

    def test_valid_construction(self):
        modal_view = View(
            type="modal",
            callback_id="modal-id",
            title=PlainTextObject(text="Awesome Modal"),
            submit=PlainTextObject(text="Submit"),
            close=PlainTextObject(text="Cancel"),
            blocks=[
                InputBlock(
                    block_id="b-id",
                    label=PlainTextObject(text="Input label"),
                    element=PlainTextInputElement(action_id="a-id")
                ),
                InputBlock(
                    block_id="cb-id",
                    label=PlainTextObject(text="Label"),
                    element=CheckboxesElement(
                        action_id="a-cb-id",
                        options=[
                            Option(text=PlainTextObject(text="*this is plain_text text*"), value="v1"),
                            Option(text=MarkdownTextObject(text="*this is mrkdwn text*"), value="v2"),
                        ],
                    ),
                ),
                SectionBlock(
                    block_id="sb-id",
                    text=MarkdownTextObject(text="This is a mrkdwn text section block."),
                    fields=[
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                        MarkdownTextObject(text="*this is mrkdwn text*"),
                        PlainTextObject(text="*this is plain_text text*", emoji=True),
                    ]
                ),
                DividerBlock(),
                SectionBlock(
                    block_id="rb-id",
                    text=MarkdownTextObject(text="This is a section block with radio button accessory"),
                    accessory=RadioButtonsElement(
                        initial_option=Option(
                            text=PlainTextObject(text="Option 1"),
                            value="option 1",
                            description=PlainTextObject(text="Description for option 1"),
                        ),
                        options=[
                            Option(
                                text=PlainTextObject(text="Option 1"),
                                value="option 1",
                                description=PlainTextObject(text="Description for option 1"),
                            ),
                            Option(
                                text=PlainTextObject(text="Option 2"),
                                value="option 2",
                                description=PlainTextObject(text="Description for option 2"),
                            ),
                        ]
                    )
                )
            ]
        )
        modal_view.validate_json()

    def test_invalid_type_value(self):
        modal_view = View(
            type="modallll",
            callback_id="modal-id",
            title=PlainTextObject(text="Awesome Modal"),
            submit=PlainTextObject(text="Submit"),
            close=PlainTextObject(text="Cancel"),
            blocks=[
                InputBlock(
                    block_id="b-id",
                    label=PlainTextObject(text="Input label"),
                    element=PlainTextInputElement(action_id="a-id")
                ),
            ]
        )
        with self.assertRaises(SlackObjectFormationError):
            modal_view.validate_json()

    def test_simple_state_values(self):
        expected = {
            "values": {
                "b1": {
                    "a1": {
                        "type": "plain_text_input",
                        "value": "Title"
                    }
                },
                "b2": {
                    "a2": {
                        "type": "plain_text_input",
                        "value": "Description"
                    }
                }
            }
        }
        state = ViewState(values={
            "b1": {
                "a1": ViewStateValue(
                    type="plain_text_input",
                    value="Title"
                )
            },
            "b2": {
                "a2": {
                    "type": "plain_text_input",
                    "value": "Description"
                }
            },
        })
        self.assertDictEqual(expected, ViewState(**expected).to_dict())
        self.assertDictEqual(expected, state.to_dict())

    def test_all_state_values(self):
        # Testing with
        # {"type":"modal","title":{"type":"plain_text","text":"My App","emoji":true},"submit":{"type":"plain_text","text":"Submit","emoji":true},"close":{"type":"plain_text","text":"Cancel","emoji":true},"blocks":[{"type":"input","element":{"type":"plain_text_input"},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"plain_text_input","multiline":true},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"datepicker","initial_date":"1990-04-28","placeholder":{"type":"plain_text","text":"Select a date","emoji":true}},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"users_select","placeholder":{"type":"plain_text","text":"Select a user","emoji":true}},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"multi_static_select","placeholder":{"type":"plain_text","text":"Select options","emoji":true},"options":[{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-0"},{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-1"},{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-2"}]},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"checkboxes","options":[{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-0"},{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-1"},{"text":{"type":"plain_text","text":"*this is plain_text text*","emoji":true},"value":"value-2"}]},"label":{"type":"plain_text","text":"Label","emoji":true}},{"type":"input","element":{"type":"radio_buttons","initial_option":{"text":{"type":"plain_text","text":"Option 1"},"value":"option 1","description":{"type":"plain_text","text":"Description for option 1"}},"options":[{"text":{"type":"plain_text","text":"Option 1"},"value":"option 1","description":{"type":"plain_text","text":"Description for option 1"}},{"text":{"type":"plain_text","text":"Option 2"},"value":"option 2","description":{"type":"plain_text","text":"Description for option 2"}},{"text":{"type":"plain_text","text":"Option 3"},"value":"option 3","description":{"type":"plain_text","text":"Description for option 3"}}]},"label":{"type":"plain_text","text":"Label","emoji":true}}]}
        expected = {
            "values": {
                "b1": {
                    "a1": {
                        "type": "datepicker",
                        "selected_date": "1990-04-12"
                    }
                },
                "b2": {
                    "a2": {
                        "type": "plain_text_input",
                        "value": "This is a test"
                    }
                },
                # multiline
                "b3": {
                    "a3": {
                        "type": "plain_text_input",
                        "value": "Something wrong\nPlease help me!"
                    }
                },
                "b4": {
                    "a4": {
                        "type": "users_select",
                        "selected_user": "U123"
                    }
                },
                "b4-2": {
                    "a4-2": {
                        "type": "multi_users_select",
                        "selected_users": ["U123", "U234"]
                    }
                },
                "b5": {
                    "a5": {
                        "type": "conversations_select",
                        "selected_conversation": "C123"
                    }
                },
                "b5-2": {
                    "a5-2": {
                        "type": "multi_conversations_select",
                        "selected_conversations": ["C123", "C234"]
                    }
                },
                "b6": {
                    "a6": {
                        "type": "channels_select",
                        "selected_channel": "C123"
                    }
                },
                "b6-2": {
                    "a6-2": {
                        "type": "multi_channels_select",
                        "selected_channels": ["C123", "C234"]
                    }
                },
                "b7": {
                    "a7": {
                        "type": "multi_static_select",
                        "selected_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*this is plain_text text*",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*this is plain_text text*",
                                    "emoji": True
                                },
                                "value": "value-1"
                            }
                        ]
                    }
                },
                "b8": {
                    "a8": {
                        "type": "checkboxes",
                        "selected_options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*this is plain_text text*",
                                    "emoji": True
                                },
                                "value": "value-0"
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "*this is plain_text text*",
                                    "emoji": True
                                },
                                "value": "value-1"
                            }
                        ]
                    }
                },
                "b9": {
                    "a9": {
                        "type": "radio_buttons",
                        "selected_option": {
                            "text": {
                                "type": "plain_text",
                                "text": "Option 1",
                                "emoji": True
                            },
                            "value": "option 1",
                            "description": {
                                "type": "plain_text",
                                "text": "Description for option 1",
                                "emoji": True
                            }
                        }
                    }
                }
            }
        }
        state = ViewState(values={
            "b1": {"a1": ViewStateValue(type="datepicker", selected_date="1990-04-12")},
            "b2": {"a2": ViewStateValue(type="plain_text_input", value="This is a test")},
            "b3": {"a3": ViewStateValue(type="plain_text_input", value="Something wrong\nPlease help me!")},
            "b4": {"a4": ViewStateValue(type="users_select", selected_user="U123")},
            "b4-2": {"a4-2": ViewStateValue(type="multi_users_select", selected_users=["U123", "U234"])},
            "b5": {"a5": ViewStateValue(type="conversations_select", selected_conversation="C123")},
            "b5-2": {"a5-2": ViewStateValue(
                type="multi_conversations_select",
                selected_conversations=["C123", "C234"]
            )},
            "b6": {"a6": ViewStateValue(type="channels_select", selected_channel="C123")},
            "b6-2": {"a6-2": ViewStateValue(type="multi_channels_select", selected_channels=["C123", "C234"])},
            "b7": {"a7": ViewStateValue(type="multi_static_select", selected_options=[
                Option(
                    text=PlainTextObject(text="*this is plain_text text*", emoji=True),
                    value="value-0"
                ),
                Option(
                    text=PlainTextObject(text="*this is plain_text text*", emoji=True),
                    value="value-1"
                ),
            ])},
            "b8": {"a8": ViewStateValue(type="checkboxes", selected_options=[
                Option(
                    text=PlainTextObject(text="*this is plain_text text*", emoji=True),
                    value="value-0"
                ),
                Option(
                    text=PlainTextObject(text="*this is plain_text text*", emoji=True),
                    value="value-1"
                ),
            ])},
            "b9": {"a9": ViewStateValue(
                type="radio_buttons",
                selected_option=Option(
                    text=PlainTextObject(text="Option 1", emoji=True),
                    value="option 1",
                    description=PlainTextObject(text="Description for option 1", emoji=True)
                )
            )},
        })
        self.assertDictEqual(expected, ViewState(**expected).to_dict())
        self.assertDictEqual(expected, state.to_dict())

    def test_load_modal_view_001(self):
        with open("tests/data/view_modal_001.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_002(self):
        with open("tests/data/view_modal_002.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_003(self):
        with open("tests/data/view_modal_003.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_004(self):
        with open("tests/data/view_modal_004.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_005(self):
        with open("tests/data/view_modal_005.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_006(self):
        with open("tests/data/view_modal_006.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_007(self):
        with open("tests/data/view_modal_007.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_008(self):
        with open("tests/data/view_modal_008.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_009(self):
        with open("tests/data/view_modal_009.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_modal_view_010(self):
        with open("tests/data/view_modal_010.json") as file:
            self.verify_loaded_view_object(file)

    # --------------------------------
    # Home Tabs
    # --------------------------------

    def test_home_tab_construction(self):
        home_tab_view = View(
            type="home",
            blocks=[
                SectionBlock(
                    text=MarkdownTextObject(text="*Here's what you can do with Project Tracker:*"),
                ),
                ActionsBlock(
                    elements=[
                        ButtonElement(
                            text=PlainTextObject(text="Create New Task", emoji=True),
                            style="primary",
                            value="create_task",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Create New Project", emoji=True),
                            value="create_project",
                        ),
                        ButtonElement(
                            text=PlainTextObject(text="Help", emoji=True),
                            value="help",
                        ),
                    ],
                ),
                ContextBlock(
                    elements=[
                        ImageElement(
                            image_url="https://api.slack.com/img/blocks/bkb_template_images/placeholder.png",
                            alt_text="placeholder",
                        ),
                    ],
                ),
                SectionBlock(
                    text=MarkdownTextObject(text="*Your Configurations*"),
                ),
                DividerBlock(),
                SectionBlock(
                    text=MarkdownTextObject(
                        text="*#public-relations*\n<fakelink.toUrl.com|PR Strategy 2019> posts new tasks, comments, and project updates to <fakelink.toChannel.com|#public-relations>"),
                    accessory=ButtonElement(
                        text=PlainTextObject(text="Edit", emoji=True),
                        value="public-relations",
                    ),
                )
            ],
        )
        home_tab_view.validate_json()

    def test_input_blocks_in_home_tab(self):
        modal_view = View(
            type="home",
            callback_id="home-tab-id",
            blocks=[
                InputBlock(
                    block_id="b-id",
                    label=PlainTextObject(text="Input label"),
                    element=PlainTextInputElement(action_id="a-id")
                ),
            ]
        )
        with self.assertRaises(SlackObjectFormationError):
            modal_view.validate_json()

    def test_submit_in_home_tab(self):
        modal_view = View(
            type="home",
            callback_id="home-tab-id",
            submit=PlainTextObject(text="Submit"),
            blocks=[DividerBlock()]
        )
        with self.assertRaises(SlackObjectFormationError):
            modal_view.validate_json()

    def test_close_in_home_tab(self):
        modal_view = View(
            type="home",
            callback_id="home-tab-id",
            close=PlainTextObject(text="Cancel"),
            blocks=[DividerBlock()]
        )
        with self.assertRaises(SlackObjectFormationError):
            modal_view.validate_json()

    def test_load_home_tab_view_001(self):
        with open("tests/data/view_home_001.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_home_tab_view_002(self):
        with open("tests/data/view_home_002.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_home_tab_view_003(self):
        with open("tests/data/view_home_003.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_home_tab_view_004(self):
        with open("tests/data/view_home_004.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_home_tab_view_005(self):
        with open("tests/data/view_home_005.json") as file:
            self.verify_loaded_view_object(file)

    def test_load_home_tab_view_006(self):
        with open("tests/data/view_home_006.json") as file:
            self.verify_loaded_view_object(file)
