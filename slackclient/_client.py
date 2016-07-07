#!/usr/bin/python
# mostly a proxy object to abstract how some of this works

import json

from slackclient._server import Server


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
    '''
    def __init__(self, token):

        self.token = token
        self.server = Server(self.token, False)

    def rtm_connect(self):
        '''
        Connects to the RTM Websocket

        :Args:
            None

        :Returns:
            False on exceptions
        '''

        try:
            self.server.rtm_connect()
            return True
        except:
            return False

    def api_call(self, method, **kwargs):
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
        result = json.loads(self.server.api_call(method, **kwargs))
        if self.server:
            if method == 'im.open':
                if "ok" in result and result["ok"]:
                    self.server.attach_channel(kwargs["user"], result["channel"]["id"])
            elif method in ('mpim.open', 'groups.create', 'groups.createchild'):
                if "ok" in result and result["ok"]:
                    self.server.attach_channel(
                        result['group']['name'],
                        result['group']['id'],
                        result['group']['members']
                    )
            elif method in ('channels.create', 'channels.join'):
                if 'ok' in result and result['ok']:
                    self.server.attach_channel(
                        result['channel']['name'],
                        result['channel']['id'],
                        result['channel']['members']
                    )
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

    def rtm_send_message(self, channel, message):
        '''
        Sends a message to a given channel.

        :Args:
            channel (str) - the string identifier for a channel or channel name (e.g. 'C1234ABC',
            'bot-test' or '#bot-test')
            message (message) - the string you'd like to send to the channel

        :Returns:
            None

        '''
        return self.server.channels.find(channel).send_message(message)

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
