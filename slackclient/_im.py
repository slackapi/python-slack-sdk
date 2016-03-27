class Im(object):
    def __init__(self, server, user, im_id):
        self.server = server
        self.user = user
        self.id = im_id

    def __eq__(self, compare_str):
        return compare_str in (self.id, self.user)

    def __str__(self):
        fmt = "{} : {:.40}"
        return "\n".join(fmt.format(key, str(value)) for key, value in self.__dict__.items())

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)
