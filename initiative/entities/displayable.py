
class Displayable(object):

    def __init__(self, name):
        self._name = name
        self._active = False

    @property
    def name(self):
        return self._name

    @property
    def active(self):
        return '*' if self._active else ''

    def as_row(self):
        return [
            self.active,
            self.name,
        ]


