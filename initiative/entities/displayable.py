
class Displayable(object):

    def __init__(self, name, health, class_, spell_slots=None):
        self._name = name
        self._active = False
        self._health = health
        self._class = class_
        self._spell_slots = [] if spell_slots is None else spell_slots

    @property
    def name(self):
        return self._name

    @property
    def active(self):
        return '*' if self._active else ''

    @property
    def health(self):
        return self._health

    @property
    def class_(self):
        return self._class

    @property
    def spell_slots(self):
        return self._spell_slots

    def as_row(self):
        return [
            self.active,
            self.name,
            self.class_,
            self.spell_slots
        ]

