# Python slackclient
The Python slackclient is a developer kit for interfacing with the Slack Web API and Real Time Messaging (RTM) API on Python 3.6 and above.

> **Note**: This client should not be used in any current SlackClient apps without regarding our Migration Guide located [here][migration-guide].

[![pypi package][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]
[![Build Status][windows-build-status]][windows-build-url]
[![Python Version][python-version]][pypi-url]
[![codecov][codecov-image]][codecov-url]
[![contact][contact-image]][contact-url]


Whether you're building a custom app for your team, or integrating a third party service into your Slack workflows, Slack Developer Kit for Python allows you to leverage the flexibility of Python to get your project up and running as quickly as possible.

You may also review our [Development Roadmap][dev-roadmap] in the project wiki.

The **Python slackclient** allows interaction with:

- The Slack web api methods available at our [Api Docs site][api-methods]
- Interaction with our [RTM API][rtm-docs]

If you want to use our [Events API][events-docs], please check the [Slack Events API adapter for Python][python-slack-events-api].

Details on the Tokens and Authentication can be found in our [Auth Guide][auth-guide].

</br>

## Table of contents

* [Requirements](#requirements)
* [Installation](#installation)
* [Build your first app](#build-an-app-in-10-minutes)
* [Basic Usage of the Web Client](#basic-usage-of-the-web-client)
    * [Sending a message to Slack](#sending-a-message-to-slack)
    * [Uploading files to Slack](#uploading-files-to-slack)
* [Basic Usage of the RTM Client](#basic-usage-of-the-rtm-client)
* [Advanced Options](#advanced-options)
* [Support](#support)
* [Change Logs](#change-logs)

</br>

### Requirements
---
This Library requires Python 3.6 and above. If you require Python 2, please use our [SlackClient - v1.3.1][slackclientv1]. If you're unsure how to check what version of Python you're on, you can check it using the following:

> **Note:** You may need to use `python3` before your commands to ensure you use the correct Python path. e.g. `python3 --version`


```bash
python --version

-- or --

python3 --version
```
</br>

### Installation

We recommend using [PyPI][pypi] to install the Slack Developer Kit for Python.


```bash
pip3 install slackclient
```

If you require Python 2 support, you can use the following to install the previous version of our Developer Kit

```bash
pip install slackclient==1.3.1
```

</br>

### Build an app in 10 minutes
---

> _Link to the "Build an app in 10 minutes" guide_

_For more examples and usage, please refer to the [Slack API Documentation site][api-docs]._

</br>

### Basic Usage of the Web Client
---

Slack provide a Web API that gives you the ability to build applications that interact with Slack in a variety of ways. This Development Kit is a module based wrapper that makes interaction with that API easier. We have a basic example here with some of the more common uses but a full list of the available methods are available [here][api-methods]. More detailed examples can be found in our [Basic Usage][basic-usage] guide


#### Sending a message to Slack

One of the most common use-cases is sending a message to Slack. If you want to send a message as your app, or as a user, this method can do both. In our examples, we specify the channel name, however it is recommended to use the `channel_id` where possible.

```python
    import os
    import slack

    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

    response = client.chat_postMessage(
        channel='#random',
        text="Hello world!")
    assert response["ok"]
    assert response["message"]["text"] == "Hello world!"
```

Here we also ensure that the response back from Slack is a successful one and that the message is the one we sent by using the `assert` statement.


#### Uploading files to Slack

We've changed the process for uploading files to Slack to be much easier and straight forward. You can now just include a path to the file directly in the API call and upload it that way. You can find the details on this api call [here][files.upload]

```python
    import os
    import slack

    client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])

    response = client.files_upload(
        channels='#random',
        file="my_file.pdf")
    assert response["ok"]
```

</br>

### Basic Usage of the RTM Client
---

The [Real Time Messaging (RTM) API][rtm-docs] is a WebSocket-based API that allows you to receive events from Slack in real time and send messages as users.

If you prefer events to be pushed to you instead, we recommend using the HTTP-based [Events API][events-docs] instead. Most event types supported by the RTM API are also available in the Events API. You can check out our [Python Slack Events Adaptor][events-sdk] if you want to use this API instead.

An RTMClient allows apps to communicate with the Slack Platform's RTM API.

The event-driven architecture of this client allows you to simply
link callbacks to their corresponding events. When an event occurs
this client executes your callback while passing along any
information it receives. We also give you the ability to call our web client from inside your callbacks.

In our example below, we watch for a [message event][message-event] that contains "Hello" and if its recieved, we call the `say_hello()` function. We then issue a call to the web client to post back to the channel saying "Hi" to the user.

```python
    import os
    import slack

    @slack.RTMClient.run_on(event='message')
    def say_hello(**payload):
        data = payload['data']
        web_client = payload['web_client']
        rtm_client = payload['rtm_client']
        if 'Hello' in data['text']:
            channel_id = data['channel']
            thread_ts = data['ts']
            user = data['user']

            web_client.chat_postMessage(
                channel=channel_id,
                text=f"Hi <@{user}>!",
                thread_ts=thread_ts
            )

    slack_token = os.environ["SLACK_API_TOKEN"]
    rtm_client = slack.RTMClient(slack_token)
    rtm_client.start()
```

</br>

### Advanced Options

The Python slackclient v2 now uses [AIOHttp][aiohttp] under the hood so it allows us to use their inbuilt SSL and Proxy support. You can pass it directly into the call while constructing the Slack Client for both the RTM and the Web client.

```python
import os
import slack
    
client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'], ssl=sslcert, proxy=proxyinfo)

```

We will always follow the standard process in AIOHttp for those proxy and SSL settings so for more information, check out their documentation page linked [here][aiohttp].
</br>

### Support
---

If you get stuck, we’re here to help. The following are the best ways to get assistance working through your issue:

Use our [Github Issue Tracker][gh-issues] for reporting bugs or requesting features.
Visit the [Bot Developer Hangout][bd-hangout] for getting help using Slack Developer Kit for Python or just generally bond with your fellow Slack developers.

</br>

### Change Logs
---

<details>
  <summary><strong>Release History</strong> (click to expand)</summary>

<!-- rel -->

* 2.0.0
    * To be added
* 1.3.1
    * To be added
<!-- relstop -->


</details>

</br>

<!-- Markdown links -->
[pypi-image]: https://badge.fury.io/py/slackclient.svg
[pypi-url]: https://pypi.python.org/pypi/slackclient
[windows-build-status]: https://ci.appveyor.com/api/projects/status/rif04t60ptslj32x/branch/master?svg=true
[windows-build-url]: https://ci.appveyor.com/project/slackapi/python-slackclient
[travis-image]: https://travis-ci.org/slackapi/python-slackclient.svg?branch=master
[travis-url]: https://travis-ci.org/slackapi/python-slackclient
[python-version]:  https://img.shields.io/pypi/pyversions/slackclient.svg
[codecov-image]: https://codecov.io/gh/slackapi/python-slackclient/branch/master/graph/badge.svg
[codecov-url]: https://codecov.io/gh/slackapi/python-slackclient
[contact-image]: https://img.shields.io/badge/contact-support-green.svg
[contact-url]: https://slack.com/support
[api-docs]: https://api.slack.com
[slackclientv1]: https://github.com/slackapi/python-slackclient/
[api-methods]: https://api.slack.com/methods
[rtm-docs]: https://api.slack.com/rtm
[events-docs]: https://api.slack.com/events-api
[events-sdk]: https://github.com/slackapi/python-slack-events-api
[message-event]: https://api.slack.com/events/message
[python-slack-events-api]: https://github.com/slackapi/python-slack-events-api
[pypi]: https://pypi.python.org/pypi
[pipenv]: https://pypi.org/project/pipenv/
[gh-issues]: https://github.com/slackapi/python-slackclient/issues
[bd-hangout]: http://community.botkit.ai/
[dev-roadmap]: https://github.com/slackapi/python-slackclient/wiki/Slack-Python-SDK-Roadmap
[migration-guide]: https://api.slack.com
[files.upload]: https://api.slack.com/methods/files.upload
[auth-guide]: docs/auth.md
[basic-usage]: docs/basic_usage.md
[aiohttp]: https://aiohttp.readthedocs.io/