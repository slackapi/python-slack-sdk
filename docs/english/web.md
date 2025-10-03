# Web client

The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations we provide out of the box.

Accessing Slack API methods requires an OAuth token — read more about [installing with OAuth](/authentication/installing-with-oauth).

Each of these [API methods](/reference/methods) is fully documented on our developer site at [docs.slack.dev](/).

## Sending a message {#sending-messages}

One of the primary uses of Slack is posting messages to a channel using the channel ID, or as a DM to another person using their user ID. This method will handle either a channel ID or a user ID passed to the `channel` parameter.

Your app's bot user needs to be in the channel (otherwise, you will get either `not_in_channel` or `channel_not_found` error code). If your app has the [chat:write.public](/reference/scopes/chat.write.public) scope, your app can post messages without joining a channel as long as the channel is public. See the [chat.postMessage](/reference/methods/chat.postMessage) API method for more info.

``` python
import logging
logging.basicConfig(level=logging.DEBUG)

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)

try:
    response = client.chat_postMessage(
        channel="C0XXXXXX",
        text="Hello from your app! :tada:"
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]    # str like 'invalid_auth', 'channel_not_found'
```

### Sending ephemeral messages

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same as sending a regular message but with an additional `user` parameter.

``` python
import os
from slack_sdk import WebClient

slack_token = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=slack_token)

response = client.chat_postEphemeral(
    channel="C0XXXXXX",
    text="Hello silently from your app! :tada:",
    user="U0XXXXXXX"
)
```

See the [`chat.postEphemeral`](/reference/methods/chat.postEphemeral) API method for more details.

### Sending streaming messages {#sending-streaming-messages}

You can have your app's messages stream in to replicate conventional AI chatbot behavior. This is done through three Web API methods:

* [`chat_startStream`](/reference/methods/chat.startstream)
* [`chat_appendStream`](/reference/methods/chat.appendstream)
* [`chat_stopStream`](/reference/methods/chat.stopstream)

:::tip[The Python Slack SDK provides a [`chat_stream()`](https://docs.slack.dev/tools/python-slack-sdk/reference/web/client.html#slack_sdk.web.client.WebClient.chat_stream) helper utility to streamline calling these methods.]

See the [_Streaming messages_](/tools/bolt-python/concepts/message-sending#streaming-messages) section of the Bolt for Python docs for implementation instructions. 

:::

#### Starting the message stream {#starting-stream}

First you need to begin the message stream:

```python
# Example: Stream a response to any message
@app.message()
def handle_message(message, client):
    channel_id = event.get("channel")
    team_id = event.get("team")
    thread_ts = event.get("thread_ts") or event.get("ts")
    user_id = event.get("user")
    
    # Start a new message stream
    stream_response = client.chat_startStream(
        channel=channel_id,
        recipient_team_id=team_id,
        recipient_user_id=user_id,
        thread_ts=thread_ts,
    )
    stream_ts = stream_response["ts"]
```

#### Appending content to the message stream {#appending-stream}

With the stream started, you can then append text to it in chunks to convey a streaming effect.

The structure of the text coming in will depend on your source. The following code snippet uses OpenAI's response structure as an example:

```python
# continued from above
    for event in returned_message:
        if event.type == "response.output_text.delta":
            client.chat_appendStream(
                channel=channel_id, 
                ts=stream_ts, 
                markdown_text=f"{event.delta}"
            )
        else:
            continue
```

#### Stopping the message stream {#stopping-stream}

Your app can then end the stream with the `chat_stopStream` method:

```python
# continued from above
    client.chat_stopStream(
        channel=channel_id, 
        ts=stream_ts
    )
```

The method also provides you an opportunity to request user feedback on your app's responses using the [feedback buttons](/reference/block-kit/block-elements/feedback-buttons-element) block element within the [context actions](/reference/block-kit/blocks/context-actions-block) block. The user will be presented with thumbs up and thumbs down buttons which send an action to your app when pressed.

```python
def create_feedback_block() -> List[Block]:
    blocks: List[Block] = [
        ContextActionsBlock(
            elements=[
                FeedbackButtonsElement(
                    action_id="feedback",
                    positive_button=FeedbackButtonObject(
                        text="Good Response",
                        accessibility_label="Submit positive feedback on this response",
                        value="good-feedback",
                    ),
                    negative_button=FeedbackButtonObject(
                        text="Bad Response",
                        accessibility_label="Submit negative feedback on this response",
                        value="bad-feedback",
                    ),
                )
            ]
        )
    ]
    return blocks

@app.message()
def handle_message(message, client):
    # ... previous streaming code ...
    
    # Stop the stream and add interactive elements
    feedback_block = create_feedback_block()
    client.chat_stopStream(
        channel=channel_id, 
        ts=stream_ts, 
        blocks=feedback_block
    )
```

See [Formatting messages with Block Kit](#block-kit) below for more details on using Block Kit with messages.

## Formatting messages with Block Kit {#block-kit}

Messages posted from apps can contain more than just text; they can also include full user interfaces composed of blocks using [Block Kit](/block-kit).

The [`chat.postMessage method`](/reference/methods/chat.postMessage) takes an optional blocks argument that allows you to customize the layout of a message. Blocks can be specified
in a single array of either dict values or [slack_sdk.models.blocks.Block](https://docs.slack.dev/tools/python-slack-sdk/reference/models/blocks/index.html) objects.

To send a message to a channel, use the channel's ID. For DMs, use the user's ID.

``` python
client.chat_postMessage(
    channel="C0XXXXXX",
    blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Danny Torrence left the following review for your property:"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "<https://example.com|Overlook Hotel> \n :star: \n Doors had too many axe holes, guest in room " +
                    "237 was far too rowdy, whole place felt stuck in the 1920s."
            },
            "accessory": {
                "type": "image",
                "image_url": "https://images.pexels.com/photos/750319/pexels-photo-750319.jpeg",
                "alt_text": "Haunted hotel image"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": "*Average Rating*\n1.0"
                }
            ]
        }
    ]
)
```

:::tip[You can use [Block Kit Builder](https://app.slack.com/block-kit-builder/) to prototype your message's look and feel.]

:::

## Threading messages {#threading-messages}

Threaded messages are a way of grouping messages together to provide greater context. You can reply to a thread or start a new threaded conversation by simply passing the original message's `ts` ID in the `thread_ts` attribute when posting a message. If you're replying to a threaded message, you'll pass the `thread_ts` ID of the message you're replying to.

A channel or DM conversation is a nearly linear timeline of messages exchanged between people, bots, and apps. When one of these messages is replied to, it becomes the parent of a thread. By default, threaded replies do not appear directly in the channel, but are instead relegated to a kind of forked timeline descending from the parent message.

``` python
response = client.chat_postMessage(
    channel="C0XXXXXX",
    thread_ts="1476746830.000003",
    text="Hello from your app! :tada:"
)
```

By default, the `reply_broadcast` parameter is set to `False`. To indicate your reply is germane to all members of a channel and therefore a notification of the reply should be posted in-channel, set the `reply_broadcast` parameter to `True`.

``` python
response = client.chat_postMessage(
    channel="C0XXXXXX",
    thread_ts="1476746830.000003",
    text="Hello from your app! :tada:",
    reply_broadcast=True
)
```
:::info[While threaded messages may contain attachments and message buttons, when your reply is broadcast to the channel, it'll actually be a reference to your reply and not the reply itself.] 

When appearing in the channel, it won't contain any attachments or message buttons. Updates and deletion of threaded replies works the same as regular messages.

:::

Refer to the [threading messages](/messaging#threading) page for more information.

## Updating a message {#updating-messages}

Let's say you have a bot that posts the status of a request. When that request changes, you'll want to update the message to reflect it's state.

``` python
response = client.chat_update(
    channel="C0XXXXXX",
    ts="1476746830.000003",
    text="updates from your app! :tada:"
)
```

See the [`chat.update`](/reference/methods/chat.update) API method for formatting options and some special considerations when calling this with a bot user.

## Deleting a message {#deleting-messages}

Sometimes you need to delete things.

``` python
response = client.chat_delete(
    channel="C0XXXXXX",
    ts="1476745373.000002"
)
```

See the [`chat.delete`](/reference/methods/chat.delete) API method for more
details.

## Conversations {#conversations}

The Slack Conversations API provides your app with a unified interface to work with all the channel-like things encountered in Slack: public channels, private channels, direct messages, group direct messages, and shared channels.

Refer to [using the Conversations API](/apis/web-api/using-the-conversations-api) for more information.

### Direct messages {#direct-messages}

The `conversations.open` API method opens either a 1:1 direct message with a single user or a multi-person direct message, depending on the number of users supplied to the `users` parameter. (For public or private channels, use the `conversations.create` API method.)

Provide a `users` parameter as an array with 1-8 user IDs to open or resume a conversation. Providing only 1 ID will create a direct message. providing more IDs will create a new multi-party direct message or will resume an existing conversation.

Subsequent calls with the same set of users will return the already existing conversation.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_open(users=["W123456789", "U987654321"])
```

See the [`conversations.open`](/reference/methods/conversations.open) API method for additional details.

### Creating channels {#creating-channels}

Creates a new channel, either public or private. The `name` parameter is required and may contain numbers, letters, hyphens, or underscores, and must contain fewer than 80 characters. To make the channel private, set the optional `is_private` parameter to `True`.

``` python
import os
from slack_sdk import WebClient
from time import time

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
channel_name = f"my-private-channel-{round(time())}"
response = client.conversations_create(
    name=channel_name,
    is_private=True
)
channel_id = response["channel"]["id"]
response = client.conversations_archive(channel=channel_id)
```

See the [`conversations.create`](/reference/methods/conversations.create) API method for additional details.

### Getting conversation information {#getting-conversation-info}

To retrieve a set of metadata about a channel (public, private, DM, or multi-party DM), use the `conversations.info` API method. The `channel` parameter is required and must be a valid channel ID. The optional `include_locale` boolean parameter will return locale data, which may be useful if you wish to return localized responses. The `include_num_members` boolean parameter will return the number of people in a channel.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_info(
    channel="C031415926",
    include_num_members=1
)
```

See the [`conversations.info`](/reference/methods/conversations.info) API method for more details.

### Listing conversations {#listing-conversations}

To get a list of all the conversations in a workspace, use the `conversations.list` API method. By default, only public conversations are returned. Use the `types` parameter specify which types of conversations you're interested in. Note that `types` is a string of comma-separated values.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_list()
conversations = response["channels"]
```

Use the `types` parameter to request additional channels, including `public_channel`, `private_channel`, `mpdm`, and `dm`. This parameter is a string of comma-separated values.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_list(
    types="public_channel, private_channel"
)
```

Archived channels are included by default. You can exclude them by passing `exclude_archived=True` to your request.

``` python
response = client.conversations_list(exclude_archived=True)
```

See the [`conversations.list`](/reference/methods/conversations.list) API method for more details.

### Getting members of a conversation {#getting-conversation-members}

To get a list of members for a conversation, use the `conversations.members` API method with the required `channel` parameter.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_members(channel="C16180339")
user_ids = response["members"]
```

See the [`conversations.members`](/reference/methods/conversations.members) API method for more details.

### Joining a conversation {#joining-conversations}

Channels are the social hub of most Slack teams. Here's how you hop into one:

``` python
response = client.conversations_join(channel="C0XXXXXXY")
```

If you are already in the channel, the response is slightly different. The `already_in_channel` attribute will be true, and a limited `channel` object will be returned. Bot users cannot join a channel on their own, they need to be invited by another user.

See the [`conversations.join`](/reference/methods/conversations.join) API method for more details.

### Leaving a conversation {#leaving-conversations}

To leave a conversation, use the `conversations.leave` API method with the required `channel` parameter containing the ID of the channel to leave.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
response = client.conversations_leave(channel="C27182818")
```

See the [`conversations.leave`](/reference/methods/conversations.leave) API method for more details.

## Opening a modal {#opening-modals}

Modals allow you to collect data from users and display dynamic information in a focused surface. Modals use the same blocks that compose messages, with the addition of an `input` block.

``` python
from slack_sdk.signature import SignatureVerifier
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

from flask import Flask, request, make_response, jsonify
app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_app():
    if not signature_verifier.is_valid_request(request.get_data(), request.headers):
        return make_response("invalid request", 403)

    if "payload" in request.form:
        payload = json.loads(request.form["payload"])
        if payload["type"] == "shortcut" and payload["callback_id"] == "test-shortcut":
            # Open a new modal by a global shortcut
            try:
                api_response = client.views_open(
                    trigger_id=payload["trigger_id"],
                    view={
                        "type": "modal",
                        "callback_id": "modal-id",
                        "title": {
                            "type": "plain_text",
                            "text": "Awesome Modal"
                        },
                        "submit": {
                            "type": "plain_text",
                            "text": "Submit"
                        },
                        "blocks": [
                            {
                                "type": "input",
                                "block_id": "b-id",
                                "label": {
                                    "type": "plain_text",
                                    "text": "Input label",
                                },
                                "element": {
                                    "action_id": "a-id",
                                    "type": "plain_text_input",
                                }
                            }
                        ]
                    }
                )
                return make_response("", 200)
            except SlackApiError as e:
                code = e.response["error"]
                return make_response(f"Failed to open a modal due to {code}", 200)

        if (
            payload["type"] == "view_submission"
            and payload["view"]["callback_id"] == "modal-id"
        ):
            # Handle a data submission request from the modal
            submitted_data = payload["view"]["state"]["values"]
            print(submitted_data)    # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}

            # Close this modal with an empty response body
            return make_response("", 200)

    return make_response("", 404)

if __name__ == "__main__":
    # export SLACK_SIGNING_SECRET=***
    # export SLACK_BOT_TOKEN=xoxb-***
    # export FLASK_ENV=development
    # python3 app.py
    app.run("localhost", 3000)
```

See the [`views.open`](/reference/methods/views.open) API method more details and additional parameters.

Also, to run the above example, the following [Slack app
configurations](https://api.slack.com/apps) are required.

To run the above example, the following [app configurations](https://api.slack.com/apps) are required:

* Enable **Interactivity** with a valid Request URL: `https://{your-public-domain}/slack/events`
* Add a global shortcut with the callback ID: `open-modal-shortcut`

## Updating and pushing modals {#updating-pushing-modals}

In response to `view_submission` requests, you can tell Slack to update the current modal view by having `"response_action": update` and an updated view. There are also other `response_action` types, such as `errors` and `push`. Refer to the [modals](/surfaces/modals) page for more details.

``` python
if (
    payload["type"] == "view_submission"
    and payload["view"]["callback_id"] == "modal-id"
):
    # Handle a data submission request from the modal
    submitted_data = payload["view"]["state"]["values"]
    print(submitted_data)    # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}

    # Update the modal with a new view
    return make_response(
        jsonify(
            {
                "response_action": "update",
                "view": {
                    "type": "modal",
                    "title": {"type": "plain_text", "text": "Accepted"},
                    "close": {"type": "plain_text", "text": "Close"},
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "plain_text",
                                "text": "Thanks for submitting the data!",
                            },
                        }
                    ],
                },
            }
        ),
        200,
    )
```

If your app modifies the current modal view when receiving `block_actions` requests from Slack, you can call the `views.update` API method with the given view ID.

``` python
private_metadata = "any str data you want to store"
response = client.views_update(
    view_id=payload["view"]["id"],
    hash=payload["view"]["hash"],
    view={
        "type": "modal",
        "callback_id": "modal-id",
        "private_metadata": private_metadata,
        "title": {
            "type": "plain_text",
            "text": "Awesome Modal"
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "b-id",
                "label": {
                    "type": "plain_text",
                    "text": "Input label",
                },
                "element": {
                    "action_id": "a-id",
                    "type": "plain_text_input",
                }
            }
        ]
    }
)
```

See the [`views.update`](/reference/methods/views.update) API method for more details.

If you want to push a new view onto the modal instead of updating an existing view, see the [`views.push`](/reference/methods/views.push) API method.

## Emoji reactions {#emoji}

You can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement, or just for fun.

This method adds a reaction (emoji) to an item (`file`, `file comment`, `channel message`, `group message`, or `direct message`). One of `file`, `file_comment`, or the combination of `channel` and `timestamp` must be specified. Note that your app's bot user needs to be in the channel (otherwise, you will get either a `not_in_channel` or `channel_not_found` error code).

``` python
response = client.reactions_add(
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
)
```

Removing an emoji reaction is basically the same format, but you'll use the `reactions.remove` API method instead of the `reactions.add` API method.

``` python
response = client.reactions_remove(
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
)
```

See the [`reactions.add`](/reference/methods/reactions.add) and [`reactions.remove`](/reference/methods/reactions.remove) API methods for more details.

## Uploading files {#upload-files}

You can upload files to Slack and share them with people in channels. Note that your app's bot user needs to be in the channel (otherwise, you will get either `not_in_channel` or `channel_not_found` error code).

``` python
response = client.files_upload_v2(
    file="test.pdf",
    title="Test upload",
    channel="C3UKJTQAC",
    initial_comment="Here is the latest version of the file!",
)
```

If you want to share files within a thread, you can pass `thread_ts` in addition to `channel_id` as shown below:

``` python
response = client.files_upload_v2(
    file="test.pdf",
    title="Test upload",
    channel="C3UKJTQAC",
    thread_ts="1731398999.934122",
    initial_comment="Here is the latest version of the file!",
)
```

See the [`files.upload`](/reference/methods/files.upload) API method for more details.

## Adding a remote file {#adding-remote-files}

You can add a file information that is stored in an external storage rather than in Slack.

``` python
response = client.files_remote_add(
    external_id="the-all-hands-deck-12345",
    external_url="https://{your domain}/files/the-all-hands-deck-12345",
    title="The All-hands Deck",
    preview_image="./preview.png" # will be displayed in channels
)
```

See the [files.remote.add](/reference/methods/files.remote.add) API method for more details.

## Calling API methods {#calling-API-methods}

This library covers all the public endpoints as the methods in `WebClient`. That said, you may see a bit of a delay with the library release. When you're in a hurry, you can directly use the `api_call` method as below.

``` python
import os
from slack_sdk import WebClient

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
response = client.api_call(
    api_method='chat.postMessage',
    params={'channel': '#random','text': "Hello world!"}
)
assert response["message"]["text"] == "Hello world!"
```

## AsyncWebClient {#asyncwebclient}

The webhook client is available in asynchronous programming using the standard [asyncio](https://docs.python.org/3/library/asyncio.html) library. You use `AsyncWebhookClient` instead. `AsyncWebhookClient` internally relies on the [AIOHTTP](https://docs.aiohttp.org/en/stable/) library, but it is an optional dependency. To use this class, run `pip install aiohttp` beforehand.

``` python
import asyncio
import os
# requires: pip install aiohttp
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

client = AsyncWebClient(token=os.environ['SLACK_API_TOKEN'])

# This must be an async method
async def post_message():
    try:
        # Don't forget `await` keyword here
        response = await client.chat_postMessage(
            channel='#random',
            text="Hello world!"
        )
        assert response["message"]["text"] == "Hello world!"
    except SlackApiError as e:
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

# This is the simplest way to run the async method
# but you can go with any ways to run it
asyncio.run(post_message())
```

## RetryHandler {#retryhandler}

With the default settings, only `ConnectionErrorRetryHandler` with its default configuration (=only one retry in the manner of [exponential backoff and jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., connection reset by peer).

To use other retry handlers, you can pass a list of `RetryHandler` to the client constructor. For instance, you can add the built-in `RateLimitErrorRetryHandler` this way:

``` python
import os
from slack_sdk.web import WebClient
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# This handler does retries when HTTP status 429 is returned
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)

# Enable rate limited error retries as well
client.retry_handlers.append(rate_limit_handler)
```

You can also create one on your own by defining a new class that inherits `slack_sdk.http_retry RetryHandler` (`AsyncRetryHandler` for asyncio apps) and implements required methods (internals of `can_retry` / `prepare_for_next_retry`). Check out the source code for the ones that are built in to learn how to properly implement them.

``` python
import socket
from typing import Optional
from slack_sdk.http_retry import (RetryHandler, RetryState, HttpRequest, HttpResponse)
from slack_sdk.http_retry.builtin_interval_calculators import BackoffRetryIntervalCalculator
from slack_sdk.http_retry.jitter import RandomJitter

class MyRetryHandler(RetryHandler):
    def _can_retry(
        self,
        *,
        state: RetryState,
        request: HttpRequest,
        response: Optional[HttpResponse] = None,
        error: Optional[Exception] = None
    ) -> bool:
        # [Errno 104] Connection reset by peer
        return error is not None and isinstance(error, socket.error) and error.errno == 104

client = WebClient(
    token=os.environ["SLACK_BOT_TOKEN"],
    retry_handlers=[MyRetryHandler(
        max_retry_count=1,
        interval_calculator=BackoffRetryIntervalCalculator(
            backoff_factor=0.5,
            jitter=RandomJitter(),
        ),
    )],
)
```

For asyncio apps, `Async` prefixed corresponding modules are available. All the methods in those methods are async/await compatible. Check [the source code](https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/http_retry/async_handler.py) for more details.

## Rate limits {#rate-limits}

When posting messages to a channel, Slack allows apps to send no more than one message per channel per second. We allow bursts over that limit for short periods; however, if your app continues to exceed the limit over a longer period of time, it will be rate limited. Different API methods have other limits — be sure to check the [rate limits](/apis/web-api/rate-limits) and test that your app has a graceful fallback if it should hit those limits.

If you go over these limits, Slack will begin returning *HTTP 429 Too Many Requests* errors, a JSON object containing the number of calls you have been making, and a *Retry-After* header containing the number of seconds until you can retry.

Here's an example of how you might handle rate limited requests:

``` python
import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

# Simple wrapper for sending a Slack message
def send_slack_message(channel, message):
    return client.chat_postMessage(
        channel=channel,
        text=message
    )

# Make the API call and save results to `response`
channel = "#random"
message = "Hello, from Python!"
# Do until being rate limited
while True:
    try:
        response = send_slack_message(channel, message)
    except SlackApiError as e:
        if e.response.status_code == 429:
            # The `Retry-After` header will tell you how long to wait before retrying
            delay = int(e.response.headers['Retry-After'])
            print(f"Rate limited. Retrying in {delay} seconds")
            time.sleep(delay)
            response = send_slack_message(channel, message)
        else:
            # other errors
            raise e
```

Since v3.9.0, the built-in `RateLimitErrorRetryHandler` is available as an easier way to do retries for rate limited errors. Refer to the [RetryHandler](#retryhandler) section for more details.

Refer to the [rate limits](/apis/web-api/rate-limits) page for more information.
