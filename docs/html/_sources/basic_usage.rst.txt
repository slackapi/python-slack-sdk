.. _web-api-examples:

==============================================
Basic Usage
==============================================
The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations
we provide out of the box.

This package is a modular wrapper designed to make Slack `Web API`_ calls simpler and easier for your
app. Provided below are examples of how to interact with commonly used API endpoints, but this is by no means
a complete list. Review the full list of available methods `here <https://api.slack.com/methods>`_.

See :ref:`Tokens & Authentication <handling-tokens>` for API token handling best practices.

--------

Sending a message
-----------------------
The primary use of Slack is sending messages. Whether you're sending a message
to a user or to a channel, this method handles both.

To send a message to a channel, use the channel's ID. For IMs, use the user's ID.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.postMessage",
    channel="C0XXXXXX",
    text="Hello from Python! :tada:"
  )

There are some unique options specific to sending IMs, so be sure to read the **channels**
section of the `chat.postMessage <https://api.slack.com/methods/chat.postMessage#channels>`_
page for a full list of formatting and authorship options.

Sending an ephemeral message, which is only visible to an assigned user in a specified channel, is nearly the same 
as sending a regular message, but with an additional ``user`` parameter.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.postEphemeral",
    channel="C0XXXXXX",
    text="Hello from Python! :tada:",
    user="U0XXXXXXX"
  )

See `chat.postEphemeral <https://api.slack.com/methods/chat.postEphemeral>`_ for more info.

--------

Customizing a message's layout
-----------------------
The chat.postMessage method takes an optional blocks argument that allows you to customize the layout of a message. 
Blocks for Web API methods are all specified in a single object literal, so just add additional keys for any optional argument.

To send a message to a channel, use the channel's ID. For IMs, use the user's ID.

.. code-block:: python

  sc.api_call(
    "chat.postMessage",
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

**Note:** You can use the `Block Kit Builder <https://api.slack.com/tools/block-kit-builder>`for a playground where you can prototype your message's look and feel.

--------

Replying to messages and creating threads
------------------------------------------
Threaded messages are just like regular messages, except thread replies are grouped together to provide greater context
to the user. You can reply to a thread or start a new threaded conversation by simply passing the original message's ``ts``
ID in the ``thread_ts`` attribute when posting a message. If you're replying to a threaded message, you'll pass the `thread_ts`
ID of the message you're replying to.

A channel or DM conversation is a nearly linear timeline of messages exchanged between people, bots, and apps.
When one of these messages is replied to, it becomes the parent of a thread. By default, threaded replies do not
appear directly in the channel, instead relegated to a kind of forked timeline descending from the parent message.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.postMessage",
    channel="C0XXXXXX",
    text="Hello from Python! :tada:",
    thread_ts="1476746830.000003"
  )


By default, ``reply_broadcast`` is set to ``False``. To indicate your reply is germane to all members of a channel,
set the ``reply_broadcast`` boolean parameter to ``True``.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.postMessage",
    channel="C0XXXXXX",
    text="Hello from Python! :tada:",
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

Updating the content of a message
----------------------------------
Let's say you have a bot which posts the status of a request. When that request
is updated, you'll want to update the message to reflect it's state. Or your user
might want to fix a typo or change some wording. This is how you'll make those changes.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.update",
    ts="1476746830.000003",
    channel="C0XXXXXX",
    text="Hello from Python! :tada:"
  )

See `chat.update <https://api.slack.com/methods/chat.update>`_ for formatting options
and some special considerations when calling this with a bot user.

--------

Deleting a message
-------------------
Sometimes you need to delete things.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "chat.delete",
    channel="C0XXXXXX",
    ts="1476745373.000002"
  )

See `chat.delete <https://api.slack.com/methods/chat.delete>`_ for more info.

--------

Adding or removing an emoji reaction
---------------------------------------
You can quickly respond to any message on Slack with an emoji reaction. Reactions
can be used for any purpose: voting, checking off to-do items, showing excitement — and just for fun.

This method adds a reaction (emoji) to an item (``file``, ``file comment``, ``channel message``, ``group message``, or ``direct message``). One of file, file_comment, or the combination of channel and timestamp must be specified.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "reactions.add",
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
  )

Removing an emoji reaction is basically the same format, but you'll use ``reactions.remove`` instead of ``reactions.add``

.. code-block:: python

  sc.api_call(
    "reactions.remove",
    channel="C0XXXXXXX",
    name="thumbsup",
    timestamp="1234567890.123456"
  )


See `reactions.add <https://api.slack.com/methods/reactions.add>`_ and `reactions.remove <https://api.slack.com/methods/reactions.remove>`_ for more info.

--------

Getting a list of channels
---------------------------
At some point, you'll want to find out what channels are available to your app. This is how you get that list.

**Note:** This call requires the ``channels:read`` scope.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call("channels.list")

Archived channels are included by default. You can exclude them by passing ``exclude_archived=1`` to your request.


.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "channels.list",
    exclude_archived=1
  )

See `channels.list <https://api.slack.com/methods/channels.list>`_ for more info.

--------

Getting a channel's info
-------------------------
Once you have the ID for a specific channel, you can fetch information about that channel.

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "channels.info",
    channel="C0XXXXXXX"
  )

See `channels.info <https://api.slack.com/methods/channels.info>`_ for more info.

--------

Joining a channel
------------------
Channels are the social hub of most Slack teams. Here's how you hop into one:

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "channels.join",
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

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call(
    "channels.leave",
    channel="C0XXXXXXX"
  )

See `channels.leave <https://api.slack.com/methods/channels.leave>`_ for more info.

--------

Get a list of team members
------------------------------

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  sc.api_call("users.list")

See `users.list <https://api.slack.com/methods/users.list>`_ for more info.


--------

Uploading files
------------------------------

.. code-block:: python

  from slackclient import SlackClient

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  with open('thinking_very_much.png') as file_content:
      sc.api_call(
          "files.upload",
          channels="C3UKJTQAC",
          file=file_content,
          title="Test upload"
      )

See `files.upload <https://api.slack.com/methods/files.upload>`_ for more info.


--------

Web API Rate Limits
--------------------
Slack allows applications to send no more than one message per second. We allow bursts over that
limit for short periods. However, if your app continues to exceed the limit over a longer period
of time it will be rate limited.

Here's a very basic example of how one might deal with rate limited requests.

If you go over these limits, Slack will start returning a HTTP 429 Too Many Requests error,
a JSON object containing the number of calls you have been making, and a Retry-After header
containing the number of seconds until you can retry.


.. code-block:: python

  from slackclient import SlackClient
  import time

  slack_token = os.environ["SLACK_API_TOKEN"]
  sc = SlackClient(slack_token)

  # Simple wrapper for sending a Slack message
  def send_slack_message(channel, message):
    return sc.api_call(
      "chat.postMessage",
      channel=channel,
      text=message
    )

  # Make the API call and save results to `response`
  response = send_slack_message("C0XXXXXX", "Hello, from Python!")

  # Check to see if the message sent successfully.
  # If the message succeeded, `response["ok"]`` will be `True`
  if response["ok"]:
    print("Message posted successfully: " + response["message"]["ts"])
    # If the message failed, check for rate limit headers in the response
  elif response["ok"] is False and response["headers"]["Retry-After"]:
    # The `Retry-After` header will tell you how long to wait before retrying
    delay = int(response["headers"]["Retry-After"])
    print("Rate limited. Retrying in " + str(delay) + " seconds")
    time.sleep(delay)
    send_slack_message(message, channel)

See the documentation on `Rate Limiting <https://api.slack.com/docs/rate-limits>`_ for more info.

.. include:: metadata.rst

