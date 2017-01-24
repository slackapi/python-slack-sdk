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
    channel="#python",
    text="Hello from Python! :tada:"
  )

There are some unique options specific to sending IMs, so be sure to read the **channels**
section of the `chat.postMessage <https://api.slack.com/methods/chat.postMessage#channels>`_
page for a full list of formatting and authorship options.

--------

Replying to messages and creating threads
-----------------------
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
    channel="#python",
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
    channel="#python",
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

.. include:: metadata.rst
