class Channel(object):
    def __init__(self, server, name, channel_id, members=None):
        self.server = server
        self.name = name
        self.id = channel_id
        self.members = members or []

    def __eq__(self, compare_str):
        if (compare_str in (self.id, self.name) or
           "#" + compare_str == self.name):
            return True
        else:
            return False

    def __str__(self):
        return "\n".join("{0} : {1:.40}".format(key, value) for key, value
                         in self.__dict__.items())

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)
