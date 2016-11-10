python-slackclient
================

[![Build Status](https://travis-ci.org/slackapi/python-slackclient.svg?branch=master)](https://travis-ci.org/slackapi/python-slackclient)
[![codecov](https://codecov.io/gh/slackapi/python-slackclient/branch/master/graph/badge.svg)](https://codecov.io/gh/slackapi/python-slackclient)
[![Documentation Status](https://readthedocs.org/projects/python-slackclient/badge/?version=latest)](http://python-slackclient.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/slackclient.svg)](https://pypi.python.org/pypi/slackclient)

A basic client for Slack.com, which can optionally connect to the Slack Real Time Messaging (RTM) API.

Check out the [full documentation over here](http://slackapi.github.io/python-slackclient).

Overview
---------
This plugin is a light wrapper around the [Slack API](https://api.slack.com/). In its basic form, it can be used to call any API method and be expected to return a dict of the JSON reply.

The optional RTM connection allows you to create a persistent websocket connection, from which you can read events just like an official Slack client. This allows you to respond to events in real time without polling and send messages without making a full HTTPS request.
