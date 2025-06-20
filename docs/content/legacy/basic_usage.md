# Basic usage

:::danger

The [`slackclient`](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode and the [slack-sdk](https://pypi.org/project/slack-sdk/) project is its successor. The v3 SDK provides additional features such as Socket Mode, OAuth flow, SCIM API, Audit Logs API, better async support, retry handlers, and more.

:::

The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations we provide out of the box.

Accessing Slack API methods requires an OAuth token — read more about [installing with OAuth](https://docs.slack.dev/authentication/installing-with-oauth).

Each of these [API methods](https://docs.slack.dev/reference/methods) is fully documented on our developer site at [docs.slack.dev](https://docs.slack.dev/).

## Sending a message {#sending-messages}

One of the primary uses of Slack is posting messages to a channel using the channel ID, or as a DM to another person using their user ID. This method will handle either a channel ID or a user ID passed to the `channel` parameter.

``` python
import logging
logging.basicConfig(level=logging.DEBUG)

import os
from slack import WebClient
from slack.errors import SlackApiError

slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)

try:
  response = client.chat_postMessage(
    channel="C0XXXXXX",
    text="Hello from your app! :tada:"
  )
except SlackApiError as e:
  # You will get a SlackApiError if "ok" is False
  assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
```

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same as sending a regular message but with an additional `user` parameter.

``` python
import os
from slack import WebClient

slack_token = os.environ["SLACK_API_TOKEN"]
client = WebClient(token=slack_token)

response = client.chat_postEphemeral(
  channel="C0XXXXXX",
  text="Hello silently from your app! :tada:",
  user="U0XXXXXXX"
)
```

See the [`chat.postEphemeral`](https://docs.slack.dev/reference/methods/chat.postephemeral) API method for more details.

## Formatting messages with Block Kit {#block-kit}

Messages posted from apps can contain more than just text; they can also include full user interfaces composed of blocks using [Block Kit](https://docs.slack.dev/block-kit).

The [`chat.postMessage method`](https://docs.slack.dev/reference/methods/chat.postmessage) takes an optional blocks argument that allows you to customize the layout of a message. Blocks are specified in a single object literal, so just add additional keys for any optional argument.

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

:::tip

You can use [Block Kit Builder](https://app.slack.com/block-kit-builder/) to prototype your message's look and feel.

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

:::info

While threaded messages may contain attachments and message buttons, when your reply is broadcast to the channel, it'll actually be a reference to your reply and not the reply itself. When appearing in the channel, it won't contain any attachments or message buttons. Updates and deletion of threaded replies works the same as regular messages.

:::

Refer to the [threading messages](https://docs.slack.dev/messaging#threading) page for more information.

## Updating a message {#updating-messages}

Let's say you have a bot that posts the status of a request. When that request changes, you'll want to update the message to reflect it's state.

``` python
response = client.chat_update(
  channel="C0XXXXXX",
  ts="1476746830.000003",
  text="updates from your app! :tada:"
)
```

See the [`chat.update`](https://docs.slack.dev/reference/methods/chat.update) API method for formatting options and some special considerations when calling this with a bot user.

## Deleting a message {#deleting-messages}

Sometimes you need to delete things.

``` python
response = client.chat_delete(
  channel="C0XXXXXX",
  ts="1476745373.000002"
)
```

See the [`chat.delete`](https://docs.slack.dev/reference/methods/chat.delete) API method for more
details.

## Opening a modal {#opening-modals}

Modals allow you to collect data from users and display dynamic information in a focused surface. Modals use the same blocks that compose messages, with the addition of an `input` block.

``` python
# This module is available since v2.6
from slack.signature import SignatureVerifier
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

from flask import Flask, request, make_response
app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_app():
  if not signature_verifier.is_valid_request(request.get_data(), request.headers):
    return make_response("invalid request", 403)

  if "payload" in request.form:
    payload = json.loads(request.form["payload"])

    if payload["type"] == "shortcut" \
      and payload["callback_id"] == "open-modal-shortcut":
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
        return make_response("", 200)
      except SlackApiError as e:
        code = e.response["error"]
        return make_response(f"Failed to open a modal due to {code}", 200)

    if payload["type"] == "view_submission" \
      and payload["view"]["callback_id"] == "modal-id":
      # Handle a data submission request from the modal
      submitted_data = payload["view"]["state"]["values"]
      print(submitted_data)  # {'b-id': {'a-id': {'type': 'plain_text_input', 'value': 'your input'}}}
      return make_response("", 200)

  return make_response("", 404)

if __name__ == "__main__":
  # export SLACK_SIGNING_SECRET=***
  # export SLACK_API_TOKEN=xoxb-***
  # export FLASK_ENV=development
  # python3 app.py
  app.run("localhost", 3000)
```

See the [`views.open`](https://docs.slack.dev/reference/methods/views.open) API method more details and additional parameters.

To run the above example, the following [app configurations](https://api.slack.com/apps) are required:

* Enable **Interactivity** with a valid Request URL: `https://{your-public-domain}/slack/events`
* Add a global shortcut with the callback ID: `open-modal-shortcut`

## Updating and pushing modals {#updating-pushing-modals}

You can dynamically update a view inside of a modal by calling the `views.update` API method and passing the view ID returned in the previous `views.open` API method call.

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

See the [`views.update`](https://docs.slack.dev/reference/methods/views.update) API method for more details.

If you want to push a new view onto the modal instead of updating an existing view, see the [`views.push`](https://docs.slack.dev/reference/methods/views.push) API method.

## Emoji reactions {#emoji}

You can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement, or just for fun.

This method adds a reaction (emoji) to an item (`file`, `file comment`, `channel message`, `group message`, or `direct message`). One of `file`, `file_comment`, or the combination of `channel` and `timestamp` must be specified.

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

See the [`reactions.add`](https://docs.slack.dev/reference/methods/reactions.add) and [`reactions.remove`](https://docs.slack.dev/reference/methods/reactions.remove) API methods for more details.

## Listing public channels {#listing-public-channels}

At some point, you'll want to find out what channels are available to your app. This is how you get that list.

``` python
response = client.conversations_list(types="public_channel")
```

Archived channels are included by default. You can exclude them by passing `exclude_archived=1` to your request.

``` python
response = client.conversations_list(exclude_archived=1)
```

See the [`conversations.list`](https://docs.slack.dev/reference/methods/conversations.list) API method for more details.

## Getting a channel's info {#get-channel-info}

Once you have the ID for a specific channel, you can fetch information about that channel.

``` python
response = client.conversations_info(channel="C0XXXXXXX")
```

See the [`conversations.info`](https://docs.slack.dev/reference/methods/conversations.info) API method for more details.

## Joining a channel {#join-channel}

Channels are the social hub of most Slack teams. Here's how you hop into one:

``` python
response = client.conversations_join(channel="C0XXXXXXY")
```

If you are already in the channel, the response is slightly different. The `already_in_channel` attribute will be true, and a limited `channel` object will be returned. Bot users cannot join a channel on their own, they need to be invited by another user.

See the [`conversations.join`](https://docs.slack.dev/reference/methods/conversations.join) API method for more details.

------------------------------------------------------------------------

## Leaving a channel {#leave-channel}

Maybe you've finished up all the business you had in a channel, or maybe you joined one by accident. This is how you leave a channel.

``` python
response = client.conversations_leave(channel="C0XXXXXXX")
```

See the [`conversations.leave`](https://docs.slack.dev/reference/methods/conversations.leave) API method for more details.

## Listing team members {#list-team-members}

``` python
response = client.users_list()
users = response["members"]
user_ids = list(map(lambda u: u["id"], users))
```

See the [`users.list`](https://docs.slack.dev/reference/methods/users.list) API method for more details.

## Uploading files {#uploading-files}

``` python
response = client.files_upload_v2(
  channel="C3UKJTQAC",
  file="./files.pdf",
  title="Test upload"
)
```

See the [`files.upload`](https://docs.slack.dev/reference/methods/files.upload) API method for more details.

## Calling API methods {#calling-API-methods}

This library covers all the public endpoints as the methods in `WebClient`. That said, you may see a bit of a delay with the library release. When you're in a hurry, you can directly use the `api_call` method as below.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ['SLACK_API_TOKEN'])
response = client.api_call(
  api_method='chat.postMessage',
  json={'channel': '#random','text': "Hello world!"}
)
assert response["message"]["text"] == "Hello world!"
```

## Rate limits {#rate-limits}

When posting messages to a channel, Slack allows apps to send no more than one message per channel per second. We allow bursts over that limit for short periods; however, if your app continues to exceed the limit over a longer period of time, it will be rate limited. Different API methods have other limits — be sure to check the [rate limits](https://docs.slack.dev/apis/web-api/rate-limits) and test that your app has a graceful fallback if it should hit those limits.

If you go over these limits, Slack will begin returning *HTTP 429 Too Many Requests* errors, a JSON object containing the number of calls you have been making, and a *Retry-After* header containing the number of seconds until you can retry.

Here's an example of how you might handle rate limited requests:

``` python
import os
import time
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token=os.environ["SLACK_API_TOKEN"])

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

Refer to the [rate limits](https://docs.slack.dev/apis/web-api/rate-limits) page for more information.
