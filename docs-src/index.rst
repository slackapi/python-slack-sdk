.. toctree::
     :hidden:

     self
     v3-migration/index
     installation/index
     web/index
     webhook/index
     oauth/index
     real_time_messaging
     faq
     about

==============================================
|product_name|
==============================================

The Slack platform offers several APIs to build apps. Each Slack API delivers part of the capabilities from the platform, so that you can pick just those that fit for your needs. This SDK offers a corresponding package for each of Slack’s APIs. They are small and powerful when used independently, and work seamlessly when used together, too.

+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Feature                        | What its for                                                                                  | Package                            |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Web API                        | Send data to or query data from Slack using any of over 200 methods.                          | ``slack_sdk.web``                  |
|                                |                                                                                               | ``slack_sdk.web.async_client``     |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Webhooks / response_url        | Send a message using Incoming Webhooks or response_url                                        | ``slack_sdk.webhook``              |
|                                |                                                                                               | ``slack_sdk.webhook.async_client`` |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| OAuth                          | Setup the authentication flow using V2 OAuth for Slack apps.                                  | ``slack_sdk.oauth``                |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| RTM API                        | Listen for incoming messages and a limited set of events happening in Slack, using WebSocket. | ``slack_sdk.rtm```                 |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| Request Signature Verification | Verify incoming requests from the Slack API servers.                                          | ``slack_sdk.signature``            |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+
| UI Builders                    | Construct UI components using easy-to-use builders.                                           | ``slack_sdk.models``               |
+--------------------------------+-----------------------------------------------------------------------------------------------+------------------------------------+

Installation
************

This package supports Python 3.6 and higher. We recommend using `PyPI <https://pypi.python.org/pypi>`_ to install |product_name|

.. code-block:: bash

	pip install slack_sdk

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
        from slack_sdk import WebClient
        client = WebClient()
        api_response = client.api_test()

You can run the code this way.

.. code-block:: bash

	python test.py

It's also good to try on the Python REPL.

Getting Help
************

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

- `GitHub Issue Tracker <https://github.com/slackapi/python-slackclient/issues>`_ for questions, feature requests, bug reports and general discussion related to this package.
- Visit the `Slack Developer Community <http://slackcommunity.com>`_ for getting help using |product_name| or just generally bond with your fellow Slack developers.

.. include:: metadata.rst
