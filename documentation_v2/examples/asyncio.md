# Usage with asyncio

Here is a simple example showing how to use the new `WebClient` in an asynchronous way.

To run this example you will need to prepare your `SLACK_TOKEN`, ideally a Bot token so you do not have to deal with permissions scopes.
Id of a slack channel (`MEMBERS_CHANNEL`) with users who should receive this message. You can simply obdatin this by using a browser slack client and copy the ID from a url, eg. `https://<your-workspace>.slack.com/messages/<channel ID>/`

```python
import asyncio
import os

import slack

SLACK_TOKEN = <your slack token>
MEMBERS_CHANNEL = <channel ID>

# instantiate WebClient in async mode
sc = slack.WebClient(SLACK_TOKEN, run_async=True)


async def send_message(user_id, message):
    """Send a direct message to the slack user."""
    response = await sc.conversations_open(users=[user_id])
    msg_post_response = await sc.chat_postMessage(
        channel=response["channel"]["id"], text=message
    )
    return user_id, msg_post_response


async def send_pm_to_channel_members(channel_id):
    """Send a direct message to all users of specific channel."""
    # get all members of the channel
    members_response = await sc.conversations_members(channel=channel_id)
    special_message = (
        f"This message is supposed to be sent to users: {members_response['members']}"
    )
    # create coroutines and gather the responses
    responses = await asyncio.gather(
        *(
            send_message(user_id, special_message)
            for user_id in members_response["members"]
        )
    )
    return responses


def main():
    # run the async main function
    result = asyncio.run(send_pm_to_channel_members(MEMBERS_CHANNEL))
    print(result)


if __name__ == "__main__":
    main()
```
