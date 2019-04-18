"""A Python module for iteracting with Slack's Web API."""

# Standard Imports
import functools

# Internal Imports
from slack.web.base_client import BaseClient
import slack.errors as e


def xoxp_token_only(api_method):
    """Ensures that an xoxp token is used when the specified method is called.

    Args:
        api_method (func): The api method that only works with xoxp tokens.
    Raises:
        BotUserAccessError: If the API method is called with a Bot User OAuth Access Token.
    """

    def xoxp_token_only_decorator(func):
        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            client = args[0]
            # The first argument is 'slack.web.client.WebClient' aka 'self'.
            if client.token.startswith("xoxb"):
                method_name = api_method.__name__
                msg = "The API method '{}' cannot be called with a Bot Token.".format(
                    method_name
                )
                raise e.BotUserAccessError(msg)
            return func(*args, **kwargs)

        return func_wrapper

    return xoxp_token_only_decorator(api_method)


class WebClient(BaseClient):
    """A WebClient allows apps to communicate with the Slack Platform's Web API.

    The Slack Web API is an interface for querying information from
    and enacting change in a Slack workspace.

    This client handles constructing and sending HTTP requests to Slack
    as well as parsing any responses received into a `SlackResponse`.

    Attributes:
        token (str): A string specifying an xoxp or xoxb token.
        use_session (bool): An boolean specifying if the client
            should take advantage of connection pooling.
            Default is True.
        base_url (str): A string representing the Slack API base URL.
            Default is 'https://www.slack.com/api/'
        proxies (dict): If you need to use a proxy, you can pass a dict
            of proxy configs. e.g. {'https': "https://127.0.0.1:8080"}
            Default is None.
        timeout (int): The maximum number of seconds the client will wait
            to connect and receive a response from Slack.
            Default is 30 seconds.

    Methods:
        api_call: Constructs a request and executes the API call to Slack.

    Example of recommended usage:
    ```python
        import slack

        client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
        response = client.chat_postMessage(
            channel='#random',
            text="Hello world!")
        assert response["ok"]
        assert response["message"]["text"] == "Hello world!"
    ```

    Example manually creating an API request:
    ```python
        import slack

        client = slack.WebClient(token=os.environ['SLACK_API_TOKEN'])
        response = client.api_call(
            api_method='chat.postMessage',
            json={'channel': '#random','text': "Hello world!"}
        )
        assert response["ok"]
        assert response["message"]["text"] == "Hello world!"
    ```

    Note:
        Any attributes or methods prefixed with _underscores are
        intended to be "private" internal use only. They may be changed or
        removed at anytime.
    """

    def api_test(self, **kwargs):
        """Checks API calling code."""
        return self.api_call("api.test", json=kwargs)

    def auth_revoke(self, **kwargs):
        """Revokes a token."""
        return self.api_call("auth.revoke", http_verb="GET", params=kwargs)

    def auth_test(self, **kwargs):
        """Checks authentication & identity."""
        return self.api_call("auth.test", json=kwargs)

    def bots_info(self, **kwargs):
        """Gets information about a bot user."""
        return self.api_call("bots.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def channels_archive(self, **kwargs):
        """Archives a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("channels.archive", json=kwargs)

    @xoxp_token_only
    def channels_create(self, **kwargs):
        """Creates a channel.

        Args:
            name (str): The name of the channel. e.g. 'mychannel'
        """
        return self.api_call("channels.create", json=kwargs)

    def channels_history(self, **kwargs):
        """Fetches history of messages and events from a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("channels.history", http_verb="GET", params=kwargs)

    def channels_info(self, **kwargs):
        """Gets information about a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("channels.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def channels_invite(self, **kwargs):
        """Invites a user to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        return self.api_call("channels.invite", json=kwargs)

    @xoxp_token_only
    def channels_join(self, **kwargs):
        """Joins a channel, creating it if needed.

        Args:
            name (str): The channel name. e.g. '#general'
        """
        return self.api_call("channels.join", json=kwargs)

    @xoxp_token_only
    def channels_kick(self, **kwargs):
        """Removes a user from a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        return self.api_call("channels.kick", json=kwargs)

    @xoxp_token_only
    def channels_leave(self, **kwargs):
        """Leaves a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("channels.leave", json=kwargs)

    def channels_list(self, **kwargs):
        """Lists all channels in a Slack team."""
        return self.api_call("channels.list", http_verb="GET", params=kwargs)

    def channels_mark(self, **kwargs):
        """Sets the read cursor in a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        return self.api_call("channels.mark", json=kwargs)

    @xoxp_token_only
    def channels_rename(self, **kwargs):
        """Renames a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        return self.api_call("channels.rename", json=kwargs)

    def channels_replies(self, **kwargs):
        """Retrieve a thread of messages posted to a channel

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        return self.api_call("channels.replies", http_verb="GET", params=kwargs)

    def channels_setPurpose(self, **kwargs):
        """Sets the purpose for a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        return self.api_call("channels.setPurpose", json=kwargs)

    def channels_setTopic(self, **kwargs):
        """Sets the topic for a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        return self.api_call("channels.setTopic", json=kwargs)

    @xoxp_token_only
    def channels_unarchive(self, **kwargs):
        """Unarchives a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("channels.unarchive", json=kwargs)

    def chat_delete(self, **kwargs):
        """Deletes a message.

        Args:
            channel (str): Channel containing the message to be deleted. e.g. 'C1234567890'
            ts (str): Timestamp of the message to be deleted. e.g. '1234567890.123456'
        """
        return self.api_call("chat.delete", json=kwargs)

    def chat_getPermalink(self, **kwargs):
        """Retrieve a permalink URL for a specific extant message

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            message_ts (str): The timestamp. e.g. '1234567890.123456'
        """
        return self.api_call("chat.getPermalink", http_verb="GET", params=kwargs)

    def chat_meMessage(self, **kwargs):
        """Share a me message into a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            text (str): The message you'd like to share. e.g. 'Hello world'
        """
        return self.api_call("chat.meMessage", json=kwargs)

    def chat_postEphemeral(self, **kwargs):
        """Sends an ephemeral message to a user in a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The id of user who should see the message. e.g. 'U0BPQUNTA'
            text (str): The message you'd like to share. e.g. 'Hello world'
                text is not required when presenting attachments.
            attachments (list): A dictionary list of attachments.
                attachments is required when not presenting text.
                e.g. [{"pretext": "pre-hello", "text": "text-world"}]
        """
        return self.api_call("chat.postEphemeral", json=kwargs)

    def chat_postMessage(self, **kwargs):
        """Sends a message to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            text (str): The message you'd like to share. e.g. 'Hello world'
                text is not required when presenting attachments.
            attachments (list): A dictionary list of attachments.
                attachments is required when not presenting text.
                e.g. [{"pretext": "pre-hello", "text": "text-world"}]
        """
        return self.api_call("chat.postMessage", json=kwargs)

    @xoxp_token_only
    def chat_unfurl(self, **kwargs):
        """Provide custom unfurl behavior for user-posted URLs.

        Args:
            channel (str): The Channel ID of the message. e.g. 'C1234567890'
            ts (str): Timestamp of the message to add unfurl behavior to. e.g. '1234567890.123456'
            unfurls (dict): a dict of the specific URLs you're offering an unfurl for.
                e.g. {"https://example.com/": {"text": "Every day is the test."}}
        """
        return self.api_call("chat.unfurl", json=kwargs)

    def chat_update(self, **kwargs):
        """Updates a message in a channel.

        Args:
            channel (str): The channel containing the message to be updated. e.g. 'C1234567890'
            ts (str): Timestamp of the message to be updated. e.g. '1234567890.123456'
            text (str): New text for the message, using the default formatting rules.
                text is not required when presenting attachments. e.g. 'Hello world'
            attachments (list): A dictionary list of attachments.
                attachments is required when not presenting text.
                e.g. [{"pretext": "pre-hello", "text": "text-world"}]
        """
        return self.api_call("chat.update", json=kwargs)

    @xoxp_token_only
    def conversations_archive(self, **kwargs):
        """Archives a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.archive", json=kwargs)

    def conversations_close(self, **kwargs):
        """Closes a direct message or multi-person direct message.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.close", json=kwargs)

    @xoxp_token_only
    def conversations_create(self, **kwargs):
        """Initiates a public or private channel-based conversation

        Args:
            name (str): The name of the channel. e.g. 'mychannel'
        """
        return self.api_call("conversations.create", json=kwargs)

    def conversations_history(self, **kwargs):
        """Fetches a conversation's history of messages and events.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.history", http_verb="GET", params=kwargs)

    def conversations_info(self, **kwargs):
        """Retrieve information about a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def conversations_invite(self, **kwargs):
        """Invites users to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            users (list): An list of user id's to invite. e.g. ['U2345678901', 'U3456789012']
        """
        return self.api_call("conversations.invite", json=kwargs)

    @xoxp_token_only
    def conversations_join(self, **kwargs):
        """Joins an existing conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.join", json=kwargs)

    @xoxp_token_only
    def conversations_kick(self, **kwargs):
        """Removes a user from a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The id of the user to kick. e.g. 'U2345678901'
        """
        return self.api_call("conversations.kick", json=kwargs)

    @xoxp_token_only
    def conversations_leave(self, **kwargs):
        """Leaves a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.leave", json=kwargs)

    def conversations_list(self, **kwargs):
        """Lists all channels in a Slack team."""
        return self.api_call("conversations.list", http_verb="GET", params=kwargs)

    def conversations_members(self, **kwargs):
        """Retrieve members of a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.members", http_verb="GET", params=kwargs)

    def conversations_open(self, **kwargs):
        """Opens or resumes a direct message or multi-person direct message."""
        return self.api_call("conversations.open", json=kwargs)

    @xoxp_token_only
    def conversations_rename(self, **kwargs):
        """Renames a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        return self.api_call("conversations.rename", json=kwargs)

    def conversations_replies(self, **kwargs):
        """Retrieve a thread of messages posted to a conversation

        Args:
            channel (str): Conversation ID to fetch thread from. e.g. 'C1234567890'
            ts (str): Unique identifier of a thread's parent message. e.g. '1234567890.123456'
        """
        return self.api_call("conversations.replies", http_verb="GET", params=kwargs)

    def conversations_setPurpose(self, **kwargs):
        """Sets the purpose for a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        return self.api_call("conversations.setPurpose", json=kwargs)

    def conversations_setTopic(self, **kwargs):
        """Sets the topic for a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        return self.api_call("conversations.setTopic", json=kwargs)

    @xoxp_token_only
    def conversations_unarchive(self, **kwargs):
        """Reverses conversation archival.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("conversations.unarchive", json=kwargs)

    def dialog_open(self, **kwargs):
        """Open a dialog with a user.

        Args:
            dialog (dict): A dictionary of dialog arguments.
                {
                    "callback_id": "46eh782b0",
                    "title": "Request something",
                    "submit_label": "Request",
                    "state": "Max",
                    "elements": [
                        {
                            "type": "text",
                            "label": "Origin",
                            "name": "loc_origin"
                        },
                        {
                            "type": "text",
                            "label": "Destination",
                            "name": "loc_destination"
                        }
                    ]
                }
            trigger_id (str): The trigger id of a recent message interaction.
                e.g. '12345.98765.abcd2358fdea'
        """
        return self.api_call("dialog.open", json=kwargs)

    @xoxp_token_only
    def dnd_endDnd(self, **kwargs):
        """Ends the current user's Do Not Disturb session immediately."""
        return self.api_call("dnd.endDnd", json=kwargs)

    @xoxp_token_only
    def dnd_endSnooze(self, **kwargs):
        """Ends the current user's snooze mode immediately."""
        return self.api_call("dnd.endSnooze", json=kwargs)

    def dnd_info(self, **kwargs):
        """Retrieves a user's current Do Not Disturb status."""
        return self.api_call("dnd.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def dnd_setSnooze(self, **kwargs):
        """Turns on Do Not Disturb mode for the current user, or changes its duration.

        Args:
            num_minutes (int): The snooze duration. e.g. 60
        """
        return self.api_call("dnd.setSnooze", http_verb="GET", params=kwargs)

    def dnd_teamInfo(self, **kwargs):
        """Retrieves the Do Not Disturb status for users on a team."""
        return self.api_call("dnd.teamInfo", http_verb="GET", params=kwargs)

    def emoji_list(self, **kwargs):
        """Lists custom emoji for a team."""
        return self.api_call("emoji.list", http_verb="GET", params=kwargs)

    def files_comments_add(self, **kwargs):
        """Add a comment to an existing file.

        Args:
            comment (str): The body of the comment.
                e.g. 'Everyone should take a moment to read this file.'
            file (str): The file id. e.g. 'F1234467890'
        """
        return self.api_call("files.comments.add", json=kwargs)

    def files_comments_delete(self, **kwargs):
        """Deletes an existing comment on a file.

        Args:
            file (str): The file id. e.g. 'F1234467890'
            id (str): The file comment id. e.g. 'Fc1234567890'
        """
        return self.api_call("files.comments.delete", json=kwargs)

    def files_comments_edit(self, **kwargs):
        """Edit an existing file comment.

        Args:
            comment (str): The body of the comment.
                e.g. 'Everyone should take a moment to read this file.'
            file (str): The file id. e.g. 'F1234467890'
            id (str): The file comment id. e.g. 'Fc1234567890'
        """
        return self.api_call("files.comments.edit", json=kwargs)

    def files_delete(self, **kwargs):
        """Deletes a file.

        Args:
            id (str): The file id. e.g. 'F1234467890'
        """
        return self.api_call("files.delete", json=kwargs)

    def files_info(self, **kwargs):
        """Gets information about a team file.

        Args:
            id (str): The file id. e.g. 'F1234467890'
        """
        return self.api_call("files.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def files_list(self, **kwargs):
        """Lists & filters team files."""
        return self.api_call("files.list", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def files_revokePublicURL(self, **kwargs):
        """Revokes public/external sharing access for a file

        Args:
            id (str): The file id. e.g. 'F1234467890'
        """
        return self.api_call("files.revokePublicURL", json=kwargs)

    @xoxp_token_only
    def files_sharedPublicURL(self, **kwargs):
        """Enables a file for public/external sharing.

        Args:
            id (str): The file id. e.g. 'F1234467890'
        """
        return self.api_call("files.sharedPublicURL", json=kwargs)

    def files_upload(self, file=None, content=None, **kwargs):
        """Uploads or creates a file.


        Args:
            file (str): Supply a file path.
                when you'd like to upload a specific file. e.g. 'dramacat.gif'
            content (str): Supply content when you'd like to create an
                editable text file containing the specified text. e.g. 'launch plan'
        Raises:
            SlackRequestError: If niether or both the `file` and `content` args are specified.
        """
        if file is None and content is None:
            raise e.SlackRequestError("The file or content argument must be specified.")
        if file is not None and content is not None:
            raise e.SlackRequestError(
                "You cannot specify both the file and the content argument."
            )

        if file:
            with open(file, "rb") as f:
                return self.api_call("files.upload", files={"file": f}, data=kwargs)
        elif content:
            data = kwargs.copy()
            data.update({"content": content})
            return self.api_call("files.upload", data=data)

    @xoxp_token_only
    def groups_archive(self, **kwargs):
        """Archives a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("groups.archive", json=kwargs)

    @xoxp_token_only
    def groups_create(self, **kwargs):
        """Creates a private channel.

        Args:
            name (str): The name of the private group. e.g. 'mychannel'
        """
        return self.api_call("groups.create", json=kwargs)

    @xoxp_token_only
    def groups_createChild(self, **kwargs):
        """Clones and archives a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        return self.api_call("groups.createChild", http_verb="GET", params=kwargs)

    def groups_history(self, **kwargs):
        """Fetches history of messages and events from a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        return self.api_call("groups.history", http_verb="GET", params=kwargs)

    def groups_info(self, **kwargs):
        """Gets information about a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        return self.api_call("groups.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def groups_invite(self, **kwargs):
        """Invites a user to a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        return self.api_call("groups.invite", json=kwargs)

    @xoxp_token_only
    def groups_kick(self, **kwargs):
        """Removes a user from a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        return self.api_call("groups.kick", json=kwargs)

    @xoxp_token_only
    def groups_leave(self, **kwargs):
        """Leaves a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        return self.api_call("groups.leave", json=kwargs)

    def groups_list(self, **kwargs):
        """Lists private channels that the calling user has access to."""
        return self.api_call("groups.list", http_verb="GET", params=kwargs)

    def groups_mark(self, **kwargs):
        """Sets the read cursor in a private channel.

        Args:
            channel (str): Private channel to set reading cursor in. e.g. 'C1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        return self.api_call("groups.mark", json=kwargs)

    def groups_open(self, **kwargs):
        """Opens a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        return self.api_call("groups.open", json=kwargs)

    @xoxp_token_only
    def groups_rename(self, **kwargs):
        """Renames a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        return self.api_call("groups.rename", json=kwargs)

    @xoxp_token_only
    def groups_replies(self, **kwargs):
        """Retrieve a thread of messages posted to a private channel

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        return self.api_call("groups.replies", http_verb="GET", params=kwargs)

    def groups_setPurpose(self, **kwargs):
        """Sets the purpose for a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        return self.api_call("groups.setPurpose", json=kwargs)

    def groups_setTopic(self, **kwargs):
        """Sets the topic for a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        return self.api_call("groups.setTopic", json=kwargs)

    @xoxp_token_only
    def groups_unarchive(self, **kwargs):
        """Unarchives a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
        """
        return self.api_call("groups.unarchive", json=kwargs)

    def im_close(self, **kwargs):
        """Close a direct message channel.

        Args:
            channel (str): Direct message channel to close. e.g. 'D1234567890'
        """
        return self.api_call("im.close", json=kwargs)

    def im_history(self, **kwargs):
        """Fetches history of messages and events from direct message channel.

        Args:
            channel (str): Direct message channel to fetch history from. e.g. 'D1234567890'
        """
        return self.api_call("im.history", http_verb="GET", params=kwargs)

    def im_list(self, **kwargs):
        """Lists direct message channels for the calling user."""
        return self.api_call("im.list", http_verb="GET", params=kwargs)

    def im_mark(self, **kwargs):
        """Sets the read cursor in a direct message channel.

        Args:
            channel (str): Direct message channel to set reading cursor in. e.g. 'D1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        return self.api_call("im.mark", json=kwargs)

    def im_open(self, **kwargs):
        """Opens a direct message channel.

        Args:
            user (str): The user id to open a DM with. e.g. 'W1234567890'
        """
        return self.api_call("im.open", json=kwargs)

    def im_replies(self, **kwargs):
        """Retrieve a thread of messages posted to a direct message conversation

        Args:
            channel (str): Direct message channel to fetch thread from. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        return self.api_call("im.replies", http_verb="GET", params=kwargs)

    def migration_exchange(self, **kwargs):
        """For Enterprise Grid workspaces, map local user IDs to global user IDs

        Args:
            users (list): A list of user ids, up to 400 per request.
                e.g. ['W1234567890', 'U2345678901', 'U3456789012']
        """
        return self.api_call("migration.exchange", http_verb="GET", params=kwargs)

    def mpim_close(self, **kwargs):
        """Closes a multiparty direct message channel.

        Args:
            channel (str): Multiparty Direct message channel to close. e.g. 'G1234567890'
        """
        return self.api_call("mpim.close", json=kwargs)

    def mpim_history(self, **kwargs):
        """Fetches history of messages and events from a multiparty direct message.

        Args:
            channel (str): Multiparty direct message to fetch history for. e.g. 'G1234567890'
        """
        return self.api_call("mpim.history", http_verb="GET", params=kwargs)

    def mpim_list(self, **kwargs):
        """Lists multiparty direct message channels for the calling user."""
        return self.api_call("mpim.list", http_verb="GET", params=kwargs)

    def mpim_mark(self, **kwargs):
        """Sets the read cursor in a multiparty direct message channel.

        Args:
            channel (str): Multiparty direct message channel to set reading cursor in.
                e.g. 'G1234567890'
            ts (str): Timestamp of the most recently seen message.
                e.g. '1234567890.123456'
        """
        return self.api_call("mpim.mark", json=kwargs)

    def mpim_open(self, **kwargs):
        """This method opens a multiparty direct message.

        Args:
            users (list): A lists of user ids. The ordering of the users
                is preserved whenever a MPIM group is returned.
                e.g. ['W1234567890', 'U2345678901', 'U3456789012']
        """
        return self.api_call("mpim.open", json=kwargs)

    def mpim_replies(self, **kwargs):
        """Retrieve a thread of messages posted to a direct message conversation from a
        multiparty direct message.

        Args:
            channel (str): Multiparty direct message channel to fetch thread from.
                e.g. 'G1234567890'
            thread_ts (str): Unique identifier of a thread's parent message.
                e.g. '1234567890.123456'
        """
        return self.api_call("mpim.replies", http_verb="GET", params=kwargs)

    def oauth_access(self, **kwargs):
        """Exchanges a temporary OAuth verifier code for an access token.

        Args:
            client_id (str): Issued when you created your application. e.g. '4b39e9-752c4'
            client_secret (str): Issued when you created your application. e.g. '33fea0113f5b1'
            code (str): The code param returned via the OAuth callback. e.g. 'ccdaa72ad'
        """
        return self.api_call("oauth.access", data=kwargs)

    def pins_add(self, **kwargs):
        """Pins an item to a channel.

        Note: We've called it file_id to avoid conflicting naming issues Python.

        Args:
            channel (str): Channel to pin the item in. e.g. 'C1234567890'
            file_id (str): File id to pin. e.g. 'F1234567890'
            file_comment (str): File comment to pin. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of message to pin. e.g. '1234567890.123456'
        """
        return self.api_call("pins.add", json=kwargs)

    def pins_list(self, **kwargs):
        """Lists items pinned to a channel.

        Args:
            channel (str): Channel to get pinned items for. e.g. 'C1234567890'
        """
        return self.api_call("pins.list", http_verb="GET", params=kwargs)

    def pins_remove(self, **kwargs):
        """Un-pins an item from a channel.

        Note: We've called it file_id to avoid conflicting naming issues Python.

        Args:
            channel (str): Channel to pin the item in. e.g. 'C1234567890'
            file_id (str): File id to pin. e.g. 'F1234567890'
            file_comment (str): File comment to pin. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of message to pin. e.g. '1234567890.123456'
        """
        return self.api_call("pins.remove", json=kwargs)

    def reactions_add(self, **kwargs):
        """Adds a reaction to an item.

        Args:
            name (str): Reaction (emoji) name. e.g. 'thumbsup'
            channel (str): Channel where the message to add reaction to was posted.
                e.g. 'C1234567890'
            timestamp (str): Timestamp of the message to add reaction to. e.g. '1234567890.123456'
        """
        return self.api_call("reactions.add", json=kwargs)

    def reactions_get(self, **kwargs):
        """Gets reactions for an item."""
        return self.api_call("reactions.get", http_verb="GET", params=kwargs)

    def reactions_list(self, **kwargs):
        """Lists reactions made by a user."""
        return self.api_call("reactions.list", http_verb="GET", params=kwargs)

    def reactions_remove(self, **kwargs):
        """Removes a reaction from an item.

        Args:
            name (str): Reaction (emoji) name. e.g. 'thumbsup'
        """
        return self.api_call("reactions.remove", json=kwargs)

    @xoxp_token_only
    def reminders_add(self, **kwargs):
        """Creates a reminder.

        Args:
            text (str): The content of the reminder. e.g. 'eat a banana'
            time (str): When this reminder should happen:
                the Unix timestamp (up to five years from now e.g. '1602288000'),
                the number of seconds until the reminder (if within 24 hours),
                or a natural language description (Ex. 'in 15 minutes' or 'every Thursday')
        """
        return self.api_call("reminders.add", json=kwargs)

    @xoxp_token_only
    def reminders_complete(self, **kwargs):
        """Marks a reminder as complete.

        Args:
            reminder (str): The ID of the reminder to be marked as complete.
                e.g. 'Rm12345678'
        """
        return self.api_call("reminders.complete", json=kwargs)

    @xoxp_token_only
    def reminders_delete(self, **kwargs):
        """Deletes a reminder.

        Args:
            reminder (str): The ID of the reminder. e.g. 'Rm12345678'
        """
        return self.api_call("reminders.delete", json=kwargs)

    @xoxp_token_only
    def reminders_info(self, **kwargs):
        """Gets information about a reminder.

        Args:
            reminder (str): The ID of the reminder. e.g. 'Rm12345678'
        """
        return self.api_call("reminders.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def reminders_list(self, **kwargs):
        """Lists all reminders created by or for a given user."""
        return self.api_call("reminders.list", http_verb="GET", params=kwargs)

    def rtm_connect(self, **kwargs):
        """Starts a Real Time Messaging session."""
        return self.api_call("rtm.connect", http_verb="GET", params=kwargs)

    def rtm_start(self, **kwargs):
        """Starts a Real Time Messaging session."""
        return self.api_call("rtm.start", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def search_all(self, **kwargs):
        """Searches for messages and files matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        return self.api_call("search.all", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def search_files(self, **kwargs):
        """Searches for files matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        return self.api_call("search.files", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def search_messages(self, **kwargs):
        """Searches for messages matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        return self.api_call("search.messages", http_verb="GET", params=kwargs)

    def stars_add(self, **kwargs):
        """Adds a star to an item.

        Note: We've called it file_id to avoid conflicting naming issues Python.

        Args:
            channel (str): Channel to add star to, or channel where the message to add
                star to was posted (used with timestamp). e.g. 'C1234567890'
            file_id (str): File to add star to. e.g. 'F1234567890'
            file_comment (str): File comment to add star to. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of the message to add star to. e.g. '1234567890.123456'
        """
        return self.api_call("stars.add", json=kwargs)

    @xoxp_token_only
    def stars_list(self, **kwargs):
        """Lists stars for a user."""
        return self.api_call("stars.list", http_verb="GET", params=kwargs)

    def stars_remove(self, **kwargs):
        """Removes a star from an item.

        Note: We've called it file_id to avoid conflicting naming issues Python.

        Args:
            channel (str): Channel to remove star from, or channel where
                the message to remove star from was posted (used with timestamp). e.g. 'C1234567890'
            file_id (str): File to remove star from. e.g. 'F1234567890'
            file_comment (str): File comment to remove star from. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of the message to remove star from. e.g. '1234567890.123456'
        """
        return self.api_call("stars.remove", json=kwargs)

    @xoxp_token_only
    def team_accessLogs(self, **kwargs):
        """Gets the access logs for the current team."""
        return self.api_call("team.accessLogs", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def team_billableInfo(self, **kwargs):
        """Gets billable users information for the current team."""
        return self.api_call("team.billableInfo", http_verb="GET", params=kwargs)

    def team_info(self, **kwargs):
        """Gets information about the current team."""
        return self.api_call("team.info", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def team_integrationLogs(self, **kwargs):
        """Gets the integration logs for the current team."""
        return self.api_call("team.integrationLogs", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def team_profile_get(self, **kwargs):
        """Retrieve a team's profile."""
        return self.api_call("team.profile.get", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def usergroups_create(self, **kwargs):
        """Create a User Group

        Args:
            name (str): A name for the User Group. Must be unique among User Groups.
                e.g. 'My Test Team'
        """
        return self.api_call("usergroups.create", json=kwargs)

    @xoxp_token_only
    def usergroups_disable(self, **kwargs):
        """Disable an existing User Group

        Args:
            usergroup (str): The encoded ID of the User Group to disable.
                e.g. 'S0604QSJC'
        """
        return self.api_call("usergroups.disable", json=kwargs)

    @xoxp_token_only
    def usergroups_enable(self, **kwargs):
        """Enable a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to enable.
                e.g. 'S0604QSJC'
        """
        return self.api_call("usergroups.enable", json=kwargs)

    @xoxp_token_only
    def usergroups_list(self, **kwargs):
        """List all User Groups for a team"""
        return self.api_call("usergroups.list", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def usergroups_update(self, **kwargs):
        """Update an existing User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
        """
        return self.api_call("usergroups.update", json=kwargs)

    @xoxp_token_only
    def usergroups_users_list(self, **kwargs):
        """List all users in a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
        """
        return self.api_call("usergroups.users.list", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def usergroups_users_update(self, **kwargs):
        """Update the list of users for a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
            users (list): A list user IDs that represent the entire list of
                users for the User Group. e.g. ['U060R4BJ4', 'U060RNRCZ']
        """
        return self.api_call("usergroups.users.update", json=kwargs)

    def users_conversations(self, **kwargs):
        """List conversations the calling user may access."""
        return self.api_call("users.conversations", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def users_deletePhoto(self, **kwargs):
        """Delete the user profile photo"""
        return self.api_call("users.deletePhoto", http_verb="GET", params=kwargs)

    def users_getPresence(self, **kwargs):
        """Gets user presence information.

        Args:
            user (str): User to get presence info on. Defaults to the authed user.
                e.g. 'W1234567890'
        """
        return self.api_call("users.getPresence", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def users_identity(self, **kwargs):
        """Get a user's identity."""
        return self.api_call("users.identity", http_verb="GET", params=kwargs)

    def users_info(self, **kwargs):
        """Gets information about a user.

        Args:
            user (str): User to get info on.
                e.g. 'W1234567890'
        """
        return self.api_call("users.info", http_verb="GET", params=kwargs)

    def users_list(self, **kwargs):
        """Lists all users in a Slack team."""
        return self.api_call("users.list", http_verb="GET", params=kwargs)

    def users_lookupByEmail(self, **kwargs):
        """Find a user with an email address.

        Args:
            email (str): An email address belonging to a user in the workspace.
                e.g. 'spengler@ghostbusters.example.com'
        """
        return self.api_call("users.lookupByEmail", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def users_setPhoto(self, image, **kwargs):
        """Set the user profile photo

        Args:
            image (str): Supply the path of the image you'd like to upload.
                e.g. 'myimage.png'
        """
        with open(image, "rb") as i:
            return self.api_call("users.setPhoto", files={"image": i}, data=kwargs)

    def users_setPresence(self, **kwargs):
        """Manually sets user presence.

        Args:
            presence (str): Either 'auto' or 'away'.
        """
        return self.api_call("users.setPresence", json=kwargs)

    @xoxp_token_only
    def users_profile_get(self, **kwargs):
        """Retrieves a user's profile information."""
        return self.api_call("users.profile.get", http_verb="GET", params=kwargs)

    @xoxp_token_only
    def users_profile_set(self, **kwargs):
        """Set the profile information for a user."""
        return self.api_call("users.profile.set", json=kwargs)
