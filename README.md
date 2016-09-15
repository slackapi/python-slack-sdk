python-slackclient
================

[![Build Status](https://travis-ci.org/slackhq/python-slackclient.svg?branch=master)](https://travis-ci.org/slackhq/python-slackclient)
[![Coverage Status](https://coveralls.io/repos/github/slackhq/python-slackclient/badge.svg?branch=master)](https://coveralls.io/github/slackhq/python-slackclient?branch=master)
[![Documentation Status](https://readthedocs.org/projects/python-slackclient/badge/?version=latest)](http://python-slackclient.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/slackclient.svg)](https://pypi.python.org/pypi/slackclient)

A basic client for Slack.com, which can optionally connect to the Slack Real Time Messaging (RTM) API.

Check out the [full documentation over here](http://python-slackclient.readthedocs.io/en/latest/?badge=latest)!

Overview
---------
This plugin is a light wrapper around the [Slack API](https://api.slack.com/). In its basic form, it can be used to call any API method and be expected to return a dict of the JSON reply.

The optional RTM connection allows you to create a persistent websocket connection, from which you can read events just like an official Slack client. This allows you to respond to events in real time without polling and send messages without making a full HTTPS request.

See [python-rtmbot](https://github.com/slackhq/python-rtmbot/) for an active project utilizing this library.
