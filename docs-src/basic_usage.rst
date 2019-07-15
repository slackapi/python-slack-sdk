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

  import os
  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(token=slack_token)

  client.chat_postMessage(
    channel="C0XXXXXX",
    text="Hello from your app! :tada:"
  )

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same
as sending a regular message, but with an additional ``user`` parameter.

.. code-block:: python

  import os
  import slack

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(token=slack_token)

  client.chat_postEphemeral(
    channel="C0XXXXXX",
    text="Hello silently from your app! :tada:",
    user="U0XXXXXXX"
  )

See `chat.postEphemeral <https://api.slack.com/methods/chat.postEphemeral>`_ for more info.

--------

Formatting with Block Kit
------------------------------
Messages posted from apps can contain more than just text, though. They can include full user interfaces composed of `blocks <https://api.slack.com/docs/block-kit>`_.

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

  client.chat_postMessage(
      channel="C0XXXXXX",
      text="Hello from your app! :tada:",
      thread_ts="1476746830.000003"
  )

By default, ``reply_broadcast`` is set to ``False``. To indicate your reply is germane to all members of a channel, and therefore a notification of the reply should be posted in-channel, set the ``reply_broadcast`` to ``True``.

.. code-block:: python

  client.chat_postMessage(
    channel="C0XXXXXX",
    text="Hello from your app! :tada:",
    thread_ts="1476746830.000003",
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

  client.chat_update(
    ts="1476746830.000003",
    channel="C0XXXXXX",
    text="updates from your app! :tada:"
  )

See `chat.update <https://api.slack.com/methods/chat.update>`_ for formatting options and some special considerations when calling this with a bot user.

--------

Deleting a message
-------------------
Sometimes you need to delete things.

.. code-block:: python

  client.chat_delete(
    channel="C0XXXXXX",
    ts="1476745373.000002"
  )

See `chat.delete <https://api.slack.com/methods/chat.delete>`_ for more info.

--------

Emoji reactions
---------------------------------------
You can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement -— or just for fun.

This method adds a reaction (emoji) to an item (``file``, ``file comment``, ``channel message``, ``group message``, or ``direct message``). One of file, file_comment, or the combination of channel and timestamp must be specified.

.. code-block:: python

  client.reactions_add(
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
  )

Removing an emoji reaction is basically the same format, but you'll use ``reactions.remove`` instead of ``reactions.add``

.. code-block:: python

  client.reactions_remove(
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
  )


See `reactions.add <https://api.slack.com/methods/reactions.add>`_ and `reactions.remove <https://api.slack.com/methods/reactions.remove>`_ for more info.

--------

Listing channels
---------------------------
At some point, you'll want to find out what channels are available to your app. This is how you get that list.

.. code-block:: python

  client.channels_list()

Archived channels are included by default. You can exclude them by passing ``exclude_archived=1`` to your request.

.. code-block:: python

  client.channels_list(
    exclude_archived=1
  )

See `channels.list <https://api.slack.com/methods/channels.list>`_ for more info.

--------

Getting a channel's info
-------------------------
Once you have the ID for a specific channel, you can fetch information about that channel.

.. code-block:: python

  client.channels_info(,
    channel="C0XXXXXXX"
  )

See `channels.info <https://api.slack.com/methods/channels.info>`_ for more info.

--------

Joining a channel
------------------
Channels are the social hub of most Slack teams. Here's how you hop into one:

.. code-block:: python

  client.channels_join(
    channel="C0XXXXXXY"
  )

If you are already in the channel, the response is slightly different.
``already_in_channel`` will be true, and a limited ``channel`` object will be returned. Bot users cannot join a channel on their own, they need to be invited by another user.

See `channels.join <https://api.slack.com/methods/channels.join>`_ for more info.

--------

Leaving a channel
------------------
Maybe you've finished up all the business you had in a channel, or maybe you
joined one by accident. This is how you leave a channel.

.. code-block:: python

  client.channels_leave(
    channel="C0XXXXXXX"
  )

See `channels.leave <https://api.slack.com/methods/channels.leave>`_ for more info.

--------

Listing team members
--------------------

.. code-block:: python

  client.users_list()

See `users.list <https://api.slack.com/methods/users.list>`_ for more info.


--------

Uploading files
---------------

.. code-block:: python

  client.files_upload(
    channels="C3UKJTQAC",
    file="files.pdf",
    title="Test upload"
  )

See `files.upload <https://api.slack.com/methods/files.upload>`_ for more info.


--------

Web API Rate Limits
--------------------
When posting messages to a channel, Slack allows applications to send no more than one message per channel per second. We allow bursts over that limit for short periods. However, if your app continues to exceed the limit over a longer period of time it will be rate limited. Different API methods have other rate limits -- be sure to `check the limits <https://api.slack.com/docs/rate-limits>`_ and test that your application has a graceful fallback if it should hit those limits.

If you go over these limits, Slack will start returning a HTTP 429 Too Many Requests error, a JSON object containing the number of calls you have been making, and a Retry-After header containing the number of seconds until you can retry.

Here's a very basic example of how one might deal with rate limited requests.

.. code-block:: python

  import slack
  import time

  slack_token = os.environ["SLACK_API_TOKEN"]
  client = slack.WebClient(token=slack_token)

  # Simple wrapper for sending a Slack message
  def send_slack_message(channel, message):
    return client.chat_postMessage(
      channel=channel,
      text=message
    )

  # Make the API call and save results to `response`
  response = send_slack_message("C0XXXXXX", "Hello, from Python!")

  # Check to see if the message sent successfully.
  # If the message succeeded, `response["ok"]`` will be `True`
  if response["ok"]:
    print(f"Message posted successfully: {response["message"]["ts"]}")
    # If the message failed, check for rate limit headers in the response
  elif response["ok"] is False and response["headers"]["Retry-After"]:
    # The `Retry-After` header will tell you how long to wait before retrying
    delay = int(response["headers"]["Retry-After"])
    print("Rate limited. Retrying in " + str(delay) + " seconds")
    time.sleep(delay)
    send_slack_message(message, channel)

See the documentation on `Rate Limiting <https://api.slack.com/docs/rate-limits>`_ for more info.

.. include:: metadata.rst

