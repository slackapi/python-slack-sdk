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
        elif items != []:
            return items

