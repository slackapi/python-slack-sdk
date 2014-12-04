python-slackclient
================
A basic client for Slack.com. Uses the Slack Real Time Messaging (RTM) API.

Dependencies
----------
* websocket-client https://pypi.python.org/pypi/websocket-client/

Installation ([virtualenv](http://virtualenv.readthedocs.org/en/latest/) is recommended.)
-----------

    git clone https://github.com/liris/websocket-client.git
    cd websocket-client
    sudo python setup.py install
  
Usage
-----
See examples in [doc/examples](doc/examples/)
See [python-rtmbot](https://github.com/slackhq/python-rtmbot/) for an active project using this library.

###Connecting
---------
_Note:_ You must obtain a token for the user/bot. You can find or generate these at the [Slack API](https://api.slack.com/#auth) page.

    import time
    from slackclient import SlackClient
    
    token = "xoxp-28192348123947234198234"# found at https://api.slack.com/#auth)
    sc = SlackClient(token)
    if sc.connect():
        while True:
            print sc.read()
            time.sleep(1)
    else:
        print "Connection Failed, invalid token?"
    

###Objects
-----------

####[SlackClient.**server**]  
Server object owns the websocket and all nested channel information.

SlackClient.server.**ping**()  
Send a ping to Slack via the websocket. Reply should be received.

SlackClient.server.**join_channel([name])**  
Join a channel called (name)

SlackClient.server.**send_to_websocket([data])**  
Send a JSON message via the websocket. See RTM documentation for allowed types.

-----------

####[SlackClient.server.**channels**]  
A searchable list of all known channels within the parent server. Call `print (sc instance)` to see the entire list.

SlackClient.server.**channels.find([identifier])**
The identifier can be either name or Slack channel ID. See above for examples.

SlackClient.server.**channnels[int].send_message([text])**
Send message [text] to [int] channel in the channels list.

SlackClient.server.**channnels.find([identifier]).send_message([text])**
Send message [text] to channel [identifier], which can be either channel name or ID. Ex "#general" or "C182391"
