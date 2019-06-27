# Using the Slack object classes

## Composing Messages

Messages are built up out of blocks and legacy attachments. Blocks are composed of the base Block classes in `blocks.py`, which themselves are composed of elements (`elements.py`) which are either atomic or contain common sub-objects (`objects.py`).

For example: A simple block template, containing a header, some fields, and an actions block at the bottom would be built up as follows:

```python
from slack.web.client import WebClient
from slack.web.classes import messages, blocks, elements

client = WebClient(token="abc")

fields = blocks.SectionBlock(fields=["*Type:*\nComputer", "*Reason:*\nAll vowel keys aren't working"])

approve_button = elements.ButtonElement(text="Approve", action_id="approval", value="order_123", style="primary")
deny_button = elements.ButtonElement(text="Deny", action_id="denial", value="order_123", style="danger")

buttons = [approve_button, deny_button]

actions = blocks.ActionsBlock(elements=buttons)

work_order_message = messages.Message(text="You have a new request", blocks=[fields, actions])

client.chat_postMessage(channel="C12345", **work_order_message.to_dict())
```

## Composing Dialogs
Dialogs can be built using a helper 'builder' class, to simplify keeping track of required fields.

```python
from slack.web.client import WebClient
from slack.web.classes import dialogs

builder = (
    dialogs.DialogBuilder()
        .title("My Cool Dialog")
        .callback_id("myCoolDialog")
        .state({'value': 123, 'key': "something"})
        .conversation_selector(name="target", label="Choose Target")
        .text_area(name="message", label="Message", hint="Enter a message", max_length=500)
        .text_field(name="signature", label="Signature", optional=True, max_length=50)
)

client = WebClient(token="abc")

client.dialog_open(dialog=builder.to_dict(), trigger_id="123458.12355")
```
