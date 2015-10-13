#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib2 as u2
import json
from slackclient import SlackClient
import xml.etree.ElementTree as et

# hungrybot token for Slack api
TOKEN = "xoxb-12362166850-sy4hycJ5edUT8rczQMCbT2TS"

DISPLAY_TO_CHANS = ["ahtable"]




def getListOfChan(socket):
    listsOfChans = json.loads(sc.api_call("channels.list"))    
    chans = {str(listsOfChans[u'channels'][i][u'name']):str(listsOfChans[u'channels'][i][u'id']) for i in range(len(listsOfChans[u'channels']))}
    return chans


def sayFood(food):
    '''
    Affiche le texte food sur les channels DISPLAY_TO_CHANS
    '''
    for chan in DISPLAY_TO_CHANS:
        sc.api_call("chat.postMessage", as_user="true", channel=chans[chan], text=food)


def parseMenu():
    menuString = u2.urlopen('http://services.telecom-bretagne.eu/rak/rss/menus.xml')
    menuString = menuString.read()
    menuXML = et.fromstring(menuString)    

    weekStr = menuXML[0][3][3].text

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    daysStr = []

    # Split for each days
    for day in days:
        temp = weekStr.split(day)
        daysStr.append(temp[0])
        weekStr = temp[1]

    daysStr.pop(0) #ozef du debut

    
    # Split for each meal
    daysMenu = []
    for dayStr in daysStr:
        temp1 = dayStr.split('<STRONG>Dejeuner</STRONG>',1)
        temp2 = temp1[1].split(' <BR/>***Rampe***<BR/>| <STRONG>Diner</STRONG> ',1)
        rampeDej = temp2[0]
        temp3 = temp2[1].split(' <BR/>***Cafeteria***<BR/>| <STRONG>Dejeuner</STRONG> ',1)
        rampeDin = temp3[0]
        temp4 = temp3[1].split(' <BR/>***Cafeteria***<BR/>| <STRONG>Diner</STRONG> ')
        cafetDej = temp4[0]
        temp5 = temp4[1].split(' <BR/>--- ')
        cafetDin = temp5[0]
        
        daysMenu.append([rampeDej,rampeDin,cafetDej,cafetDin])

    daysPlates = []
    # Get out of the hyperlink
    for i in range(len(daysMenu)):
        daysPlates.append([])
        for j in range(len(daysMenu[i])):
            daysPlates[i].append([])
            
            plates = daysMenu[i][j].split('|')
            for plate in plates:
                try:
                    temp = plate.split('>',1)[1].split('<',1)[0]
                    daysPlates[i][j].append(temp)
                except:
                    pass
                
        
    return daysPlates

        

sc = SlackClient (TOKEN)
chans = getListOfChan (sc)    




#announceFood(message, chans)
