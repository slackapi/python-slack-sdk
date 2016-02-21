class Channel(object):
    def __init__(self, server, name, id, members=[]):
        self.server = server
        self.name = name
        self.id = id
        self.members = members

    def __eq__(self, compare_str):
        if self.name == compare_str or self.name == "#" + compare_str or self.id == compare_str:
            return True
        else:
            return False

    def __str__(self):
        data = ""
        for key in list(self.__dict__.keys()):
            data += "{0} : {1}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)

