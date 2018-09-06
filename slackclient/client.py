#!/usr/bin/python
# mostly a proxy object to abstract how some of this works

import json
import logging
import time

from .server import Server
from .exceptions import ParseResponseError, SlackClientError

LOG = logging.getLogger(__name__)


class SlackClient(object):
    '''
    The SlackClient makes API Calls to the `Slack Web API <https://api.slack.com/web>`_ as well as
    managing connections to the `Real-time Messaging API via websocket <https://api.slack.com/rtm>`_

    It also manages some of the Client state for Channels that the associated token (User or Bot)
    is associated with.

    For more information, check out the `Slack API Docs <https://api.slack.com/>`_
    '''
    def __init__(
            self,
            access_token=None,
            refresh_token=None,
            client_id=None,
            client_secret=None,
            refresh_callback=None,
            proxies=None,
            **kwargs
    ):
        """
        Init:
            :Args:
                token (str): Your Slack Authentication token. You can find or generate a test token
                `here <https://api.slack.com/docs/oauth-test-tokens>`_
                Note: Be `careful with your token <https://api.slack.com/docs/oauth-safety>`_
                proxies (dict): Proxies to use when create websocket or api calls,
                declare http and websocket proxies using {'http': 'http://127.0.0.1'},
                and https proxy using {'https': 'https://127.0.0.1:443'}
                refresh_token (str): Your Slack app's refresh token. This token is used to
                update your app's OAuth access token
                client_id (str): Your app's Client ID
                client_secret (srt): Your app's Client Secret (Used for OAuth requests)
                refresh_callback (function): Your application's function for updating Slack
                OAuth tokens inside your data store
        """
        if (refresh_token):
            if (callable(refresh_callback)):
                self.server = Server(
                    client=self,
                    connect=False,
                    proxies=proxies,
                    refresh_token=refresh_token,
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_callback=refresh_callback
                )
            else:
                raise SlackClientError(
                    "Token refresh callback function is required when using refresh token."
                )
        else:
            # Slack app configs
            self.server = Server(
                access_token=access_token,
                connect=False,
                proxies=proxies
            )
        self.token = access_token  # noqa TODO: Change this to `self.access_token` in the next major version bump

    def update_client_tokens(self, team_id, access_token, expires_in):
        """
        This method is used to update this client instance's
        OAuth access tokens upon a token refresh event

        :Args:
            access_token (str): The client's OAuth access token, used for Web API requests
            refresh_token(str): The OAuth token used for making access token refresh requests
            expires_in (int): OAuth access token lifespan. This is used to set the `expires_at` TTL
            refresh_callback (obj): A callable object to be executed upon token refresh
        """
        # Set the client's team ID and access token
        setattr(self.server.api_requester, 'team_id', team_id)
        setattr(self.server.api_requester, 'access_token', access_token)
        setattr(self, 'token', access_token)

        # Update the token expiration timestamp
        current_ts = int(time.time()) * 1000
        expires_at = int(current_ts + expires_in)
        setattr(self.server.api_requester, 'access_token_expires_at', expires_at)

    def append_user_agent(self, name, version):
        self.server.append_user_agent(name, version)

    def rtm_connect(self, with_team_state=True, **kwargs):
        '''
        Connects to the RTM Websocket

        :Args:
            with_team_state (bool): Connect via `rtm.start` to pull workspace state information.
            `False` connects via `rtm.connect`, which is lighter weight and better for very large
            teams.

        :Returns:
            False on exceptions
        '''

        if (self.server.refresh_token):
            raise SlackClientError("Workspace tokens may not be used to connect to the RTM API.")

        try:
            self.server.rtm_connect(use_rtm_start=with_team_state, **kwargs)
            return self.server.connected
        except Exception:
            LOG.warn("Failed RTM connect", exc_info=True)
            return False

    def api_call(self, method, timeout=None, **kwargs):
        """
        Call the Slack Web API as documented here: https://api.slack.com/web

        :Args:
            method (str): The API Method to call. See
            `the full list here <https://api.slack.com/methods>`_
        :Kwargs:
            (optional) kwargs: any arguments passed here will be bundled and sent to the api
            requester as post_data and will be passed along to the API.

            Example::

                sc.api_call(
                    "channels.setPurpose",
                    channel="CABC12345",
                    purpose="Writing some code!"
                )

        :Returns:
            str -- returns the text of the HTTP response.

            Examples::

                u'{"ok":true,"purpose":"Testing bots"}'
                or
                u'{"ok":false,"error":"channel_not_found"}'

            See here for more information on responses: https://api.slack.com/web
        """
        response_body = self.server.api_call(method, timeout=timeout, **kwargs)
        try:
            result = json.loads(response_body)
        except ValueError as json_decode_error:
            raise ParseResponseError(response_body, json_decode_error)

        if "ok" in result and result["ok"]:
            if method == 'im.open':
                self.server.attach_channel(kwargs["user"], result["channel"]["id"])
            elif method in ('mpim.open', 'groups.create', 'groups.createchild'):
                self.server.parse_channel_data([result['group']])
            elif method in ('channels.create', 'channels.join'):
                self.server.parse_channel_data([result['channel']])
        return result

    def rtm_read(self):
        '''
        Reads from the RTM Websocket stream then calls `self.process_changes(item)` for each line
        in the returned data.

        Multiple events may be returned, always returns a list [], which is empty if there are no
        incoming messages.

        :Args:
            None

        :Returns:
            data (json) - The server response. For example::

                [{u'presence': u'active', u'type': u'presence_change', u'user': u'UABC1234'}]

        :Raises:
            SlackNotConnected if self.server is not defined.
        '''
        # in the future, this should handle some events internally i.e. channel
        # creation
        if self.server:
            json_data = self.server.websocket_safe_read()
            data = []
            if json_data != '':
                for d in json_data.split('\n'):
                    data.append(json.loads(d))
            for item in data:
                self.process_changes(item)
            return data
        else:
            raise SlackNotConnected

    def rtm_send_message(self, channel, message, thread=None, reply_broadcast=None):
        '''
        Sends a message to a given channel.

        :Args:
            channel (str) - the string identifier for a channel or channel name (e.g. 'C1234ABC',
            'bot-test' or '#bot-test')
            message (message) - the string you'd like to send to the channel
            thread (str or None) - the parent message ID, if sending to a
                thread
            reply_broadcast (bool) - if messaging a thread, whether to
                also send the message back to the channel

        :Returns:
            None

        '''
        # The `channel` argument can be a channel name or an ID. At first its assumed to be a
        # name and an attempt is made to find the ID in the workspace state cache.
        # If that lookup fails, the argument is used as the channel ID.
        found_channel = self.server.channels.find(channel)
        channel_id = found_channel.id if found_channel else channel
        return self.server.rtm_send_message(
            channel_id,
            message,
            thread,
            reply_broadcast
        )

    def process_changes(self, data):
        '''
        Internal method which processes RTM events and modifies the local data store
        accordingly.

        Stores new channels when joining a group (Multi-party DM), IM (DM) or channel.

        Stores user data on a team join event.
        '''
        if "type" in data.keys():
            if data["type"] in ('channel_created', 'group_joined'):
                channel = data["channel"]
                self.server.attach_channel(channel["name"], channel["id"], [])
            if data["type"] == 'im_created':
                channel = data["channel"]
                self.server.attach_channel(channel["user"], channel["id"], [])
            if data["type"] == "team_join":
                user = data["user"]
                self.server.parse_user_data([user])
            pass


class SlackNotConnected(Exception):
    pass
