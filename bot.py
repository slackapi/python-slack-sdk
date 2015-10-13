#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from slackclient import SlackClient

token = "xoxb-12362166850-sy4hycJ5edUT8rczQMCbT2TS"
sc = SlackClient(token)

listsOfChans = json.loads(sc.api_call("channels.list"))

chans = {str(listsOfChans[u'channels'][i][u'name']):str(listsOfChans[u'channels'][i][u'id']) for i in range(len(listsOfChans[u'channels']))}



def annouceFood(food):
    sc.api_call("chat.postMessage", as_user="true", channel=chans['ahtable'], text="J'espère que vous avez faim ce soir pour les aiguillettes de poulet avec des pommes de terre hongroises ou des lasagnes au thon !")


    
