.. toctree::
   :hidden:

   self
   auth
   basic_usage
   conversations
   real_time_messaging
   faq
   changelog
   about

Important Notice
*********************

The `slackclient <https://pypi.org/project/slackclient/>`_ PyPI project is in maintenance mode now and `slack-sdk <https://pypi.org/project/slack-sdk/>`_ project is the successor. The v3 SDK provides more functionalities such as Socket Mode, OAuth flow module, SCIM API, Audit Logs API, better asyncio support, retry handlers, and many more.

Refer to `the migration guide <https://slack.dev/python-slack-sdk/v3-migration/index.html#from-slackclient-2-x>`_ to learn how to smoothly migrate your existing code.

--------

==============================================
|product_name|
==============================================

Slack's APIs allow anyone to build full featured integrations that extend
and expand the capabilities of your Slack workspace. These APIs allow you
to build applications that interact with Slack just like the people on your
team -- they can post messages, respond to events that happen -- as well
as build complex UIs for getting work done.

To make it easier for Python programmers to build Slack applications, we've
provided this open source SDK. |product_name| will let you get started building
Python apps as quickly as possible. The current version, |current_version|, is
built for Python 3.6 and higher -- if you need to target Python 2.x, you might
consider using v1 of the SDK.

Slack Platform Basics
*********************
If you're new to the Slack platform, we have a general purpose `guide for building apps <https://api.slack.com/start>`_ that isn't specific to any language or framework. It's a great place to learn all about the concepts that go into building a great Slack app.

Before you get started building on the Slack platform, you need to `set up your app's configuration <https://api.slack.com/apps/new>`_. This is where you define things like your app's permissions and the endpoints that Slack should use for interacting with the backend you will build with Python.

The app configuration page is also where you will acquire the OAuth token you will use to call Slack's APIs. Treat this token with care, just like you would a password, because it has access to workspace and can potentially read and write data to and from it.


Installation
************

We recommend using `PyPI <https://pypi.python.org/pypi>`_ to install |product_name|

.. code-block:: bash

	pip install slackclient

Of course, you can always pull the source code directly into your project:

.. code-block:: bash

	git clone https://github.com/slackapi/python-slackclient.git

And then, save a few lines of code as ``./test.py``.

.. code-block:: python

    # test.py
    import sys
    # Load the local source directly
    sys.path.insert(1, "./python-slackclient")
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    # Verify it works
    from slack import WebClient
    client = WebClient()
    api_response = client.api_test()

You can run the code this way.

.. code-block:: bash

	python test.py

It's also good to try on the Python REPL.

Getting Help
************

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

- Use our `Github Issue Tracker <https://github.com/slackapi/python-slackclient/issues>`_ for reporting bugs or requesting features.
- Visit the `Slack Developer Community <http://slackcommunity.com>`_ for getting help using |product_name| or just generally bond with your fellow Slack developers.

.. include:: metadata.rst
