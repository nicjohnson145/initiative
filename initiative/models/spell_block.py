class SpellBlock(object):

    def __init__(self, obj):
        self._obj = obj

    @property
    def name(self):
        return self._obj['name']

    @property
    def level(self):
        return self._obj['level']

    @property
    def casting_time(self):
        return self._obj['casting_time']

    @property
    def range(self):
        return self._obj['range']

    @property
    def components(self):
        return ', '.join(self._obj['components'])

    @property
    def concentration(self):
        return str(self._obj['concentration'])

    @property
    def duration(self):
        return self._obj['duration']

    @property
    def description(self):
        return '\n'.join(self._obj['desc'])

    @property
    def higher_levels(self):
        return '\n'.join(self._obj.get('higher_level', ''))

