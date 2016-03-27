class Channel(object):
    def __init__(self, server, name, channel_id, members=None):
        self.server = server
        self.name = name
        self.id = channel_id
        self.members = members or []

    def __eq__(self, compare_str):
        return compare_str in (self.id, self.name) or "#" + compare_str == self.name

    def __str__(self):
        fmt = "{} : {:.40}"
        return "\n".join(fmt.format(key, str(value)) for key, value in self.__dict__.items())

    def __repr__(self):
        return self.__str__()

    def send_message(self, message):
        message_json = {"type": "message", "channel": self.id, "text": message}
        self.server.send_to_websocket(message_json)
