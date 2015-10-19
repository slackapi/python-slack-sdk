#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
from random import choice
import time
import hungrybotlib as l
from slackclient import SlackClient


# hungrybot token for Slack api
TOKEN = "xoxb-12362166850-sy4hycJ5edUT8rczQMCbT2TS"

DISPLAY_TO_CHANS = ["ahtable"]


if __name__ == "__main__":
    """
    type of meal should be an integer and the only argument, it value can be:
    .0 : Déjeuner au RAK
    .1 : Diner au RAK
    .2 : Déjeuner à la caféteria
    .3 : Diner à la caféteria
    """
    typeOfMeal = int(sys.argv[1])
    plates = l.getMenus()
    
    day = time.localtime(time.time())[6]

    choice_str = {3: ["vous pourrez choisir entre %s, %s ou %s"], 4:["vous pourrez choisir entre %s ou %s ou %s voire %s"], 5:["vous avez le choix : %s, %s, %s, %s ou %s"], 6:["plein de bonnes choses : %s, %s, %s, %s, %s ou encore %s"]}
    if typeOfMeal == 0:
        entree = plates[day][typeOfMeal][0]
        dessert = plates[day][typeOfMeal][-1]
        plats = plates[day][typeOfMeal][1:-1]
    
        hello_morning = ["Coucou mes lapinous ! ", "Salut mes choupinous, ", "Bonjour mes petits coeurs ! "]
        what_morning = ["Alors aujourd'hui au menu... \n", "On va trop bien bouffer aujourd'hui !\n", "Ahlalala, j'aimerais bien être un humain parfois vu ce que vous mangez...\n"]
        
        what_dejeuner = ["Donc, ce midi, ", "Pour le déjeuner, "]
        entree_str = ["en entrée il y a : ", "vous pourrez commencer avec : "]
        plat_str = [";\npuis en plat principal ", " .\nEt pour manger, "]
        dessert_str = [";\net pour finir ", ".\nEn dessert :"]
        
        message = choice(hello_morning)+choice(what_morning)+choice(what_dejeuner)+choice(entree_str)+entree+choice(plat_str)+choice(choice_str[len(plats)])%tuple(plats)+choice(dessert_str)+dessert+"."        

    else:
        plats = plates[day][typeOfMeal]
        hello_diner = ["Ah enfin je commençais a voir la dalle...\¬", "A TAAAAAABLE\n"]
        what_dinner = ["Pour ce soir:", "Au diner:"]
        
        message = choice(hello_diner)+choice(what_dinner)+choice(choice_str[len(plats)])%tuple(plats)+"."

    
    l.sayFood(message, DISPLAY_TO_CHANS, TOKEN)
        
