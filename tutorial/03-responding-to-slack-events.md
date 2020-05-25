# Responding to Slack events

The code for this step is available [here](PythOnBoardingBot).

## Install the dependencies

> 💡 **[“Requirements files”](https://pip.pypa.io/en/stable/user_guide/#id12)** are files containing a list of items to be installed using pip install. Details on the format of the files are here: [Requirements File Format](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).

- In the root directory create a "requirements.txt" file.
- Add the following contents to that file and save the file.

```
slackclient>=2.0.0
slackeventsapi>=2.1.0
Flask>=1.1.2
```

> 💡 **[Certifi](https://github.com/certifi/python-certifi)** is a carefully curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. It has been extracted from the Requests project.

- Next you can install those dependencies by running the following command from your terminal:

```
$ pip3 install -r requirements.txt
-> Successfully installed slackclient-2.0.0
```

## Creating the app

- Create an `app.py` file to run the app.

The first thing we'll need to do is import the code our app needs to run.

- In `app.py` add the following code:

```Python
import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from onboarding_tutorial import OnboardingTutorial
```

- Next, let's create a Flask server and initialize the WebClient and SlackEventAdapter. Add the following lines to `app.py`:

```Python
# Initialize a Flask app to host the events adapter
app = Flask(__name__)
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app)

# Initialize a Web API client
slack_web_client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
```

Next we'll need our app to store some data. For simplicity we'll store our app data in-memory with the following data structure: `{"channel": {"user_id": OnboardingTutorial}}`.

- Add the following line under the previous code:

```Python
onboarding_tutorials_sent = {}
```

Let's add a function that's responsible for creating and sending the onboarding welcome message to new users. We'll also save the time stamp of the message when it's posted so we can update this message in the future.

- Add the following lines of code to `app.py`:

```Python
def start_onboarding(user_id: str, channel: str):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = slack_web_client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial
```

**Note:** We're using the `WebClient` to send messages into Slack.

> 💡 **[WebClient](/slack/web/client.py)** A WebClient allows apps to communicate with the Slack Platform's Web API. This client handles constructing and sending HTTP requests to Slack as well as parsing any responses received into a `SlackResponse` dictionary-like object.

### Responding to events in Slack

When events occur in Slack there are two primary ways to be notified about them. We can send you an HTTP Request through our Events API (preferred) or you can stream events through a websocket connection with our RTM API. The RTM API is only recommended if you're behind a firewall and cannot receive incoming web requests from Slack.

> ⚠️ The RTM API isn't available for default Slack apps. If you need to use RTM (possibly due to corporate firewall limitations), you can do so by creating a [classic Slack app](https://api.slack.com/apps?new_classic_app=1). If you have an existing RTM app, you can continue to use its associated tokens. You can read more [in the documentation](https://slack.dev/python-slackclient/real_time_messaging.html).

In this tutorial we'll be using the Events API and the [SlackEventAdapter](https://github.com/slackapi/python-slack-events-api). If you need access to the RTM API, you can access it [via the `RTMClient`](https://slack.dev/python-slackclient/real_time_messaging.html).

Back to our application, it's time to link our onboarding functionality to Slack events.

- Add the following lines of code to `app.py`:

```Python
# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.
@slack_events_adapter.on("team_join")
def onboarding_message(payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    event = payload.get("event", {})

    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user", {}).get("id")

    # Open a DM with the new user.
    response = slack_web_client.im_open(user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel)


# ============= Reaction Added Events ============= #
# When a users adds an emoji reaction to the onboarding message,
# the type of the event will be 'reaction_added'.
# Here we'll link the update_emoji callback to the 'reaction_added' event.
@slack_events_adapter.on("reaction_added")
def update_emoji(payload):
    """Update the onboarding welcome message after receiving a "reaction_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    event = payload.get("event", {})

    channel_id = event.get("item", {}).get("channel")
    user_id = event.get("user")

    if channel_id not in onboarding_tutorials_sent:
        return

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

    # Mark the reaction task as completed.
    onboarding_tutorial.reaction_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = slack_web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# =============== Pin Added Events ================ #
# When a users pins a message the type of the event will be 'pin_added'.
# Here we'll link the update_pin callback to the 'reaction_added' event.
@slack_events_adapter.on("pin_added")
def update_pin(payload):
    """Update the onboarding welcome message after receiving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    event = payload.get("event", {})

    channel_id = event.get("channel_id")
    user_id = event.get("user")

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

    # Mark the pin task as completed.
    onboarding_tutorial.pin_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = slack_web_client.chat_update(**message)

    # Update the timestamp saved on the onboarding tutorial object
    onboarding_tutorial.timestamp = updated_message["ts"]


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@slack_events_adapter.on("message")
def message(payload):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    event = payload.get("event", {})

    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")


    if text and text.lower() == "start":
        return start_onboarding(user_id, channel_id)
```

Finally, we need to make our app runnable.

- 🏁 Add the following lines of code to the end of `app.py` and run `FLASK_ENV=development python app.py`.

```Python
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.run(port=3000)
```

**Note:** When running in a virtual environment you often need to specify the location of the SSL Certificate(`cacert.pem`). To make this easy we use Certifi's built-in `where()` function to locate the installed certificate authority (CA) bundle.

```python
import ssl as ssl_lib
import certifi

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
```

**Final Note:** If you're interested in learning how to modify this app to run asynchronously I've adapted this code as such [here](PythOnBoardingBot/async_app.py).

---

**Next section: [04 - Running the app](04-running-the-app.md).**

**Previous section: [02 - Building a message](02-building-a-message.md).**

**Back to the [Table of contents](README.md#table-of-contents).**
