import os
import logging
import slack
import ssl as ssl_lib
import certifi
from onboarding_message import OnboardingMessage

# For simplicity we'll store our bot data with the following data structure.
# onboarding_messages = {'team_id': {"user_id": "onboarding_message_ts"}}
onboarding_messages_sent = {}


def store_message_sent(
    team_id: str, user_id: str, onboarding_message: OnboardingMessage
):
    """Store the message sent in onboarding_messages_sent."""
    if team_id not in onboarding_messages_sent:
        onboarding_messages_sent[team_id] = {}
    onboarding_messages_sent[team_id][user_id] = onboarding_message


# ================ Team Join Event =============== #
# When the user first joins a team, the type of the event will be 'team_join'.
# Here we'll link the onboarding_message callback to the 'team_join' event.
@slack.RTMClient.run_on(event="team_join")
def onboarding_message(**payload):
    """Create and send an onboarding welcome message to new users. Save the
    time stamp of this message so we can update this message in the future.
    """
    # Get the id of the Slack team associated with the incoming event
    team_id = payload["data"]["team_id"]
    # Get the id of the Slack user associated with the incoming event
    user_id = payload["data"]["event"]["user"]["id"]
    # Get WebClient so you can communicate back to Slack.
    web_client = payload["web_client"]

    # Open a DM to send a welcome message.
    dm_channel_id = web_client.im_open(user=user_id)["channel"]["id"]

    # Post the onboarding message.
    onboarding_message = OnboardingMessage(dm_channel_id)
    response = web_client.chat_postMessage(**onboarding_message)
    # We'll save the timestamp of the message we've just posted so
    # we can use it to update the message after a user
    # has completed an onboarding task.
    onboarding_message.timestamp = response["ts"]
    store_message_sent(team_id, user_id, onboarding_message)


# ============= Reaction Added Events ============= #
# When a users adds an emoji reaction to the onboarding message,
# the type of the event will be 'reaction_added'.
# Here we'll link the update_emoji callback to the 'reaction_added' event.
@slack.RTMClient.run_on(event="reaction_added")
def update_emoji(**payload):
    """Update onboarding welcome message after recieving a "reaction_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    web_client = payload["web_client"]
    team_id = payload["data"]["team_id"]
    user_id = payload["data"]["event"]["user"]

    # Get the original message sent.
    message = onboarding_messages_sent[team_id][user_id]

    # Mark the reaction task as completed.
    message.reaction_task_completed = True

    # Update the message in Slack
    updated_message = web_client.chat_update(**message)

    # Update the timestamp saved on the message object
    message.timestamp = updated_message["ts"]


# =============== Pin Added Events ================ #
# When a users pins a message the type of the event will be 'pin_added'.
# Here we'll link the update_pin callback to the 'reaction_added' event.
@slack.RTMClient.run_on(event="pin_added")
def update_pin(**payload):
    """Update onboarding welcome message after recieving a "pin_added"
    event from Slack. Update timestamp for welcome message as well.
    """
    web_client = payload["web_client"]
    team_id = payload["data"]["team_id"]
    user_id = payload["data"]["event"]["user"]

    # Get the original message sent.
    message = onboarding_messages_sent[team_id][user_id]

    # Mark the reaction task as completed.
    message.pin_task_completed = True

    # Update the message in Slack
    updated_message = web_client.chat_update(**message)

    # Update the timestamp saved on the message object
    message.timestamp = updated_message["ts"]


# ============== Message Events ============= #
# When a user shares a message, the event type will be 'message'.
# Here we'll link the update_share callback to the 'message' event.
@slack.RTMClient.run_on(event="message")
def update_share(**payload):
    """Update onboarding welcome message after recieving a "message"
    event from Slack. We'll need to check that the message we're
    looking for has been shared by looking for the "is_shared" attribute.
    """
    data = payload["data"]
    web_client = payload["web_client"]

    if (
        "attachements" in data["event"]
        and "is_share" in data["event"]["attachments"][0]
    ):
        team_id = data["team_id"]
        user_id = data["event"]["user"]

        # Get the original message sent.
        message = onboarding_messages_sent[team_id][user_id]

        # Mark the share task as completed.
        message.share_task_completed = True

        # Update the message in Slack
        updated_message = web_client.chat_update(**message)

        # Update the timestamp saved on the message object
        message.timestamp = updated_message["ts"]


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    slack_token = os.environ["SLACK_XOXB_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token, ssl=ssl_context)
    rtm_client.start()
