from cached_property import cached_property
import math

SKILLS = set([
    "acrobatics"
    "animal_handling"
    "arcana"
    "athletics"
    "deception"
    "history"
    "insight"
    "intimidation"
    "investigation"
    "medicine"
    "nature"
    "perception"
    "performance"
    "persuasion"
    "religion"
    "sleight_of_hand"
    "stealth"
    "survival"
])


class StatBlock(object):

    def __init__(self, obj):
        self._obj = obj
        self._current_hp = self._obj['hit_points']

    @property
    def current_hp(self):
        return self._current_hp

    @current_hp.setter
    def current_hp(self, value):
        self._current_hp = value

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
        return self.get_attribute_string('strength')

    @property
    def dexterity(self):
        return self.get_attribute_string('dexterity')

    @property
    def intelligence(self):
        return self.get_attribute_string('intelligence')

    @property
    def wisdom(self):
        return self.get_attribute_string('wisdom')

    @property
    def constitution(self):
        return self.get_attribute_string('constitution')

    @property
    def charisma(self):
        return self.get_attribute_string('charisma')

    @cached_property
    def saving_throws(self):
        throws = [(key + ' +' + str(value)) for key, value in self._obj.items() if '_save' in key]
        if len(throws) == 0:
            return 'None'
        return 'n/a' if len(throws) == 0 else ', '.join(throws)

    @cached_property
    def skills(self):
        return [(key, '+' + str(value)) for key, value in self._obj.items() if key in SKILLS]

    @property
    def damage_vulnerabilities(self):
        return self._obj['damage_vulnerabilities']

    @property
    def damage_resistances(self):
        return self._obj['damage_resistances']

    @property
    def damage_immunities(self):
        return self._obj['damage_immunities']

    @property
    def condition_immunities(self):
        return self._obj['condition_immunities']

    @property
    def senses(self):
        return self._obj['senses'].split(',')

    @property
    def languages(self):
        return self._obj['languages'].split(',')

    @property
    def abilities(self):
        return [(obj['name'], obj['desc']) for obj in self._obj.get('special_abilities', [])]

    @property
    def actions(self):
        return [(obj['name'], obj['desc']) for obj in self._obj['actions']]

    @property
    def legendary_actions(self):
        return [(obj['name'], obj['desc']) for obj in self._obj.get('legendary_actions', [])]

    def get_modifier(self, value):
        mod = math.floor((value - 10) / 2)
        sign = '+' if mod >= 0 else ''
        return sign + str(mod)

    def get_attribute_string(self, attr):
        score = self._obj[attr]
        mod = self.get_modifier(score)
        return f"{score} ({mod})"

