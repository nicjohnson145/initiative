from cached_property import cached_property


class StatBlock(object):

    def init(self, obj):
        self._obj = obj

    @property
    def name(self):
        return self._obj['name']

    @property
    def armor_class(self):
        return self._obj['armor_class']

    @property
    def hit_points(self):
        return self._obj['hit_points']

    @property
    def speed(self):
        return self._obj['speed']

    @property
    def strength(self):
        return self._obj['strength']

    @property
    def dexterity(self):
        return self._obj['dexterity']

    @property
    def intelligence(self):
        return self._obj['intelligence']

    @property
    def wisdom(self):
        return self._obj['wisdom']

    @property
    def constitution(self):
        return self._obj['constitution']

    @property
    def charisma(self):
        return self._obj['charisma']

    @cached_property
    def saving_throws(self):
        saves = [(key, value) for key, value in self._obj.items() if '_save' in key]

