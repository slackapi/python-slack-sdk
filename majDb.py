#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import hungrybotlib as l
from random import choice

import config as cfg


l.cacheMenus(cfg.menu_file, cfg.menu_url, cfg.days)

with open("counter", "r") as f:
    count = int(f.read())
text = ["Une nouvelle semaine de bouffe !", "Et voila, je viens de mettre à jour les menus.", "Le RAK vient de me dire ce qu'on mange la semaine prochaine..."]

if count == 1:
    l.sayFood("Bonjour ! Je suis fier de me présenter, je suis HungryBot, je vais vous guider tout au long de vos études en vous indiquant ce que vous pourrez manger de bon au RAK de TB !", cfg.channels, cfg.token)
else:
    l.sayFood(choice(text)+"\nC'est la "+str(count)+"ème semaine que je suis à votre service.", cfg.channels, cfg.token)

with open("counter", "w") as f:
    f.write(str(count+1))
