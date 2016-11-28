python-slackclient
===================

A basic client for Slack.com, which can optionally connect to the Slack Real Time Messaging (RTM) API.

|build-status| |codecov| |doc-status| |pypi-version|

.. |build-status| image:: https://travis-ci.org/slackapi/python-slackclient.svg?branch=master
    :target: https://travis-ci.org/slackapi/python-slackclient
.. |codecov| image:: https://codecov.io/gh/slackapi/python-slackclient/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/slackapi/python-slackclient
.. |doc-status| image:: https://readthedocs.org/projects/python-slackclient/badge/?version=latest
    :target: http://python-slackclient.readthedocs.io/en/latest/?badge=latest
.. |pypi-version| image:: https://badge.fury.io/py/slackclient.svg
    :target: https://pypi.python.org/pypi/slackclient

Overview
--------

Whether you're building a custom app for your team, or integrating a third party
service into your Slack workflows, Slack Developer Kit for Python allows you to leverage the flexibility
of Python to get your project up and running as quickly as possible.

Requirements and Installation
******************************

Slack Developer Kit for Python currently works with Python 2.7 (watch for Python 3 support in the future), and requires `PyPI` to install
dependencies. Of course, since you probably installed this module with `PyPI`, this is not a problem.

We recommend using `PyPI <https://pypi.python.org/pypi>`_ to install Slack Developer Kit for Python

.. code-block:: bash

	pip install slackclient

Of course, if you prefer doing things the hard way, you can always implement Slack Developer Kit for Python
by pulling down the source code directly into your project:

.. code-block:: bash

	git clone https://github.com/slackapi/python-slackclient.git
	pip install -r requirements.txt

Getting Help
-------------

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

- Use our `Github Issue Tracker <https://github.com/slackapi/python-slackclient/issues>`_ for reporting bugs or requesting features.
- Visit the `dev4slack channel <http://dev4slack.xoxco.com>`_ for getting help using Slack Developer Kit for Python or just generally bond with your fellow Slack developers.

Documentation
--------------

For comprehensive method information and usage examples, see the `full documentation <http://slackapi.github.io/python-slackclient>`_.

Basic Usage
------------
The Slack Web API allows you to build applications that interact with Slack in more complex ways than the integrations
we provide out of the box.

This package is a modular wrapper designed to make Slack `Web API <https://api.slack.com/web>`_ calls simpler and easier for your
app. Provided below are examples of how to interact with commonly used API endpoints, but this is by no means
a complete list. Review the full list of available methods `here <https://api.slack.com/methods>`_.

See `Tokens & Authentication <http://slackapi.github.io/python-slackclient/auth.html#handling-tokens>` for API token handling best practices.

Sending a message
********************
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

Deleting a message
********************
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

Adding or removing an emoji reaction
****************************************
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

Getting a list of channels
******************************
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

Getting a channel's info
*************************
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

Joining a channel
********************
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

Leaving a channel
********************
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

Additional Information
********************************************************************************************
For comprehensive method information and usage examples, see the `full documentation`_.
