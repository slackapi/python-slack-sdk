#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hungrybotlib as l
from random import choice

# hungrybot token for Slack api
TOKEN = "xoxb-12362166850-sy4hycJ5edUT8rczQMCbT2TS"

DISPLAY_TO_CHANS = ["ahtable"]


l.cacheMenus()

with open("counter", "r") as f:
    count = int(f.read())
text = ["Une nouvelle semaine de bouffe !", "Et voila, je viens de mettre à jour les menus.", "Le RAK vient de me dire ce qu'on mange la semaine prochaine..."]

if count == 1:
    l.sayFood("Bonjour ! Je suis fier de me présenter, je suis HungryBot, je vais vous guider tout au long de vos études en vous indiquant ce que vous pourrez manger de bon au RAK de TB !", DISPLAY_TO_CHANS, TOKEN)
else:
    l.sayFood(choice(text)+"\nC'est la "+str(count)+"ème semaine que je suis à votre service.", DISPLAY_TO_CHANS, TOKEN)

with open("counter", "w") as f:
    f.write(str(count+1))
