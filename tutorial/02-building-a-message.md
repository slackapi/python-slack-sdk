# Building a message

The code for this step is available [here](PythOnBoardingBot/onboarding_tutorial.py).

> 💡 **[Block Kit](https://docs.slack.dev/block-kit/)** is a UI framework for Slack apps that offers a balance of control and flexibility when building experiences in messages and other surfaces. Customize the order and appearance of information and guide users through your app's capabilities by composing, updating, sequencing, and stacking blocks — reusable components that work almost everywhere in Slack. You can experiment and prototype with Block Kit using the [Block Kit Builder](https://api.slack.com/tools/block-kit-builder).

We're going to be using Block Kit to build our onboarding tutorial messages.

With Block Kit, we can create a message in Slack that looks like this:
<img width="787" alt="Onboarding Message" src="https://user-images.githubusercontent.com/3329665/56854465-b84a6f80-68eb-11e9-9625-f45ac2d2fe18.png">

By sending the following json payload:

```Python
{
    "channel": "D0123456",
    "username": "pythonboardingbot",
    "icon_emoji": ":robot_face:",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Welcome to Slack! :wave: We're so glad you're here. :blush:\n\n*Get started by completing the steps below:*",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":white_large_square: *Add an emoji reaction to this message* :thinking_face:\nYou can quickly respond to any message on Slack with an emoji reaction. Reactions can be used for any purpose: voting, checking off to-do items, showing excitement.",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": " :information_source: *<https://get.slack.help/hc/en-us/articles/206870317-Emoji-reactions|Learn How to Use Emoji Reactions>*",
                }
            ],
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": ":white_large_square: *Pin this message* :round_pushpin:\nImportant messages and files can be pinned to the details pane in any channel or direct message, including group messages, for easy reference.",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": " :information_source: *<https://get.slack.help/hc/en-us/articles/205239997-Pinning-messages-and-files|Learn How to Pin a Message>*",
                }
            ],
        },
    ],
}
```

To make this simpler, more pleasant and more productive we'll create a class that's responsible for building it. We'll also store the state of which tasks were completed so that it's easy to update existing messages.

- Create a file called `onboarding_tutorial.py`.
- 🏁Add the following code into it:

```Python
class OnboardingTutorial:
    """Constructs the onboarding message and stores the state of which tasks were completed."""

    WELCOME_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Welcome to Slack! :wave: We're so glad you're here. :blush:\n\n"
                "*Get started by completing the steps below:*"
            ),
        },
    }
    DIVIDER_BLOCK = {"type": "divider"}

    def __init__(self, channel):
        self.channel = channel
        self.username = "pythonboardingbot"
        self.icon_emoji = ":robot_face:"
        self.timestamp = ""
        self.reaction_task_completed = False
        self.pin_task_completed = False

    def get_message_payload(self):
        return {
            "ts": self.timestamp,
            "channel": self.channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "blocks": [
                self.WELCOME_BLOCK,
                self.DIVIDER_BLOCK,
                *self._get_reaction_block(),
                self.DIVIDER_BLOCK,
                *self._get_pin_block(),
            ],
        }

    def _get_reaction_block(self):
        task_checkmark = self._get_checkmark(self.reaction_task_completed)
        text = (
            f"{task_checkmark} *Add an emoji reaction to this message* :thinking_face:\n"
            "You can quickly respond to any message on Slack with an emoji reaction."
            "Reactions can be used for any purpose: voting, checking off to-do items, showing excitement."
        )
        information = (
            ":information_source: *<https://get.slack.help/hc/en-us/articles/206870317-Emoji-reactions|"
            "Learn How to Use Emoji Reactions>*"
        )
        return self._get_task_block(text, information)

    def _get_pin_block(self):
        task_checkmark = self._get_checkmark(self.pin_task_completed)
        text = (
            f"{task_checkmark} *Pin this message* :round_pushpin:\n"
            "Important messages and files can be pinned to the details pane in any channel or"
            " direct message, including group messages, for easy reference."
        )
        information = (
            ":information_source: *<https://get.slack.help/hc/en-us/articles/205239997-Pinning-messages-and-files"
            "|Learn How to Pin a Message>*"
        )
        return self._get_task_block(text, information)

    @staticmethod
    def _get_checkmark(task_completed: bool) -> str:
        if task_completed:
            return ":white_check_mark:"
        return ":white_large_square:"

    @staticmethod
    def _get_task_block(text, information):
        return [
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": information}]},
        ]
```

---

**Next section: [03 - Responding to Slack events](03-responding-to-slack-events.md).**

**Previous section: [01 - Creating the Slack app](01-creating-the-slack-app.md).**

**Back to the [Table of contents](README.md#table-of-contents).**
