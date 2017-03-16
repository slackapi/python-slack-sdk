class Im(object):
    '''
    IMs represent direct message channels between two users on Slack.
    '''
    def __init__(self, server, user, im_id):
        self.server = server
        self.user = user
        self.id = im_id

    def __eq__(self, compare_str):
        return compare_str in (self.id, self.user)

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        fmt = "{0} : {1:.40}"
        return "\n".join(fmt.format(key, value) for key, value
                         in self.__dict__.items() if key != "server")

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        '''
        Sends a message to a this IM (or DM depending on your preferred terminology).

        :Args:
            message (message) - the string you'd like to send to the IM

        :Returns:
            None
        '''
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)
