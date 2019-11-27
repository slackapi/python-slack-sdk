"""A Python module for interacting with Slack's Web API."""

# Standard Imports
from typing import Union, List
from io import IOBase
from asyncio import Future

# Internal Imports
from slack.web.base_client import BaseClient, SlackResponse
import slack.errors as e


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
        timeout (int): The maximum number of seconds the client will wait
            to connect and receive a response from Slack.
            Default is 30 seconds.

    Methods:
        api_call: Constructs a request and executes the API call to Slack.

    Example of recommended usage:
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

    Example manually creating an API request:
    ```python
        import os
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

    def admin_apps_approve(
        self, *, app_id: str = None, request_id: str = None, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Approve an app for installation on a workspace.

        Either app_id or request_id is required.
        These IDs can be obtained either directly via the app_requested event,
        or by the admin.apps.requests.list method.

        Args:
            app_id (str): The id of the app to approve. e.g. 'A12345'
            request_id (str): The id of the request to approve. e.g. 'Ar12345'
        Raises:
            SlackRequestError: If niether or both the `app_id` and `request_id` args are specified.
        """
        if app_id:
            kwargs.update({"app_id": app_id})
        elif request_id:
            kwargs.update({"request_id": request_id})
        else:
            raise e.SlackRequestError(
                "The app_id or request_id argument must be specified."
            )

        return self.api_call("admin.apps.approve", json=kwargs)

    def admin_apps_requests_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """List app requests for a team/workspace."""
        return self.api_call("admin.apps.requests.list", http_verb="GET", params=kwargs)

    def admin_apps_restrict(self, **kwargs) -> Union[Future, SlackResponse]:
        """Restrict an app for installation on a workspace."""
        return self.api_call("admin.apps.restrict", json=kwargs)

    def admin_users_session_reset(
        self, *, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Wipes all valid sessions on all devices for a given user.

        Args:
            user_id (str): The ID of the user to wipe sessions for. e.g. 'W12345678'
        """
        kwargs.update({"user_id": user_id})
        return self.api_call("admin.users.session.reset", json=kwargs)

    def admin_inviteRequests_approve(
        self, *, invite_request_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Approve a workspace invite request.

        team_id is required if your Enterprise Grid org contains more than one workspace.

        Args:
            invite_request_id (str): ID of the request to invite. e.g. 'Ir1234'
        """
        kwargs.update({"invite_request_id": invite_request_id})
        return self.api_call("admin.inviteRequests.approve", json=kwargs)

    def admin_inviteRequests_approved_list(
        self, **kwargs
    ) -> Union[Future, SlackResponse]:
        """List all approved workspace invite requests."""
        return self.api_call("admin.inviteRequests.approved.list", json=kwargs)

    def admin_inviteRequests_denied_list(
        self, **kwargs
    ) -> Union[Future, SlackResponse]:
        """List all denied workspace invite requests."""
        return self.api_call("admin.inviteRequests.denied.list", json=kwargs)

    def admin_inviteRequests_deny(
        self, *, invite_request_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Deny a workspace invite request.

        Args:
            invite_request_id (str): ID of the request to invite. e.g. 'Ir1234'
        """
        kwargs.update({"invite_request_id": invite_request_id})
        return self.api_call("admin.inviteRequests.deny", json=kwargs)

    def admin_inviteRequests_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """List all pending workspace invite requests."""
        return self.api_call("admin.inviteRequests.list", json=kwargs)

    def admin_teams_admins_list(
        self, *, team_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """List all of the admins on a given workspace.

        Args:
            team_id (str): ID of the team.
        """
        kwargs.update({"team_id": team_id})
        return self.api_call("admin.teams.admins.list", http_verb="GET", params=kwargs)

    def admin_teams_create(
        self, *, team_domain: str, team_name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Create an Enterprise team.

        Args:
            team_domain (str): Team domain. e.g. 'slacksoftballteam'
            team_name (str): Team name. e.g. 'Slack Softball Team'
        """
        kwargs.update({"team_domain": team_domain, "team_name": team_name})
        return self.api_call("admin.teams.create", json=kwargs)

    def admin_teams_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """List all teams on an Enterprise organization."""
        return self.api_call("admin.teams.list", json=kwargs)

    def admin_teams_owners_list(
        self, *, team_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """List all of the admins on a given workspace.

        Args:
            team_id (str): ID of the team.
        """
        kwargs.update({"team_id": team_id})
        return self.api_call("admin.teams.owners.list", http_verb="GET", params=kwargs)

    def admin_teams_settings_setDescription(
        self, *, team_id: str, description: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Set the description of a given workspace.

        Args:
            team_id (str): ID of the team.
            description (str): Description of the team.
        """
        kwargs.update({"team_id": team_id, "description": description})
        return self.api_call("admin.teams.settings.setDescription", json=kwargs)

    def admin_teams_settings_setIcon(
        self, *, team_id: str, image_url: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the icon of a workspace.

        Args:
            team_id (str): ID of the team.
            image_url (str): Url of the icon.
        """
        kwargs.update({"team_id": team_id, "image_url": image_url})
        return self.api_call(
            "admin.teams.settings.setIcon", http_verb="GET", params=kwargs
        )

    def admin_teams_settings_setName(
        self, *, team_id: str, name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the icon of a workspace.

        Args:
            team_id (str): ID of the team.
            name (str): Name of the team.
        """
        kwargs.update({"team_id": team_id, "name": name})
        return self.api_call("admin.teams.settings.setName", json=kwargs)

    def admin_users_assign(
        self, *, team_id: str, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Add an Enterprise user to a workspace.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            user_id (str): ID of the user to add to the workspace.
        """
        kwargs.update({"team_id": team_id, "user_id": user_id})
        return self.api_call("admin.users.assign", json=kwargs)

    def admin_users_invite(
        self, *, team_id: str, email: str, channel_ids: List[str], **kwargs
    ) -> Union[Future, SlackResponse]:
        """Invite a user to a workspace.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            email (str): The email address of the person to invite. e.g. 'joe@email.com'
            channel_ids (list): A list of channel_ids for this user to join.
                At least one channel is required. e.g. ['C1A2B3C4D', 'C26Z25Y24']
        """
        kwargs.update({"team_id": team_id, "email": email, "channel_ids": channel_ids})
        return self.api_call("admin.users.invite", json=kwargs)

    def admin_users_remove(
        self, *, team_id: str, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Remove a user from a workspace.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            user_id (str): The ID of the user to remove. e.g. 'W12345678'
        """
        kwargs.update({"team_id": team_id, "user_id": user_id})
        return self.api_call("admin.users.remove", json=kwargs)

    def admin_users_setAdmin(
        self, *, team_id: str, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Set an existing guest, regular user, or owner to be an admin user.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            user_id (str): The ID of the user to remove. e.g. 'W12345678'
        """
        kwargs.update({"team_id": team_id, "user_id": user_id})
        return self.api_call("admin.users.setAdmin", json=kwargs)

    def admin_users_setOwner(
        self, *, team_id: str, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Set an existing guest, regular user, or admin user to be a workspace owner.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            user_id (str): The ID of the user to remove. e.g. 'W12345678'
        """
        kwargs.update({"team_id": team_id, "user_id": user_id})
        return self.api_call("admin.users.setOwner", json=kwargs)

    def admin_users_setRegular(
        self, *, team_id: str, user_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Set an existing guest user, admin user, or owner to be a regular user.

        Args:
            team_id (str): ID of the team. e.g. 'T1234'
            user_id (str): The ID of the user to remove. e.g. 'W12345678'
        """
        kwargs.update({"team_id": team_id, "user_id": user_id})
        return self.api_call("admin.users.setRegular", json=kwargs)

    def api_test(self, **kwargs) -> Union[Future, SlackResponse]:
        """Checks API calling code."""
        return self.api_call("api.test", json=kwargs)

    def auth_revoke(self, **kwargs) -> Union[Future, SlackResponse]:
        """Revokes a token."""
        return self.api_call("auth.revoke", http_verb="GET", params=kwargs)

    def auth_test(self, **kwargs) -> Union[Future, SlackResponse]:
        """Checks authentication & identity."""
        return self.api_call("auth.test", json=kwargs)

    def bots_info(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about a bot user."""
        return self.api_call("bots.info", http_verb="GET", params=kwargs)

    def channels_archive(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Archives a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("channels.archive", json=kwargs)

    def channels_create(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Creates a channel.

        Args:
            name (str): The name of the channel. e.g. 'mychannel'
        """
        kwargs.update({"name": name})
        return self.api_call("channels.create", json=kwargs)

    def channels_history(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Fetches history of messages and events from a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("channels.history", http_verb="GET", params=kwargs)

    def channels_info(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("channels.info", http_verb="GET", params=kwargs)

    def channels_invite(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Invites a user to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("channels.invite", json=kwargs)

    def channels_join(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Joins a channel, creating it if needed.

        Args:
            name (str): The channel name. e.g. '#general'
        """
        kwargs.update({"name": name})
        return self.api_call("channels.join", json=kwargs)

    def channels_kick(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Removes a user from a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("channels.kick", json=kwargs)

    def channels_leave(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Leaves a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("channels.leave", json=kwargs)

    def channels_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists all channels in a Slack team."""
        return self.api_call("channels.list", http_verb="GET", params=kwargs)

    def channels_mark(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the read cursor in a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("channels.mark", json=kwargs)

    def channels_rename(
        self, *, channel: str, name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Renames a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        kwargs.update({"channel": channel, "name": name})
        return self.api_call("channels.rename", json=kwargs)

    def channels_replies(
        self, *, channel: str, thread_ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a thread of messages posted to a channel

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "thread_ts": thread_ts})
        return self.api_call("channels.replies", http_verb="GET", params=kwargs)

    def channels_setPurpose(
        self, *, channel: str, purpose: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the purpose for a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        kwargs.update({"channel": channel, "purpose": purpose})
        return self.api_call("channels.setPurpose", json=kwargs)

    def channels_setTopic(
        self, *, channel: str, topic: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the topic for a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        kwargs.update({"channel": channel, "topic": topic})
        return self.api_call("channels.setTopic", json=kwargs)

    def channels_unarchive(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Unarchives a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("channels.unarchive", json=kwargs)

    def chat_delete(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Deletes a message.

        Args:
            channel (str): Channel containing the message to be deleted. e.g. 'C1234567890'
            ts (str): Timestamp of the message to be deleted. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("chat.delete", json=kwargs)

    def chat_deleteScheduledMessage(
        self, *, channel: str, scheduled_message_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Deletes a scheduled message.

        Args:
            channel (str): The channel the scheduled_message is posting to. e.g. 'C1234567890'
            scheduled_message_id (str): scheduled_message_id returned from call to chat.scheduleMessage e.g. 'Q1234ABCD'
        """
        kwargs.update(
            {"channel": channel, "scheduled_message_id": scheduled_message_id}
        )
        return self.api_call("chat.deleteScheduledMessage", json=kwargs)

    def chat_getPermalink(
        self, *, channel: str, message_ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a permalink URL for a specific extant message

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            message_ts (str): The timestamp. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "message_ts": message_ts})
        return self.api_call("chat.getPermalink", http_verb="GET", params=kwargs)

    def chat_meMessage(
        self, *, channel: str, text: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Share a me message into a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            text (str): The message you'd like to share. e.g. 'Hello world'
        """
        kwargs.update({"channel": channel, "text": text})
        return self.api_call("chat.meMessage", json=kwargs)

    def chat_postEphemeral(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sends an ephemeral message to a user in a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The id of user who should see the message. e.g. 'U0BPQUNTA'
            text (str): The message you'd like to share. e.g. 'Hello world'
                text is not required when presenting blocks.
            blocks (list): A dictionary list of blocks.
                Blocks are required when not presenting text.
                e.g. [{"type": "section", "text": {"type": "plain_text", "text": "Hello world"}}]
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("chat.postEphemeral", json=kwargs)

    def chat_postMessage(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sends a message to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            text (str): The message you'd like to share. e.g. 'Hello world'
                text is not required when presenting blocks.
            blocks (list): A dictionary list of blocks.
                Blocks are required when not presenting text.
                e.g. [{"type": "section", "text": {"type": "plain_text", "text": "Hello world"}}]
        """
        kwargs.update({"channel": channel})
        return self.api_call("chat.postMessage", json=kwargs)

    def chat_scheduleMessage(
        self, *, channel: str, post_at: str, text: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Schedules a message.

        Args:
            channel (str): The channel the scheduled_message is posting to. e.g. 'C1234567890'
            post_at (str): Unix EPOCH timestamp of time in future to send the message. e.g. '299876400'
            text (str): The message you'd like to send. e.g. 'Hello world'
        """
        kwargs.update({"channel": channel, "post_at": post_at, "text": text})
        return self.api_call("chat.scheduleMessage", json=kwargs)

    def chat_unfurl(
        self, *, channel: str, ts: str, unfurls: dict, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Provide custom unfurl behavior for user-posted URLs.

        Args:
            channel (str): The Channel ID of the message. e.g. 'C1234567890'
            ts (str): Timestamp of the message to add unfurl behavior to. e.g. '1234567890.123456'
            unfurls (dict): a dict of the specific URLs you're offering an unfurl for.
                e.g. {"https://example.com/": {"text": "Every day is the test."}}
        """
        kwargs.update({"channel": channel, "ts": ts, "unfurls": unfurls})
        return self.api_call("chat.unfurl", json=kwargs)

    def chat_update(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Updates a message in a channel.

        Args:
            channel (str): The channel containing the message to be updated. e.g. 'C1234567890'
            ts (str): Timestamp of the message to be updated. e.g. '1234567890.123456'
            text (str): The message you'd like to share. e.g. 'Hello world'
                text is not required when presenting blocks.
            blocks (list): A dictionary list of blocks.
                Blocks are required when not presenting text.
                e.g. [{"type": "section", "text": {"type": "plain_text", "text": "Hello world"}}]
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("chat.update", json=kwargs)

    def chat_scheduledMessages_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists all scheduled messages."""
        return self.api_call("chat.scheduledMessages.list", json=kwargs)

    def conversations_archive(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Archives a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.archive", json=kwargs)

    def conversations_close(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Closes a direct message or multi-person direct message.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.close", json=kwargs)

    def conversations_create(
        self, *, name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Initiates a public or private channel-based conversation

        Args:
            name (str): The name of the channel. e.g. 'mychannel'
        """
        kwargs.update({"name": name})
        return self.api_call("conversations.create", json=kwargs)

    def conversations_history(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Fetches a conversation's history of messages and events.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.history", http_verb="GET", params=kwargs)

    def conversations_info(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve information about a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.info", http_verb="GET", params=kwargs)

    def conversations_invite(
        self, *, channel: str, users: List[str], **kwargs
    ) -> Union[Future, SlackResponse]:
        """Invites users to a channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            users (list): An list of user id's to invite. e.g. ['U2345678901', 'U3456789012']
        """
        kwargs.update({"channel": channel, "users": users})
        return self.api_call("conversations.invite", json=kwargs)

    def conversations_join(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Joins an existing conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.join", json=kwargs)

    def conversations_kick(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Removes a user from a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            user (str): The id of the user to kick. e.g. 'U2345678901'
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("conversations.kick", json=kwargs)

    def conversations_leave(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Leaves a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.leave", json=kwargs)

    def conversations_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists all channels in a Slack team."""
        return self.api_call("conversations.list", http_verb="GET", params=kwargs)

    def conversations_members(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve members of a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.members", http_verb="GET", params=kwargs)

    def conversations_open(self, **kwargs) -> Union[Future, SlackResponse]:
        """Opens or resumes a direct message or multi-person direct message."""
        return self.api_call("conversations.open", json=kwargs)

    def conversations_rename(
        self, *, channel: str, name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Renames a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        kwargs.update({"channel": channel, "name": name})
        return self.api_call("conversations.rename", json=kwargs)

    def conversations_replies(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a thread of messages posted to a conversation

        Args:
            channel (str): Conversation ID to fetch thread from. e.g. 'C1234567890'
            ts (str): Unique identifier of a thread's parent message. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("conversations.replies", http_verb="GET", params=kwargs)

    def conversations_setPurpose(
        self, *, channel: str, purpose: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the purpose for a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        kwargs.update({"channel": channel, "purpose": purpose})
        return self.api_call("conversations.setPurpose", json=kwargs)

    def conversations_setTopic(
        self, *, channel: str, topic: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the topic for a conversation.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        kwargs.update({"channel": channel, "topic": topic})
        return self.api_call("conversations.setTopic", json=kwargs)

    def conversations_unarchive(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Reverses conversation archival.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("conversations.unarchive", json=kwargs)

    def dialog_open(
        self, *, dialog: dict, trigger_id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
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
        kwargs.update({"dialog": dialog, "trigger_id": trigger_id})
        return self.api_call("dialog.open", json=kwargs)

    def dnd_endDnd(self, **kwargs) -> Union[Future, SlackResponse]:
        """Ends the current user's Do Not Disturb session immediately."""
        return self.api_call("dnd.endDnd", json=kwargs)

    def dnd_endSnooze(self, **kwargs) -> Union[Future, SlackResponse]:
        """Ends the current user's snooze mode immediately."""
        return self.api_call("dnd.endSnooze", json=kwargs)

    def dnd_info(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieves a user's current Do Not Disturb status."""
        return self.api_call("dnd.info", http_verb="GET", params=kwargs)

    def dnd_setSnooze(
        self, *, num_minutes: int, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Turns on Do Not Disturb mode for the current user, or changes its duration.

        Args:
            num_minutes (int): The snooze duration. e.g. 60
        """
        kwargs.update({"num_minutes": num_minutes})
        return self.api_call("dnd.setSnooze", http_verb="GET", params=kwargs)

    def dnd_teamInfo(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieves the Do Not Disturb status for users on a team."""
        return self.api_call("dnd.teamInfo", http_verb="GET", params=kwargs)

    def emoji_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists custom emoji for a team."""
        return self.api_call("emoji.list", http_verb="GET", params=kwargs)

    def files_comments_delete(
        self, *, file: str, id: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Deletes an existing comment on a file.

        Args:
            file (str): The file id. e.g. 'F1234467890'
            id (str): The file comment id. e.g. 'Fc1234567890'
        """
        kwargs.update({"file": file, "id": id})
        return self.api_call("files.comments.delete", json=kwargs)

    def files_delete(self, *, file: str, **kwargs) -> Union[Future, SlackResponse]:
        """Deletes a file.

        Args:
            file (str): The file id. e.g. 'F1234467890'
        """
        kwargs.update({"file": file})
        return self.api_call("files.delete", json=kwargs)

    def files_info(self, *, file: str, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about a team file.

        Args:
            file (str): The file id. e.g. 'F1234467890'
        """
        kwargs.update({"file": file})
        return self.api_call("files.info", http_verb="GET", params=kwargs)

    def files_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists & filters team files."""
        return self.api_call("files.list", http_verb="GET", params=kwargs)

    def files_remote_info(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieve information about a remote file added to Slack."""
        return self.api_call("files.remote.info", http_verb="GET", params=kwargs)

    def files_remote_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieve information about a remote file added to Slack."""
        return self.api_call("files.remote.list", http_verb="GET", params=kwargs)

    def files_remote_add(
        self, *, external_id: str, external_url: str, title: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Adds a file from a remote service.

        Args:
            external_id (str): Creator defined GUID for the file. e.g. '123456'
            external_url (str): URL of the remote file. e.g. 'http://example.com/my_cloud_service_file/abc123'
            title (str): Title of the file being shared. e.g. 'Danger, High Voltage!'
        """
        kwargs.update(
            {"external_id": external_id, "external_url": external_url, "title": title}
        )
        return self.api_call("files.remote.add", http_verb="GET", params=kwargs)

    def files_remote_update(self, **kwargs) -> Union[Future, SlackResponse]:
        """Updates an existing remote file."""
        return self.api_call("files.remote.update", http_verb="GET", params=kwargs)

    def files_remote_remove(self, **kwargs) -> Union[Future, SlackResponse]:
        """Remove a remote file."""
        return self.api_call("files.remote.remove", http_verb="GET", params=kwargs)

    def files_remote_share(
        self, *, channels: Union[str, List[str]], **kwargs
    ) -> Union[Future, SlackResponse]:
        """Share a remote file into a channel.

        Args:
            channels (list): Comma-separated list of channel IDs where the file will be shared.
                e.g. ['C1234567890', 'C2345678901']
        """
        kwargs.update({"channels": channels})
        return self.api_call("files.remote.share", http_verb="GET", params=kwargs)

    def files_revokePublicURL(
        self, *, file: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Revokes public/external sharing access for a file

        Args:
            file (str): The file id. e.g. 'F1234467890'
        """
        kwargs.update({"file": file})
        return self.api_call("files.revokePublicURL", json=kwargs)

    def files_sharedPublicURL(
        self, *, file: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Enables a file for public/external sharing.

        Args:
            file (str): The file id. e.g. 'F1234467890'
        """
        kwargs.update({"file": file})
        return self.api_call("files.sharedPublicURL", json=kwargs)

    def files_upload(
        self, *, file: Union[str, IOBase] = None, content: str = None, **kwargs
    ) -> Union[Future, SlackResponse]:
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
            return self.api_call("files.upload", files={"file": file}, data=kwargs)
        data = kwargs.copy()
        data.update({"content": content})
        return self.api_call("files.upload", data=data)

    def groups_archive(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Archives a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.archive", json=kwargs)

    def groups_create(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Creates a private channel.

        Args:
            name (str): The name of the private group. e.g. 'mychannel'
        """
        kwargs.update({"name": name})
        return self.api_call("groups.create", json=kwargs)

    def groups_createChild(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Clones and archives a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.createChild", http_verb="GET", params=kwargs)

    def groups_history(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Fetches history of messages and events from a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.history", http_verb="GET", params=kwargs)

    def groups_info(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.info", http_verb="GET", params=kwargs)

    def groups_invite(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Invites a user to a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("groups.invite", json=kwargs)

    def groups_kick(
        self, *, channel: str, user: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Removes a user from a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
            user (str): The user id. e.g. 'U1234567890'
        """
        kwargs.update({"channel": channel, "user": user})
        return self.api_call("groups.kick", json=kwargs)

    def groups_leave(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Leaves a private channel.

        Args:
            channel (str): The group id. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.leave", json=kwargs)

    def groups_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists private channels that the calling user has access to."""
        return self.api_call("groups.list", http_verb="GET", params=kwargs)

    def groups_mark(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the read cursor in a private channel.

        Args:
            channel (str): Private channel to set reading cursor in. e.g. 'C1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("groups.mark", json=kwargs)

    def groups_open(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Opens a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.open", json=kwargs)

    def groups_rename(
        self, *, channel: str, name: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Renames a private channel.

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            name (str): The new channel name. e.g. 'newchannel'
        """
        kwargs.update({"channel": channel, "name": name})
        return self.api_call("groups.rename", json=kwargs)

    def groups_replies(
        self, *, channel: str, thread_ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a thread of messages posted to a private channel

        Args:
            channel (str): The channel id. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "thread_ts": thread_ts})
        return self.api_call("groups.replies", http_verb="GET", params=kwargs)

    def groups_setPurpose(
        self, *, channel: str, purpose: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the purpose for a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
            purpose (str): The new purpose for the channel. e.g. 'My Purpose'
        """
        kwargs.update({"channel": channel, "purpose": purpose})
        return self.api_call("groups.setPurpose", json=kwargs)

    def groups_setTopic(
        self, *, channel: str, topic: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the topic for a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
            topic (str): The new topic for the channel. e.g. 'My Topic'
        """
        kwargs.update({"channel": channel, "topic": topic})
        return self.api_call("groups.setTopic", json=kwargs)

    def groups_unarchive(
        self, *, channel: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Unarchives a private channel.

        Args:
            channel (str): The channel id. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("groups.unarchive", json=kwargs)

    def im_close(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Close a direct message channel.

        Args:
            channel (str): Direct message channel to close. e.g. 'D1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("im.close", json=kwargs)

    def im_history(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Fetches history of messages and events from direct message channel.

        Args:
            channel (str): Direct message channel to fetch history from. e.g. 'D1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("im.history", http_verb="GET", params=kwargs)

    def im_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists direct message channels for the calling user."""
        return self.api_call("im.list", http_verb="GET", params=kwargs)

    def im_mark(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the read cursor in a direct message channel.

        Args:
            channel (str): Direct message channel to set reading cursor in. e.g. 'D1234567890'
            ts (str): Timestamp of the most recently seen message. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("im.mark", json=kwargs)

    def im_open(self, *, user: str, **kwargs) -> Union[Future, SlackResponse]:
        """Opens a direct message channel.

        Args:
            user (str): The user id to open a DM with. e.g. 'W1234567890'
        """
        kwargs.update({"user": user})
        return self.api_call("im.open", json=kwargs)

    def im_replies(
        self, *, channel: str, thread_ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a thread of messages posted to a direct message conversation

        Args:
            channel (str): Direct message channel to fetch thread from. e.g. 'C1234567890'
            thread_ts (str): The timestamp of an existing message with 0 or more replies.
                e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "thread_ts": thread_ts})
        return self.api_call("im.replies", http_verb="GET", params=kwargs)

    def migration_exchange(
        self, *, users: List[str], **kwargs
    ) -> Union[Future, SlackResponse]:
        """For Enterprise Grid workspaces, map local user IDs to global user IDs

        Args:
            users (list): A list of user ids, up to 400 per request.
                e.g. ['W1234567890', 'U2345678901', 'U3456789012']
        """
        kwargs.update({"users": users})
        return self.api_call("migration.exchange", http_verb="GET", params=kwargs)

    def mpim_close(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Closes a multiparty direct message channel.

        Args:
            channel (str): Multiparty Direct message channel to close. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("mpim.close", json=kwargs)

    def mpim_history(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Fetches history of messages and events from a multiparty direct message.

        Args:
            channel (str): Multiparty direct message to fetch history for. e.g. 'G1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("mpim.history", http_verb="GET", params=kwargs)

    def mpim_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists multiparty direct message channels for the calling user."""
        return self.api_call("mpim.list", http_verb="GET", params=kwargs)

    def mpim_mark(
        self, *, channel: str, ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Sets the read cursor in a multiparty direct message channel.

        Args:
            channel (str): Multiparty direct message channel to set reading cursor in.
                e.g. 'G1234567890'
            ts (str): Timestamp of the most recently seen message.
                e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "ts": ts})
        return self.api_call("mpim.mark", json=kwargs)

    def mpim_open(self, *, users: List[str], **kwargs) -> Union[Future, SlackResponse]:
        """This method opens a multiparty direct message.

        Args:
            users (list): A lists of user ids. The ordering of the users
                is preserved whenever a MPIM group is returned.
                e.g. ['W1234567890', 'U2345678901', 'U3456789012']
        """
        kwargs.update({"users": users})
        return self.api_call("mpim.open", json=kwargs)

    def mpim_replies(
        self, *, channel: str, thread_ts: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Retrieve a thread of messages posted to a direct message conversation from a
        multiparty direct message.

        Args:
            channel (str): Multiparty direct message channel to fetch thread from.
                e.g. 'G1234567890'
            thread_ts (str): Unique identifier of a thread's parent message.
                e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel, "thread_ts": thread_ts})
        return self.api_call("mpim.replies", http_verb="GET", params=kwargs)

    def oauth_access(
        self, *, client_id: str, client_secret: str, code: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Exchanges a temporary OAuth verifier code for an access token.

        Args:
            client_id (str): Issued when you created your application. e.g. '4b39e9-752c4'
            client_secret (str): Issued when you created your application. e.g. '33fea0113f5b1'
            code (str): The code param returned via the OAuth callback. e.g. 'ccdaa72ad'
        """
        kwargs.update({"code": code})
        return self.api_call(
            "oauth.access",
            data=kwargs,
            auth={"client_id": client_id, "client_secret": client_secret},
        )

    def pins_add(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Pins an item to a channel.

        Args:
            channel (str): Channel to pin the item in. e.g. 'C1234567890'
            file (str): File id to pin. e.g. 'F1234567890'
            file_comment (str): File comment to pin. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of message to pin. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel})
        return self.api_call("pins.add", json=kwargs)

    def pins_list(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Lists items pinned to a channel.

        Args:
            channel (str): Channel to get pinned items for. e.g. 'C1234567890'
        """
        kwargs.update({"channel": channel})
        return self.api_call("pins.list", http_verb="GET", params=kwargs)

    def pins_remove(self, *, channel: str, **kwargs) -> Union[Future, SlackResponse]:
        """Un-pins an item from a channel.

        Args:
            channel (str): Channel to pin the item in. e.g. 'C1234567890'
            file (str): File id to pin. e.g. 'F1234567890'
            file_comment (str): File comment to pin. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of message to pin. e.g. '1234567890.123456'
        """
        kwargs.update({"channel": channel})
        return self.api_call("pins.remove", json=kwargs)

    def reactions_add(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Adds a reaction to an item.

        Args:
            name (str): Reaction (emoji) name. e.g. 'thumbsup'
            channel (str): Channel where the message to add reaction to was posted.
                e.g. 'C1234567890'
            timestamp (str): Timestamp of the message to add reaction to. e.g. '1234567890.123456'
        """
        kwargs.update({"name": name})
        return self.api_call("reactions.add", json=kwargs)

    def reactions_get(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets reactions for an item."""
        return self.api_call("reactions.get", http_verb="GET", params=kwargs)

    def reactions_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists reactions made by a user."""
        return self.api_call("reactions.list", http_verb="GET", params=kwargs)

    def reactions_remove(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Removes a reaction from an item.

        Args:
            name (str): Reaction (emoji) name. e.g. 'thumbsup'
        """
        kwargs.update({"name": name})
        return self.api_call("reactions.remove", json=kwargs)

    def reminders_add(
        self, *, text: str, time: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Creates a reminder.

        Args:
            text (str): The content of the reminder. e.g. 'eat a banana'
            time (str): When this reminder should happen:
                the Unix timestamp (up to five years from now e.g. '1602288000'),
                the number of seconds until the reminder (if within 24 hours),
                or a natural language description (Ex. 'in 15 minutes' or 'every Thursday')
        """
        kwargs.update({"text": text, "time": time})
        return self.api_call("reminders.add", json=kwargs)

    def reminders_complete(
        self, *, reminder: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Marks a reminder as complete.

        Args:
            reminder (str): The ID of the reminder to be marked as complete.
                e.g. 'Rm12345678'
        """
        kwargs.update({"reminder": reminder})
        return self.api_call("reminders.complete", json=kwargs)

    def reminders_delete(
        self, *, reminder: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Deletes a reminder.

        Args:
            reminder (str): The ID of the reminder. e.g. 'Rm12345678'
        """
        kwargs.update({"reminder": reminder})
        return self.api_call("reminders.delete", json=kwargs)

    def reminders_info(
        self, *, reminder: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Gets information about a reminder.

        Args:
            reminder (str): The ID of the reminder. e.g. 'Rm12345678'
        """
        kwargs.update({"reminder": reminder})
        return self.api_call("reminders.info", http_verb="GET", params=kwargs)

    def reminders_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists all reminders created by or for a given user."""
        return self.api_call("reminders.list", http_verb="GET", params=kwargs)

    def rtm_connect(self, **kwargs) -> Union[Future, SlackResponse]:
        """Starts a Real Time Messaging session."""
        return self.api_call("rtm.connect", http_verb="GET", params=kwargs)

    def rtm_start(self, **kwargs) -> Union[Future, SlackResponse]:
        """Starts a Real Time Messaging session."""
        return self.api_call("rtm.start", http_verb="GET", params=kwargs)

    def search_all(self, *, query: str, **kwargs) -> Union[Future, SlackResponse]:
        """Searches for messages and files matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        kwargs.update({"query": query})
        return self.api_call("search.all", http_verb="GET", params=kwargs)

    def search_files(self, *, query: str, **kwargs) -> Union[Future, SlackResponse]:
        """Searches for files matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        kwargs.update({"query": query})
        return self.api_call("search.files", http_verb="GET", params=kwargs)

    def search_messages(self, *, query: str, **kwargs) -> Union[Future, SlackResponse]:
        """Searches for messages matching a query.

        Args:
            query (str): Search query. May contains booleans, etc.
                e.g. 'pickleface'
        """
        kwargs.update({"query": query})
        return self.api_call("search.messages", http_verb="GET", params=kwargs)

    def stars_add(self, **kwargs) -> Union[Future, SlackResponse]:
        """Adds a star to an item.

        Args:
            channel (str): Channel to add star to, or channel where the message to add
                star to was posted (used with timestamp). e.g. 'C1234567890'
            file (str): File to add star to. e.g. 'F1234567890'
            file_comment (str): File comment to add star to. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of the message to add star to. e.g. '1234567890.123456'
        """
        return self.api_call("stars.add", json=kwargs)

    def stars_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists stars for a user."""
        return self.api_call("stars.list", http_verb="GET", params=kwargs)

    def stars_remove(self, **kwargs) -> Union[Future, SlackResponse]:
        """Removes a star from an item.

        Args:
            channel (str): Channel to remove star from, or channel where
                the message to remove star from was posted (used with timestamp). e.g. 'C1234567890'
            file (str): File to remove star from. e.g. 'F1234567890'
            file_comment (str): File comment to remove star from. e.g. 'Fc1234567890'
            timestamp (str): Timestamp of the message to remove star from. e.g. '1234567890.123456'
        """
        return self.api_call("stars.remove", json=kwargs)

    def team_accessLogs(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets the access logs for the current team."""
        return self.api_call("team.accessLogs", http_verb="GET", params=kwargs)

    def team_billableInfo(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets billable users information for the current team."""
        return self.api_call("team.billableInfo", http_verb="GET", params=kwargs)

    def team_info(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about the current team."""
        return self.api_call("team.info", http_verb="GET", params=kwargs)

    def team_integrationLogs(self, **kwargs) -> Union[Future, SlackResponse]:
        """Gets the integration logs for the current team."""
        return self.api_call("team.integrationLogs", http_verb="GET", params=kwargs)

    def team_profile_get(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieve a team's profile."""
        return self.api_call("team.profile.get", http_verb="GET", params=kwargs)

    def usergroups_create(self, *, name: str, **kwargs) -> Union[Future, SlackResponse]:
        """Create a User Group

        Args:
            name (str): A name for the User Group. Must be unique among User Groups.
                e.g. 'My Test Team'
        """
        kwargs.update({"name": name})
        return self.api_call("usergroups.create", json=kwargs)

    def usergroups_disable(
        self, *, usergroup: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Disable an existing User Group

        Args:
            usergroup (str): The encoded ID of the User Group to disable.
                e.g. 'S0604QSJC'
        """
        kwargs.update({"usergroup": usergroup})
        return self.api_call("usergroups.disable", json=kwargs)

    def usergroups_enable(
        self, *, usergroup: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Enable a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to enable.
                e.g. 'S0604QSJC'
        """
        kwargs.update({"usergroup": usergroup})
        return self.api_call("usergroups.enable", json=kwargs)

    def usergroups_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """List all User Groups for a team"""
        return self.api_call("usergroups.list", http_verb="GET", params=kwargs)

    def usergroups_update(
        self, *, usergroup: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Update an existing User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
        """
        kwargs.update({"usergroup": usergroup})
        return self.api_call("usergroups.update", json=kwargs)

    def usergroups_users_list(
        self, *, usergroup: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """List all users in a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
        """
        kwargs.update({"usergroup": usergroup})
        return self.api_call("usergroups.users.list", http_verb="GET", params=kwargs)

    def usergroups_users_update(
        self, *, usergroup: str, users: List[str], **kwargs
    ) -> Union[Future, SlackResponse]:
        """Update the list of users for a User Group

        Args:
            usergroup (str): The encoded ID of the User Group to update.
                e.g. 'S0604QSJC'
            users (list): A list user IDs that represent the entire list of
                users for the User Group. e.g. ['U060R4BJ4', 'U060RNRCZ']
        """
        kwargs.update({"usergroup": usergroup, "users": users})
        return self.api_call("usergroups.users.update", json=kwargs)

    def users_conversations(self, **kwargs) -> Union[Future, SlackResponse]:
        """List conversations the calling user may access."""
        return self.api_call("users.conversations", http_verb="GET", params=kwargs)

    def users_deletePhoto(self, **kwargs) -> Union[Future, SlackResponse]:
        """Delete the user profile photo"""
        return self.api_call("users.deletePhoto", http_verb="GET", params=kwargs)

    def users_getPresence(self, *, user: str, **kwargs) -> Union[Future, SlackResponse]:
        """Gets user presence information.

        Args:
            user (str): User to get presence info on. Defaults to the authed user.
                e.g. 'W1234567890'
        """
        kwargs.update({"user": user})
        return self.api_call("users.getPresence", http_verb="GET", params=kwargs)

    def users_identity(self, **kwargs) -> Union[Future, SlackResponse]:
        """Get a user's identity."""
        return self.api_call("users.identity", http_verb="GET", params=kwargs)

    def users_info(self, *, user: str, **kwargs) -> Union[Future, SlackResponse]:
        """Gets information about a user.

        Args:
            user (str): User to get info on.
                e.g. 'W1234567890'
        """
        kwargs.update({"user": user})
        return self.api_call("users.info", http_verb="GET", params=kwargs)

    def users_list(self, **kwargs) -> Union[Future, SlackResponse]:
        """Lists all users in a Slack team."""
        return self.api_call("users.list", http_verb="GET", params=kwargs)

    def users_lookupByEmail(
        self, *, email: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Find a user with an email address.

        Args:
            email (str): An email address belonging to a user in the workspace.
                e.g. 'spengler@ghostbusters.example.com'
        """
        kwargs.update({"email": email})
        return self.api_call("users.lookupByEmail", http_verb="GET", params=kwargs)

    def users_setPhoto(
        self, *, image: Union[str, IOBase], **kwargs
    ) -> Union[Future, SlackResponse]:
        """Set the user profile photo

        Args:
            image (str): Supply the path of the image you'd like to upload.
                e.g. 'myimage.png'
        """
        return self.api_call("users.setPhoto", files={"image": image}, data=kwargs)

    def users_setPresence(
        self, *, presence: str, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Manually sets user presence.

        Args:
            presence (str): Either 'auto' or 'away'.
        """
        kwargs.update({"presence": presence})
        return self.api_call("users.setPresence", json=kwargs)

    def users_profile_get(self, **kwargs) -> Union[Future, SlackResponse]:
        """Retrieves a user's profile information."""
        return self.api_call("users.profile.get", http_verb="GET", params=kwargs)

    def users_profile_set(self, **kwargs) -> Union[Future, SlackResponse]:
        """Set the profile information for a user."""
        return self.api_call("users.profile.set", json=kwargs)

    def views_open(
        self, *, trigger_id: str, view: dict, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Open a view for a user.​

        Open a modal with a user by exchanging a trigger_id received
        from another interaction.
​
        See the modals (https://api.slack.com/block-kit/surfaces/modals)
        documentation to learn how to obtain triggers from interactive components.

        Args:
            trigger_id (str): Exchange a trigger to post to the user.
                e.g. '12345.98765.abcd2358fdea'
            view (dict): The view payload.
        """
        kwargs.update({"trigger_id": trigger_id, "view": view})
        return self.api_call("views.open", json=kwargs)

    def views_push(
        self, *, trigger_id: str, view: dict, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Push a view onto the stack of a root view.

        Push a new view onto the existing view stack by passing a view
        payload and a valid trigger_id generated from an interaction
        within the existing modal.

        Read the modals documentation (https://api.slack.com/block-kit/surfaces/modals)
        to learn more about the lifecycle and intricacies of views.

        Args:
            trigger_id (str): Exchange a trigger to post to the user.
                e.g. '12345.98765.abcd2358fdea'
            view (dict): The view payload.
        """
        kwargs.update({"trigger_id": trigger_id, "view": view})
        return self.api_call("views.push", json=kwargs)

    def views_update(
        self, *, view: dict, external_id: str = None, view_id: str = None, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Update an existing view.

        Update a view by passing a new view definition along with the
        view_id returned in views.open or the external_id.

        See the modals documentation (https://api.slack.com/block-kit/surfaces/modals#updating_views)
        to learn more about updating views and avoiding race conditions with the hash argument.

        Args:
            view (dict): The view payload.
            external_id (str): A unique identifier of the view set by the developer.
                e.g. 'bmarley_view2'
            view_id (str): A unique identifier of the view to be updated.
                e.g. 'VMM512F2U'
        Raises:
            SlackRequestError: Either view_id or external_id is required.
        """
        kwargs.update({"view": view})
        if external_id:
            kwargs.update({"external_id": external_id})
        elif view_id:
            kwargs.update({"view_id": view_id})
        else:
            raise e.SlackRequestError("Either view_id or external_id is required.")

        return self.api_call("views.update", json=kwargs)

    def views_publish(
        self, *, user_id: str, view: dict, **kwargs
    ) -> Union[Future, SlackResponse]:
        """Publish a static view for a User.
        Create or update the view that comprises an
        app's Home tab (https://api.slack.com/surfaces/tabs)
        for a specific user.
        Args:
            user_id (str): id of the user you want publish a view to.
                e.g. 'U0BPQUNTA'
            view (dict): The view payload.
        """
        kwargs.update({"user_id": user_id, "view": view})
        return self.api_call("views.publish", json=kwargs)
