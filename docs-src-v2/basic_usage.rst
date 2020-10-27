.. _web-api-examples:

==============================================
Basic Usage
==============================================

The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations we provide out of the box.

Access Slack's API methods requires an OAuth token -- see the `Tokens & Authentication <auth>`_ section for more on how Slack uses OAuth tokens as well as best practices.

`Each of these API methods <https://api.slack.com/methods>`_ is fully documented on our developer site at api.slack.com

Sending a message
-----------------------
One of the primary uses of Slack is posting messages to a channel using the channel ID or as a DM to another person using their user ID. This method will handle either a channel ID or a user ID passed to the ``channel`` parameter.

.. code-block:: python

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

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same
as sending a regular message, but with an additional ``user`` parameter.

.. code-block:: python

  import os
  from slack import WebClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = WebClient(token=slack_token)

  response = client.chat_postEphemeral(
    channel="C0XXXXXX",
    text="Hello silently from your app! :tada:",
    user="U0XXXXXXX"
  )

See `chat.postEphemeral <https://api.slack.com/methods/chat.postEphemeral>`_ for more info.

--------

Formatting with Block Kit
------------------------------
Messages posted from apps can contain more than just text, though. They can include full user interfaces composed of `blocks <https://api.slack.com/block-kit>`_.

The chat.postMessage method takes an optional blocks argument that allows you to customize the layout of a message. Blocks specified in a single object literal, so just add additional keys for any optional argument.

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

--------

Threading Messages
------------------
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

See the `Threading messages together <https://api.slack.com/docs/message-threading#forking_conversations>`_
article for more information.

--------

Updating a message
----------------------------------
Let's say you have a bot which posts the status of a request. When that request changes, you'll want to update the message to reflect it's state.

.. code-block:: python

  response = client.chat_update(
    channel="C0XXXXXX",
    ts="1476746830.000003",
    text="updates from your app! :tada:"
  )

See `chat.update <https://api.slack.com/methods/chat.update>`_ for formatting options and some special considerations when calling this with a bot user.

--------

Deleting a message
-------------------
Sometimes you need to delete things.

.. code-block:: python

  response = client.chat_delete(
    channel="C0XXXXXX",
    ts="1476745373.000002"
  )

See `chat.delete <https://api.slack.com/methods/chat.delete>`_ for more info.

--------

Opening a modal
----------------------------------
Modals allow you to collect data from users and display dynamic information in a focused surface.

Modals use the same blocks that compose messages with the addition of an `input` block.

.. code-block:: python

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

See `views.open <https://api.slack.com/methods/views.open>`_ more details and additional parameters.

Also, to run the above example, the following `Slack app configurations <https://api.slack.com/apps>`_ are required.

* Enable **Interactivity** with a valid Request URL: ``https://{your-public-domain}/slack/events``
* Add a global shortcut with the Callback ID: ``open-modal-shortcut``

--------

Updating and pushing modals
------------------------------
You can dynamically update a view inside of a modal by calling `views.update` and passing the view ID returned in the previous `views.open` call.

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

Emoji reactions
---------------------------------------
You can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement -— or just for fun.

This method adds a reaction (emoji) to an item (``file``, ``file comment``, ``channel message``, ``group message``, or ``direct message``). One of file, file_comment, or the combination of channel and timestamp must be specified.

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

Listing public channels
---------------------------
At some point, you'll want to find out what channels are available to your app. This is how you get that list.

.. code-block:: python

  response = client.conversations_list(types="public_channel")

Archived channels are included by default. You can exclude them by passing ``exclude_archived=1`` to your request.

.. code-block:: python

  response = client.conversations_list(exclude_archived=1)

See `conversations.list <https://api.slack.com/methods/conversations.list>`_ for more info.

--------

Getting a channel's info
-------------------------
Once you have the ID for a specific channel, you can fetch information about that channel.

.. code-block:: python

  response = client.conversations_info(channel="C0XXXXXXX")

See `conversations.info <https://api.slack.com/methods/conversations.info>`_ for more info.

--------

Joining a channel
------------------
Channels are the social hub of most Slack teams. Here's how you hop into one:

.. code-block:: python

  response = client.conversations_join(channel="C0XXXXXXY")

If you are already in the channel, the response is slightly different.
``already_in_channel`` will be true, and a limited ``channel`` object will be returned. Bot users cannot join a channel on their own, they need to be invited by another user.

See `conversations.join <https://api.slack.com/methods/conversations.join>`_ for more info.

--------

Leaving a channel
------------------
Maybe you've finished up all the business you had in a channel, or maybe you
joined one by accident. This is how you leave a channel.

.. code-block:: python

  response = client.conversations_leave(channel="C0XXXXXXX")

See `conversations.leave <https://api.slack.com/methods/conversations.leave>`_ for more info.

--------

Listing team members
--------------------

.. code-block:: python

  response = client.users_list()
  users = response["members"]
  user_ids = list(map(lambda u: u["id"], users))

See `users.list <https://api.slack.com/methods/users.list>`_ for more info.


--------

Uploading files
---------------

.. code-block:: python

  response = client.files_upload(
    channels="C3UKJTQAC",
    file="files.pdf",
    title="Test upload"
  )

See `files.upload <https://api.slack.com/methods/files.upload>`_ for more info.

--------

Calling any API methods
--------------------------

This library covers all the public endpoints as the methods in ``WebClient``. That said, you may see a bit delay of the library release. When you're in a hurry, you can directly use ``api_call`` method as below.

.. code-block:: python

  import os
  from slack import WebClient

  client = WebClient(token=os.environ['SLACK_API_TOKEN'])
  response = client.api_call(
    api_method='chat.postMessage',
    json={'channel': '#random','text': "Hello world!"}
  )
  assert response["message"]["text"] == "Hello world!"


--------

Web API Rate Limits
--------------------
When posting messages to a channel, Slack allows applications to send no more than one message per channel per second. We allow bursts over that limit for short periods. However, if your app continues to exceed the limit over a longer period of time it will be rate limited. Different API methods have other rate limits -- be sure to `check the limits <https://api.slack.com/docs/rate-limits>`_ and test that your application has a graceful fallback if it should hit those limits.

If you go over these limits, Slack will start returning a HTTP 429 Too Many Requests error, a JSON object containing the number of calls you have been making, and a Retry-After header containing the number of seconds until you can retry.

Here's a very basic example of how one might deal with rate limited requests.

.. code-block:: python

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
      if e.response["error"] == "ratelimited":
        # The `Retry-After` header will tell you how long to wait before retrying
        delay = int(e.response.headers['Retry-After'])
        print(f"Rate limited. Retrying in {delay} seconds")
        time.sleep(delay)
        response = send_slack_message(channel, message)
      else:
        # other errors
        raise e

See the documentation on `Rate Limiting <https://api.slack.com/docs/rate-limits>`_ for more info.

.. include:: metadata.rst

