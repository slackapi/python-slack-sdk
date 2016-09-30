.. python-slackclient documentation master file, created by
   sphinx-quickstart on Mon Jun 27 17:36:09 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================================
Welcome to python-slackclient's documentation!
==============================================

Contents:

.. toctree::
   :maxdepth: 2

   source/classes

Overview
*****************
This plugin is a light wrapper around the `Slack API <api.slack.com/>`_. In its basic form, it can be used to call any API method and be expected to return a dict of the JSON reply.

The optional RTM connection allows you to create a persistent websocket connection, from which you can read events just like an official Slack client. This allows you to respond to events in real time without polling and send messages without making a full HTTPS request.

See `python-rtmbot <https://github.com/slackhq/python-rtmbot/>`_ for an active project utilizing this library.


Installation
******************

Automatic w/ PyPI (`virtualenv <https://virtualenv.readthedocs.io/en/latest/>`_ is recommended.)
-------------------------------------------------------------------------------------------------

.. code-block:: bash

	pip install slackclient

Manual
----------------------

.. code-block:: bash

	git clone https://github.com/slackhq/python-slackclient.git
	pip install -r requirements.txt

Usage
*********************

See examples in docs/examples

Note: You must obtain a token for the user/bot. You can find or generate these at the Slack API page.

Basic API methods
-----------------------

::

	from slackclient import SlackClient

	token = "xoxp-28192348123947234198234"      # found at https://api.slack.com/web#authentication
	sc = SlackClient(token)
	print sc.api_call("api.test")
	print sc.api_call("channels.info", channel="1234567890")
	print sc.api_call(
		"chat.postMessage", channel="#general", text="Hello from Python! :tada:",
		username='pybot', icon_emoji=':robot_face:'
	)


Real Time Messaging
-------------------------

::

	import time
	from slackclient import SlackClient

	token = "xoxp-28192348123947234198234"# found at https://api.slack.com/web#authentication
	sc = SlackClient(token)
	if sc.rtm_connect():
		while True:
			print sc.rtm_read()
			time.sleep(1)
	else:
	print "Connection Failed, invalid token?"


Objects & Methods
--------------------------

:class:`slackclient.SlackClient`
	The basic proxy-model for accessing most of the API and RTM functionality


:class:`slackclient._server.Server`
	object owns the websocket and all nested channel information.


:class:`SlackClient.server.channels` A searchable list of all known channels within the parent server.
Call print (sc instance) to see the entire list.

+------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------+
| Methods                                                                | Description                                                                                                    |
+========================================================================+================================================================================================================+
| SlackClient.server.channels.find([identifier])                         | The identifier can be either name or Slack channel ID. See above for examples.                                 |
+------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------+
| SlackClient.server.channels[int].send_message([text])	                 | Send message [text] to [int] channel in the channels list.                                                     |
+------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------+
| SlackClient.server.channels.find([identifier]).send_message([text])	 | Send message [text] to channel [identifier], which can be either channel name or ID. Ex "#general" or "C182391"|
+------------------------------------------------------------------------+----------------------------------------------------------------------------------------------------------------+

Contributing
************************

Submitting a Pull Request
-------------------------
Please feel free to sent us pull requests or issues that you'd like to see included in the python-slackclient!

We ask that you include any appropriate tests or documentation in the pull request and try to follow
`good commit message hygiene <https://medium.com/brigade-engineering/the-secrets-to-great-commit-messages-106fc0a92a25#.lsttwx97v>`_
in your commit message and PR commentary.

Building Documentation
-----------------------
To build this documentation you'll need to create a virtual environment.
You'll need to install `virtualenv <https://virtualenv.readthedocs.io/en/latest/>`_ if you don't already have it.

.. code-block:: bash

    pip install virtualenv

After virtualenv is installed, create a new environment and activate it:

.. code-block:: bash

    virtualenv env
    source env/bin/activate

Now you're ready to install the dependencies and generate these docs for yourself!

.. code-block:: bash

	pip install -r requirements-dev.txt -r requirements.txt
	cd docs
	make html

Once it's built, there will be a file at /docs/_build/html/index.html that you can open in your browser to see the docs.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
