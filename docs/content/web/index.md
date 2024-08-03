==============================================
Web Client
==============================================

The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations we provide out of the box.

Access Slack's API methods requires an OAuth token -- see the `Tokens & Authentication <../installation/index.html>`_ section for more on how Slack uses OAuth tokens as well as best practices.

`Each of these API methods <https://api.slack.com/methods>`_ is fully documented on our developer site at https://api.slack.com/

The Python document for this module is available at https://slack.dev/python-slack-sdk/api-docs/slack_sdk/

Messaging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Sending a message**

One of the primary uses of Slack is posting messages to a channel using the channel ID or as a DM to another person using their user ID. This method will handle either a channel ID or a user ID passed to the ``channel`` parameter.

Note that your app's bot user needs to be in the channel (otherwise, you will get either ``not_in_channel`` or ``channel_not_found`` error code). If your app has `chat:write.public <https://api.slack.com/scopes/chat:write.public>`_ scope, your app can post messages without joining a channel as long as the channel is public. See `chat.postMessage <https://api.slack.com/methods/chat.postMessage>`_ for more info.

.. code-block:: python

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

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same
as sending a regular message, but with an additional ``user`` parameter.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    slack_token = os.environ["SLACK_BOT_TOKEN"]
    client = WebClient(token=slack_token)

    response = client.chat_postEphemeral(
        channel="C0XXXXXX",
        text="Hello silently from your app! :tada:",
        user="U0XXXXXXX"
    )

See `chat.postEphemeral <https://api.slack.com/methods/chat.postEphemeral>`_ for more info.

**Formatting with Block Kit**

Messages posted from apps can contain more than just text, though. They can include full user interfaces composed of `blocks <https://api.slack.com/block-kit>`_.

The chat.postMessage method takes an optional ``blocks`` argument that allows you to customize the layout of a message. Blocks can be specified in a single array of either dict values or `slack_sdk.models.blocks.Block <https://slack.dev/python-slack-sdk/api-docs/slack_sdk/models/blocks/index.html>`_ objects.

To send a message to a channel, use the channel's ID. For IMs, use the user's ID.

.. code-block:: python

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

**Note:** You can use the `Block Kit Builder <https://api.slack.com/tools/block-kit-builder>`_ to prototype your message's look and feel.

**Threading Messages**

Threaded messages are a way of grouping messages together to provide greater context. You can reply to a thread or start a new threaded conversation by simply passing the original message's ``ts`` ID in the ``thread_ts`` attribute when posting a message. If you're replying to a threaded message, you'll pass the `thread_ts` ID of the message you're replying to.

A channel or DM conversation is a nearly linear timeline of messages exchanged between people, bots, and apps. When one of these messages is replied to, it becomes the parent of a thread. By default, threaded replies do not appear directly in the channel, instead relegated to a kind of forked timeline descending from the parent message.

.. code-block:: python

    response = client.chat_postMessage(
        channel="C0XXXXXX",
        thread_ts="1476746830.000003",
        text="Hello from your app! :tada:"
    )

By default, ``reply_broadcast`` is set to ``False``. To indicate your reply is germane to all members of a channel, and therefore a notification of the reply should be posted in-channel, set the ``reply_broadcast`` to ``True``.

.. code-block:: python

    response = client.chat_postMessage(
        channel="C0XXXXXX",
        thread_ts="1476746830.000003",
        text="Hello from your app! :tada:",
        reply_broadcast=True
    )

**Note:** While threaded messages may contain attachments and message buttons, when your reply is broadcast to the
channel, it'll actually be a reference to your reply, not the reply itself.
So, when appearing in the channel, it won't contain any attachments or message buttons. Also note that updates and
deletion of threaded replies works the same as regular messages.

See the `Threading messages together <https://api.slack.com/docs/message-threading#forking_conversations>`_ article for more information.

**Updating a message**

Let's say you have a bot which posts the status of a request. When that request changes, you'll want to update the message to reflect it's state.

.. code-block:: python

    response = client.chat_update(
        channel="C0XXXXXX",
        ts="1476746830.000003",
        text="updates from your app! :tada:"
    )

See `chat.update <https://api.slack.com/methods/chat.update>`_ for formatting options and some special considerations when calling this with a bot user.

**Deleting a message**

Sometimes you need to delete things.

.. code-block:: python

    response = client.chat_delete(
        channel="C0XXXXXX",
        ts="1476745373.000002"
    )

See `chat.delete <https://api.slack.com/methods/chat.delete>`_ for more info.


**Emoji reactions**

You can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement -— or just for fun.

This method adds a reaction (emoji) to an item (``file``, ``file comment``, ``channel message``, ``group message``, or ``direct message``). One of file, file_comment, or the combination of channel and timestamp must be specified. Also, note that your app's bot user needs to be in the channel (otherwise, you will get either ``not_in_channel`` or ``channel_not_found`` error code).

.. code-block:: python

    response = client.reactions_add(
        channel="C0XXXXXXX",
        name="thumbsup",
        timestamp="1234567890.123456"
    )

Removing an emoji reaction is basically the same format, but you'll use ``reactions.remove`` instead of ``reactions.add``

.. code-block:: python

    response = client.reactions_remove(
        channel="C0XXXXXXX",
        name="thumbsup",
        timestamp="1234567890.123456"
    )


See `reactions.add <https://api.slack.com/methods/reactions.add>`_ and `reactions.remove <https://api.slack.com/methods/reactions.remove>`_ for more info.

--------

Files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Uploading files**

You can upload files onto Slack and share the file with people in channels. Note that your app's bot user needs to be in the channel (otherwise, you will get either ``not_in_channel`` or ``channel_not_found`` error code).

.. code-block:: python

    response = client.files_upload_v2(
        channel="C3UKJTQAC",
        file="files.pdf",
        title="Test upload",
        initial_comment="Here is the latest version of the file!",
    )

See `files_upload_v2 method release notes <https://github.com/slackapi/python-slack-sdk/releases/tag/v3.19.0>`_ for more info.

**Adding a remote file**

You can add a file information that is stored in an external storage, not in Slack.

.. code-block:: python

    response = client.files_remote_add(
        external_id="the-all-hands-deck-12345",
        external_url="https://{your domain}/files/the-all-hands-deck-12345",
        title="The All-hands Deck",
        preview_image="./preview.png" # will be displayed in channels
    )

See `files.remote.add <https://api.slack.com/methods/files.remote.add>`_ for more info.


--------

Conversations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Slack Conversations API provides your app with a unified interface to work with all the channel-like things encountered in Slack; public channels, private channels, direct messages, group direct messages, and our newest channel type, Shared Channels.

See `Conversations API <https://api.slack.com/docs/conversations-api>`_ docs for more info.

**Start a direct message**

The ``conversations_open`` method opens either a 1:1 direct message with a single user or a a multi-person direct message, depending on the number of users supplied to the ``users`` parameter.

*For public or private channels, use the conversations_create method.*

Provide a ``users`` parameter as an array with 1 to 8 user IDs to open or resume a conversation. Providing only 1 ID will create a direct message. Providing more will create a new multi-party DM or resume an existing conversation.

Subsequent calls to ``conversations_open`` with the same set of users will return the already existing conversation.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_open(users=["W123456789", "U987654321"])

See `conversations.open <https://api.slack.com/methods/conversations.open>`_ additional info.

**Creating channels**

Creates a new channel, either public or private. The ``name`` parameter is required, may contain numbers, letters, hyphens, and underscores, and must contain fewer than 80 characters. To make the channel private, set the option ``is_private`` parameter to ``True``.

.. code-block:: python

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

See `conversations.create <https://api.slack.com/methods/conversations.create>`_ additional info.

**Listing conversations**

To get a list of all the conversations in a workspace, use ``conversations_list``. By default, only public conversations are returned; use the ``types`` parameter specify which types of conversations you're interested in (Note: ``types`` is a string of comma-separated values)

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_list()
    conversations = response["channels"]

Use the ``types`` parameter to request additional channels, including ``public_channel``, ``private_channel``, ``mpim``, and ``im``. This parameter is a string of comma-separated values.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_list(
        types="public_channel, private_channel"
    )

See `conversations.list <https://api.slack.com/methods/conversations.list>`_ for more info.

Archived channels are included by default. You can exclude them by passing ``exclude_archived=True`` to your request.

.. code-block:: python

    response = client.conversations_list(exclude_archived=True)

See `conversations.list <https://api.slack.com/methods/conversations.list>`_ for more info.

**Getting a conversation information**

To retrieve a set of metadata about a channel (public, private, DM, or multi-party DM), use ``conversations_info``. The ``channel`` parameter is required and must be a valid channel ID. The optional ``include_locale`` boolean parameter will return locale data, which may be useful if you wish to return localized responses. The ``include_num_members`` boolean parameter will return the number of people in a channel.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_info(
        channel="C031415926",
        include_num_members=1
    )

See `conversations.info <https://api.slack.com/methods/conversations.info>`_ for more info.

**Getting members of a conversation**

To get a list of the members of a conversation, use ``conversations_members`` with the required ``channel`` parameter.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_members(channel="C16180339")
    user_ids = response["members"]

See `conversations.members <https://api.slack.com/methods/conversations.members>`_ for more info.

**Joining a conversation**

Channels are the social hub of most Slack teams. Here's how you hop into one:

.. code-block:: python

    response = client.conversations_join(channel="C0XXXXXXY")

If you are already in the channel, the response is slightly different.
``already_in_channel`` will be true, and a limited ``channel`` object will be returned. Bot users cannot join a channel on their own, they need to be invited by another user.

See `conversations.join <https://api.slack.com/methods/conversations.join>`_ for more info.

**Leaving a conversation**

To leave a conversation, use ``conversations_leave`` with the required ``channel`` param containing the ID of the channel to leave.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    response = client.conversations_leave(channel="C27182818")

See `conversations.leave <https://api.slack.com/methods/conversations.leave>`_ for more info.

--------

Modals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Opening a modal**

Modals allow you to collect data from users and display dynamic information in a focused surface.

Modals use the same ``blocks`` that compose messages with the addition of an ``input`` block.

.. code-block:: python

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

See `views.open <https://api.slack.com/methods/views.open>`_ more details and additional parameters.

Also, to run the above example, the following `Slack app configurations <https://api.slack.com/apps>`_ are required.

* Enable **Interactivity** with a valid Request URL: ``https://{your-public-domain}/slack/events``
* Add a global shortcut with the Callback ID: ``open-modal-shortcut``

**Updating and pushing modals**

In response to `view_submission` requests, you can tell Slack to update the current modal view by having `"response_action": "update"` and an updated view. Also, there are other response_action types such as `errors` and `push`. Refer to `the API document <https://api.slack.com/surfaces/modals/using#updating_response>`_ for more details.

.. code-block:: python

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

If your app modify the current modal view when receiving `block_actions` requests from Slack, you can call `views.update` API method with the given view ID.

.. code-block:: python

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

See `views.update <https://api.slack.com/methods/views.update>`_ for more info.

If you want to push a new view onto the modal instead of updating an existing view, reference the `views.push <https://api.slack.com/methods/views.push>`_ documentation.


--------

Rate Limits
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
When posting messages to a channel, Slack allows applications to send no more than one message per channel per second. We allow bursts over that limit for short periods. However, if your app continues to exceed the limit over a longer period of time it will be rate limited. Different API methods have other rate limits -- be sure to `check the limits <https://api.slack.com/docs/rate-limits>`_ and test that your application has a graceful fallback if it should hit those limits.

If you go over these limits, Slack will start returning a HTTP 429 Too Many Requests error, a JSON object containing the number of calls you have been making, and a Retry-After header containing the number of seconds until you can retry.

Here's a very basic example of how one might deal with rate limited requests.

.. code-block:: python

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

Since v3.9.0, the built-in ``RateLimitErrorRetryHandler`` is available as an easier way to do the retries for rate limited errors. Refer to the RetryHandler section in this page for more details.

To learn the Slack rate limits in general, see the documentation on `Rate Limiting <https://api.slack.com/docs/rate-limits>`_.

--------

Calling any API methods
--------------------------

This library covers all the public endpoints as the methods in ``WebClient``. That said, you may see a bit delay of the library release. When you're in a hurry, you can directly use ``api_call`` method as below.

.. code-block:: python

    import os
    from slack_sdk import WebClient

    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    response = client.api_call(
        api_method='chat.postMessage',
        params={'channel': '#random','text': "Hello world!"}
    )
    assert response["message"]["text"] == "Hello world!"


--------

AsyncWebClient
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All the API methods are available in asynchronous programming using the standard `asyncio <https://docs.python.org/3/library/asyncio.html>`_ library. You use ``AsyncWebClient`` instead for it.

``AsyncWebClient`` internally relies on `AIOHTTP <https://docs.aiohttp.org/en/stable/>`_ library but it is an optional dependency. So, to use this class, run ``pip install aiohttp`` beforehand.

.. code-block:: python

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


--------

RetryHandler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With the default settings, only ``ConnectionErrorRetryHandler`` with its default configuration (=only one retry in the manner of `exponential backoff and jitter <https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/>`_) is enabled. The retry handler retries if an API client encounters a connectivity-related failure (e.g., Connection reset by peer).

To use other retry handlers, you can pass a list of ``RetryHandler`` to the client constructor. For instance, you can add the built-in ``RateLimitErrorRetryHandler`` this way:

.. code-block:: python

    import os
    from slack_sdk.web import WebClient
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    # This handler does retries when HTTP status 429 is returned
    from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler
    rate_limit_handler = RateLimitErrorRetryHandler(max_retry_count=1)

    # Enable rate limited error retries as well
    client.retry_handlers.append(rate_limit_handler)

Creating your own ones is also quite simple. Defining a new class that inherits ``slack_sdk.http_retry.RetryHandler`` (``AsyncRetryHandler`` for asyncio apps) and implements required methods (internals of ``can_retry`` / ``prepare_for_next_retry``). Check the built-in ones' source code for learning how to properly implement.

.. code-block:: python

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

For asyncio apps, ``Async`` prefixed corresponding modules are available. All the methods in those methods are async/await compatible. Check `the source code <https://github.com/slackapi/python-slack-sdk/blob/main/slack_sdk/http_retry/async_handler.py>`_ and `tests <https://github.com/slackapi/python-slack-sdk/blob/main/tests/slack_sdk_async/web/test_async_web_client_http_retry.py>`_ for more details.


.. include:: ../metadata.rst
