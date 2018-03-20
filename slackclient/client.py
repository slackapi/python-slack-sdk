#!/usr/bin/python
# mostly a proxy object to abstract how some of this works

import json
import traceback

from .server import Server
from .exceptions import ParseResponseError


class SlackClient(object):
    '''
    The SlackClient makes API Calls to the `Slack Web API <https://api.slack.com/web>`_ as well as
    managing connections to the `Real-time Messaging API via websocket <https://api.slack.com/rtm>`_

    It also manages some of the Client state for Channels that the associated token (User or Bot)
    is associated with.

    For more information, check out the `Slack API Docs <https://api.slack.com/>`_

    Init:
        :Args:
            token (str): Your Slack Authentication token. You can find or generate a test token
            `here <https://api.slack.com/docs/oauth-test-tokens>`_
            Note: Be `careful with your token <https://api.slack.com/docs/oauth-safety>`_
            proxies (dict): Proxies to use when create websocket or api calls,
            declare http and websocket proxies using {'http': 'http://127.0.0.1'},
            and https proxy using {'https': 'https://127.0.0.1:443'}
    '''
    def __init__(self, token, proxies=None):

        self.token = token
        self.server = Server(self.token, False, proxies)

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

        try:
            self.server.rtm_connect(use_rtm_start=with_team_state, **kwargs)
            return self.server.connected
        except Exception:
            traceback.print_exc()
            return False

    def api_call(self, method, timeout=None, **kwargs):
        '''
        Call the Slack Web API as documented here: https://api.slack.com/web

        :Args:
            method (str): The API Method to call. See
            `the full list here <https://api.slack.com/methods>`_
        :Kwargs:
            (optional) kwargs: any arguments passed here will be bundled and sent to the api
            requester as post_data and will be passed along to the API.

            Example::

                sc.server.api_call(
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
        '''
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
