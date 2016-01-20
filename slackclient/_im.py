class Im(object):
    def __init__(self, server, user, id):
        self.server = server
        self.user = user
        self.id = id

    def __eq__(self, compare_str):
        if self.id == compare_str or self.user == compare_str:
            return True
        else:
            return False

    def __str__(self):
        data = ""
        for key in list(self.__dict__.keys()):
            if key != "server":
                data += "{0} : {1}\n".format(key, str(self.__dict__[key])[:40])
        return data

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)

