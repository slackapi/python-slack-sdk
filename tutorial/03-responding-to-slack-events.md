# Responding to Slack events

The code for this step is available [here](PythOnBoardingBot).

## Install the dependencies

> 💡 **["Requirements files"](https://pip.pypa.io/en/stable/user_guide/#id12)** are files containing a list of items to be installed using pip install. Details on the format of the files are here: [Requirements File Format](https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format).

- In the root directory create a "requirements.txt" file.
- Add the following contents to that file and save the file.

```
slack_sdk>=3.0
slack_bolt>=1.6.1
certifi
```

> 💡 **[Certifi](https://github.com/certifi/python-certifi)** is a carefully curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts. It has been extracted from the Requests project.

- Next you can install those dependencies by running the following command from your terminal:

```
$ pip3 install -r requirements.txt
-> Successfully installed slack_sdk-3.0.0
```

## Creating the app

- Create an `app.py` file to run the app.

The first thing we'll need to do is import the code our app needs to run.

- In `app.py` add the following code:

```Python
import logging
from slack_bolt import App
from slack_sdk.web import WebClient
from onboarding_tutorial import OnboardingTutorial
```

- Next, create a Bolt for Python application. Add the following line to `app.py`:

```Python
app = App()
```

Next we'll need our app to store some data. For simplicity we'll store our app data in-memory with the following data structure: `{"channel": {"user_id": OnboardingTutorial}}`.

- Add the following line under the previous code:

```Python
onboarding_tutorials_sent = {}
```

Let's add a function that's responsible for creating and sending the onboarding welcome message to new users. We'll also save the time stamp of the message when it's posted so we can update this message in the future.

- Add the following lines of code to `app.py`:

```Python
def start_onboarding(user_id: str, channel: str, client: WebClient):
    # Create a new onboarding tutorial.
    onboarding_tutorial = OnboardingTutorial(channel)

    # Get the onboarding message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the onboarding message in Slack
    response = client.chat_postMessage(**message)

    # Capture the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_tutorial.timestamp = response["ts"]

    # Store the message sent in onboarding_tutorials_sent
    if channel not in onboarding_tutorials_sent:
        onboarding_tutorials_sent[channel] = {}
    onboarding_tutorials_sent[channel][user_id] = onboarding_tutorial
```

### Responding to events in Slack

When events occur in Slack there are two primary ways to be notified about them. We can send you an [HTTP Request through our Events API](https://docs.slack.dev/apis/events-api/), or you can stream events through a WebSocket connection with our [Socket Mode](https://docs.slack.dev/apis/events-api/using-socket-mode/) API. If you're behind a firewall and cannot receive incoming web requests from Slack, we recommend going with Socket Mode.

In this tutorial we'll be using the Events API and the [Bolt for Python](https://github.com/slackapi/bolt-python).

Back to our application, it's time to link our onboarding functionality to Slack events.

- Add the following lines of code to `app.py`:

```Python
# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.

# Note: Bolt provides a WebClient instance as an argument to the listener function
# we've defined here, which we then use to access Slack Web API methods like conversations_open.
# For more info, checkout: https://docs.slack.dev/tools/bolt-python/concepts/message-listening
@app.event("team_join")
def onboarding_message(event, client):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get the id of the Slack user associated with the incoming event
    user_id = event.get("user", {}).get("id")

    # Open a DM with the new user.
    response = client.conversations_open(users=user_id)
    channel = response["channel"]["id"]

    # Post the onboarding message.
    start_onboarding(user_id, channel, client)


# ============= Reaction Added Events ============= #
# When a users adds an emoji reaction to the onboarding message,
# the type of the event will be 'reaction_added'.
# Here we'll link the update_emoji callback to the 'reaction_added' event.
@app.event("reaction_added")
def update_emoji(event, client):
    """Update the onboarding welcome message after receiving a "reaction_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    # Get the ids of the Slack user and channel associated with the incoming event
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
    updated_message = client.chat_update(**message)


# =============== Pin Added Events ================ #
# When a users pins a message the type of the event will be 'pin_added'.
# Here we'll link the update_pin callback to the 'pin_added' event.
@app.event("pin_added")
def update_pin(event, client):
    """Update the onboarding welcome message after receiving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    # Get the ids of the Slack user and channel associated with the incoming event
    channel_id = event.get("channel_id")
    user_id = event.get("user")

    # Get the original tutorial sent.
    onboarding_tutorial = onboarding_tutorials_sent[channel_id][user_id]

    # Mark the pin task as completed.
    onboarding_tutorial.pin_task_completed = True

    # Get the new message payload
    message = onboarding_tutorial.get_message_payload()

    # Post the updated message in Slack
    updated_message = client.chat_update(**message)


# ============== Message Events ============= #
# When a user sends a DM, the event type will be 'message'.
# Here we'll link the message callback to the 'message' event.
@app.event("message")
def message(event, client):
    """Display the onboarding welcome message after receiving a message
    that contains "start".
    """
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    if text and text.lower() == "start":
        return start_onboarding(user_id, channel_id, client)
```

Finally, we need to make our app runnable.

- 🏁 Add the following lines of code to the end of `app.py`.

```Python
if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    app.start(3000)
```

**Note:** When running in a virtual environment you often need to specify the location of the SSL Certificate(`cacert.pem`). To make this easy we use Certifi's built-in `where()` function to locate the installed certificate authority (CA) bundle.

```python
import ssl as ssl_lib
import certifi

ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
```

---

**Next section: [04 - Running the app](04-running-the-app.md).**

**Previous section: [02 - Building a message](02-building-a-message.md).**

**Back to the [Table of contents](README.md#table-of-contents).**
