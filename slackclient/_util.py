class SearchList(list):

    def find(self, name):
        items = []
        for child in self:
            if child.__class__ == self.__class__:
                items += child.find(name)
            else:
                if child == name:
                    items.append(child)

        if len(items) == 1:
            return items[0]
        elif items:
            return items
        else:
            return None


class SearchDict(dict):
    def find(self, search_string):
        # Find the user by name
        user = self.get(search_string)
        if user:
            return user
        else:
            # If the user can't be found by name, try searching by ID
            for name, user in self.items():
                if str(user.id) == search_string:
                    return user
