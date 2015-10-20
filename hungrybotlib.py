#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import ast
import urllib2 as u2
import json
from slackclient import SlackClient
import xml.etree.ElementTree as et



def getListOfChan(sc):
    listsOfChans = json.loads(sc.api_call("channels.list"))
    chans = {str(listsOfChans[u'channels'][i][u'name']):str(listsOfChans[u'channels'][i][u'id']) for i in range(len(listsOfChans[u'channels']))}
    return chans



def sayFood(food, chansToDisp, token):
    '''
    Affiche le texte food sur les channels DISPLAY_TO_CHANS
    '''

    sc = SlackClient(token)
    chans = getListOfChan(sc)

    for chan in chansToDisp:
        sc.api_call("chat.postMessage", as_user="true", channel=chans[chan], text=food)


def parseMenu(menu_url, days):
    menuString = u2.urlopen(menu_url)
    menuString = menuString.read()
    menuXML = et.fromstring(menuString)

    weekStr = menuXML[0][3][3].text

    # days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    daysStr = []

    # Split for each days
    for day in days:
        temp = weekStr.split(day)
        daysStr.append(temp[0])
        weekStr = temp[1]

    daysStr.pop(0)  #ozef du debut

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
                    daysPlates[i][j].append(temp.encode('utf-8'))
                except:
                    pass

    return daysPlates


def cacheMenus(menu_file, menu_url, days):
    menus = parseMenu(menu_url, days)
    with open(menu_file, "w") as menuFile:
        menuFile.write(str(menus))


def getMenus(menu_file):
    with open(menu_file, "r") as f:
        s = f.read()
        menus = ast.literal_eval(s)
    return menus
