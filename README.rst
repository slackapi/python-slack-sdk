python-slackclient
==================

|build-status| |codecov| |doc-status| |pypi-version|

A basic client for Slack.com, which can optionally connect to the Slack Real Time Messaging (RTM) API.

Check out the `full documentation over here <http://slackapi.github.io/python-slackclient>`_.

Overview
--------

This plugin is a light wrapper around the `Slack API <https://api.slack.com/>`_. In its basic form, it can be used to call any API method and be expected to return a dict of the JSON reply.

The optional RTM connection allows you to create a persistent websocket connection, from which you can read events just like an official Slack client. This allows you to respond to events in real time without polling and send messages without making a full HTTPS request.


.. |build-status| image:: https://travis-ci.org/slackapi/python-slackclient.svg?branch=master
    :target: https://travis-ci.org/slackapi/python-slackclient
.. |codecov| image:: https://codecov.io/gh/slackapi/python-slackclient/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/slackapi/python-slackclient
.. |doc-status| image:: https://readthedocs.org/projects/python-slackclient/badge/?version=latest
    :target: http://python-slackclient.readthedocs.io/en/latest/?badge=latest
.. |pypi-version| image:: https://badge.fury.io/py/slackclient.svg
    :target: https://pypi.python.org/pypi/slackclient
