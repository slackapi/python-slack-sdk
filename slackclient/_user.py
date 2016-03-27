class User(object):
    def __init__(self, server, name, user_id, real_name, tz):
        self.tz = tz
        self.name = name
        self.real_name = real_name
        self.server = server
        self.id = user_id

    def __eq__(self, compare_str):
        return compare_str in (self.id, self.name)

    def __str__(self):
        fmt = "{} : {:.40}"
        return "\n".join(fmt.format(key, str(value)) for key, value
                         in self.__dict__.items() if key != "server")

    def __repr__(self):
        return self.__str__()
