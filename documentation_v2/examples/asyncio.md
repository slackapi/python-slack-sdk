# Usage with asyncio

Here is a simple example how to use new `WebClient` in asynchronous way.

```python
import asyncio
from slack import WebClient
import os

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
MEMBERS_CHANNEL = os.environ.get('MEMBERS_CHANNEL')

SC = WebClient(
    SLACK_TOKEN,
    run_async=True
)


async def send_message(user_id, message):
    response = await SC.conversations_open(users=[user_id])
    send_response = await SC.chat_postMessage(
        channel=response["channel"]["id"], text=message,
    )
    return user_id, send_response


async def send_pm_to_channel_members():
    members = await SC.conversations_members(channel=MEMBERS_CHANNEL)
    special_message = f"This message is supposed to be sent to users: {members['members']}"
    responses = await asyncio.gather(*(send_message(user_id, special_message) for user_id in members['members']))
    return responses


def main():
    result = asyncio.run(send_pm_to_channel_members())
    print(result)


if __name__ == '__main__':
    main()

```
