#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from slackclient import SlackClient

token = "xoxb-12362166850-sy4hycJ5edUT8rczQMCbT2TS"
sc = SlackClient(token)

listsOfChans = json.loads(sc.api_call("channels.list"))


nameOfChans = [str(listsOfChans[u'channels'][i][u'name']) for i in range(len(listsOfChans[u'channels']))]
idOfChans = [str(listsOfChans[u'channels'][i][u'id']) for i in range(len(listsOfChans[u'channels']))]

idOfGeneral=''
for i in range(len(nameOfChans)):
    if nameOfChans[i] == "general":
        idOfGeneral = idOfChans[i]

print idOfChans
print nameOfChans
print idOfGeneral
#resp1 = sc.api_call("channels.join", name=idOfGeneral)
#print(resp1)
resp = sc.api_call("chat.postMessage", as_user="true", channel=idOfGeneral, text="Demain midi, en entrée une superbe salade de chèvre chaud - qui, si je peux me permettre, est sa mère la pute bonne - En plat du thon à la catalane avec son riz au safran. Nous vous proposerons un crumble en dessert chaud.\nDemain soir des aiguillettes de poulet avec des pommes de terre hongroises ou des lasagnes au thon.")
print(resp)
