# Conversations API

:::danger

The [`slackclient`](https://pypi.org/project/slackclient/) PyPI project is in maintenance mode and the [slack-sdk](https://pypi.org/project/slack-sdk/) project is its successor. The v3 SDK provides additional features such as Socket Mode, OAuth flow, SCIM API, Audit Logs API, better async support, retry handlers, and more.

:::

The Slack Conversations API provides your app with a unified interface to work with all the channel-like things encountered in Slack: public channels, private channels, direct messages, group direct messages, and shared channels.

Refer to [using the Conversations API](https://docs.slack.dev/apis/web-api/using-the-conversations-api) for more information.

## Direct messages {#direct-messages}

The `conversations.open` API method opens either a 1:1 direct message with a single user or a multi-person direct message, depending on the number of users supplied to the `users` parameter. (For public or private channels, use the `conversations.create` API method.)

Provide a `users` parameter as an array with 1-8 user IDs to open or resume a conversation. Providing only 1 ID will create a direct message. providing more IDs will create a new multi-party direct message or will resume an existing conversation.

Subsequent calls with the same set of users will return the already existing conversation.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_open(users=["W123456789", "U987654321"])
```

See the [`conversations.open`](https://docs.slack.dev/reference/methods/conversations.open) API method for additional details.

## Creating channels {#creating-channels}

Creates a new channel, either public or private. The `name` parameter is required and may contain numbers, letters, hyphens, or underscores, and must contain fewer than 80 characters. To make the channel private, set the optional `is_private` parameter to `True`.

``` python
import os
from slack import WebClient
from time import time

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
channel_name = f"my-private-channel-{round(time())}"
response = client.conversations_create(
  name=channel_name,
  is_private=True
)
channel_id = response["channel"]["id"]
response = client.conversations_archive(channel=channel_id)
```

See the [`conversations.create`](https://docs.slack.dev/reference/methods/conversations.create) API method for additional details.

## Getting conversation information {#more-information}

To retrieve a set of metadata about a channel (public, private, DM, or multi-party DM), use the `conversations.info` API method. The `channel` parameter is required and must be a valid channel ID. The optional `include_locale` boolean parameter will return locale data, which may be useful if you wish to return localized responses. The `include_num_members` boolean parameter will return the number of people in a channel.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_info(
  channel="C031415926",
  include_num_members=1
)
```

See the [`conversations.info`](https://docs.slack.dev/reference/methods/conversations.info) API method for more details.

## Listing conversations {#listing-conversations}

To get a list of all the conversations in a workspace, use the `conversations.list` API method. By default, only public conversations are returned. Use the `types` parameter specify which types of conversations you're interested in. Note that `types` is a string of comma-separated values.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_list()
conversations = response["channels"]
```

Use the `types` parameter to request additional channels, including `public_channel`, `private_channel`, `mpdm`, and `dm`. This parameter is a string of comma-separated values.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_list(
  types="public_channel, private_channel"
)
```

See the [`conversations.list`](https://docs.slack.dev/reference/methods/conversations.list) API method for more details.

## Getting members of a conversation {#get-members}

To get a list of members for a conversation, use the `conversations.members` API method with the required `channel` parameter.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_members(channel="C16180339")
user_ids = response["members"]
```

See the [`conversations.members`](https://docs.slack.dev/reference/methods/conversations.members) API method for more details.

## Leaving a conversation {#leave-conversations}

To leave a conversation, use the `conversations.leave` API method with the required `channel` parameter containing the ID of the channel to leave.

``` python
import os
from slack import WebClient

client = WebClient(token=os.environ["SLACK_API_TOKEN"])
response = client.conversations_leave(channel="C27182818")
```

See the [`conversations.leave`](https://docs.slack.dev/reference/methods/conversations.leave) API method for more details.
