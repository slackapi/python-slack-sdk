#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import random
from slackclient import SlackClient
import time

#get your personal token from https://api.slack.com/web, bottom of the page.
api_key = ''
client = SlackClient(api_key)

if client.rtm_connect():
    while True:
        last_read = client.rtm_read()
        if last_read:
            try:
                parsed = last_read[0]['text']
                #reply to channel message was found in.
                message_channel = last_read[0]['channel']
                if parsed and 'food:' in parsed:
                    choice = random.choice(['hamburger', 'pizza'])
                    client.rtm_send_message(message_channel,
                                            'Today you\'ll eat %s.' % choice)
            except:
                pass
        time.sleep(1)
