# Installation process

## Requirements :
pip install websockets-client

## WHAT TODO :
create a configuration file:
```
cp config.py.tpl config.py
```

Edit the configuration file with your token

Rajouter ceci dans le crontab:
```
30 10 * * * cd /home/nimag42/TB/perso/hungrybot && python2 bot.py 0
30 18 * * * cd /home/nimag42/TB/perso/hungrybot && python2 bot.py 1
00 22 * * 0 cd /home/nimag42/TB/perso/hungrybot && python2 majDb.py
```
