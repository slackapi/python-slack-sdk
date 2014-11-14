class Channel(object):
    def __init__(self, server, name, identifier, active, last_read=0, prepend_name="", members=[]):
        super(Channel, self).__init__(name, identifier)
        self.type = "channel"
        self.server = server
        self.name = prepend_name + self.name
        self.typing = {}
        self.active = active
        self.members = set(members)
        self.last_read = float(last_read)
        self.previous_prnt_name = ""
        self.previous_prnt_message = ""
        if active:
            self.create_buffer()
            self.attach_buffer()
            self.update_nicklist()
    def __eq__(self, compare_str):
        if compare_str == self.fullname() or compare_str == self.name or compare_str == self.identifier or compare_str == self.name[1:] or (compare_str == self.channel_buffer and self.channel_buffer is not None):
            return True
        else:
            return False
    def create_buffer(self):
        channel_buffer = w.buffer_search("", "%s.%s" % (self.server.domain, self.name))
        if channel_buffer:
            self.channel_buffer = channel_buffer
        else:
            self.channel_buffer = w.buffer_new("%s.%s" % (self.server.domain, self.name), "input", self.name, "", "")
            w.buffer_set(self.channel_buffer, "short_name", 'loading..')
    def attach_buffer(self):
        channel_buffer = w.buffer_search("", "%s.%s" % (self.server.domain, self.name))
        if channel_buffer != main_weechat_buffer:
            self.channel_buffer = channel_buffer
#            w.buffer_set(self.channel_buffer, "highlight_words", self.server.nick)
        else:
            self.channel_buffer = None
    def detach_buffer(self):
        if self.channel_buffer != None:
            w.buffer_close(self.channel_buffer)
            self.channel_buffer = None
    def update_nicklist(self):
        w.buffer_set(self.channel_buffer, "nicklist", "1")
        w.nicklist_remove_all(self.channel_buffer)
        for user in self.members:
            user = self.server.users.find(user)
            if user.presence == 'away':
                w.nicklist_add_nick(self.channel_buffer, "", user.name, user.color(), " ", "", 1)
            else:
                w.nicklist_add_nick(self.channel_buffer, "", user.name, user.color(), "+", "", 1)
    def fullname(self):
        return "%s.%s" % (self.server.domain, self.name)
    def has_user(self, name):
        return name in self.members
    def user_join(self, name):
        self.members.add(name)
        self.update_nicklist()
    def user_leave(self, name):
        if name in self.members:
            self.members.remove(name)
        self.update_nicklist()
    def set_active(self):
        self.active = True
    def set_inactive(self):
        self.active = False
    def set_typing(self, user):
        self.typing[user] = time.time()
    def send_message(self, message):
        request = {"type":"message", "channel":self.identifier, "text": message}
        self.server.ws.send(json.dumps(request))
    def open(self, update_remote=True):
        self.create_buffer()
        self.active = True
        self.get_history()
        if update_remote:
            t = time.time()
            async_slack_api_request(self.server.domain, self.server.token, SLACK_API_TRANSLATOR[self.type]["join"], {"name":self.name.lstrip("#"), "ts":t})
    def close(self, update_remote=True):
        if self.active == True:
            self.active = False
            self.detach_buffer()
        if update_remote:
            t = time.time()
            async_slack_api_request(self.server.domain, self.server.token, SLACK_API_TRANSLATOR[self.type]["leave"], {"channel":self.identifier, "ts":t})
    def closed(self):
        self.channel_buffer = None
        self.close()
    def unset_typing(self, user):
        try:
            del self.typing[user]
        except:
            pass
    def is_someone_typing(self):
        for user in self.typing.keys():
            if self.typing[user] + 4 > time.time():
                return True
        return False
    def get_typing_list(self):
        typing = []
        for user in self.typing.keys():
            if self.typing[user] + 4 > time.time():
                typing.append(user)
        return typing
    def mark_read(self, update_remote=True):
        t = time.time()

        if self.channel_buffer:
            w.buffer_set(self.channel_buffer, "unread", "")
        if update_remote:
            self.last_read = time.time()
            self.set_read_marker(self.last_read)
    def set_read_marker(self, time):
        async_slack_api_request(self.server.domain, self.server.token, SLACK_API_TRANSLATOR[self.type]["mark"], {"channel":self.identifier, "ts":time})
    def rename(self, name=None, fmt=None, gray=False):
        if not gray:
            color = w.color('default')
        else:
            color = w.color('darkgray')
        if self.channel_buffer:
            if name:
                new_name = name
            elif fmt:
                new_name = fmt % (self.name[1:])
            else:
                new_name = self.name
            w.buffer_set(self.channel_buffer, "short_name", color + new_name)
    def buffer_prnt(self, user='unknown user', message='no message', time=0, backlog=False):
        set_read_marker = False
        time = float(time)
        message = message.encode('ascii', 'ignore')
        if time != 0 and self.last_read >= time:
            tags = "no_highlight,notify_none,logger_backlog_end"
            set_read_marker = True
        elif message.find(self.server.nick) > -1:
            tags = "notify_highlight"
        elif user != self.server.nick and self.name in self.server.users:
            tags = "notify_private,notify_message"
        else:
            tags = "notify_message"
        time = int(float(time))
        if self.channel_buffer:
            if self.server.users.find(user) and user != self.server.nick:
                name = self.server.users.find(user).colorized_name()
            else:
                name = user
            if message != self.previous_prnt_message:
                #dbg([message, self.previous_prnt_message])
                w.prnt_date_tags(self.channel_buffer, time, tags, "%s\t%s" % (name, message))
                #eventually maybe - doesn't reprint name if next message is same user
                #if name != self.previous_prnt_name:
                #    w.prnt_date_tags(self.channel_buffer, time, tags, "%s\t%s" % (name, message))
                #    self.previous_prnt_name = name
                #else:
                #    w.prnt_date_tags(self.channel_buffer, time, tags, "%s\t%s" % ("", message))
            self.previous_prnt_message = message
            if set_read_marker:
                self.mark_read(False)
        else:
            dbg("failed to print something..")
    def get_history(self):
        if self.active:
            t = time.time()
            async_slack_api_request(self.server.domain, self.server.token, SLACK_API_TRANSLATOR[self.type]["history"], {"channel":self.identifier, "ts":t, "count":BACKLOG_SIZE})


