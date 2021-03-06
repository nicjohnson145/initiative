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
NOTHING = 'n/a'


class StatBlock(object):

    def __init__(self, obj):
        self.from_dict(obj)

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
    def raw_strength(self):
        return self._obj['strength']

    @property
    def strength_mod(self):
        return self.get_modifier(self.raw_strength)

    @property
    def dexterity(self):
        return self.get_attribute_string('dexterity')

    @property
    def raw_dexterity(self):
        return self._obj['dexterity']

    @property
    def dexterity_mod(self):
        return self.get_modifier(self.raw_dexterity)

    @property
    def intelligence(self):
        return self.get_attribute_string('intelligence')

    @property
    def raw_intelligence(self):
        return self._obj['intelligence']

    @property
    def intelligence_mod(self):
        return self.get_modifier(self.raw_intelligence)

    @property
    def wisdom(self):
        return self.get_attribute_string('wisdom')

    @property
    def raw_wisdom(self):
        return self._obj['wisdom']

    @property
    def wisdom_mod(self):
        return self.get_modifier(self.raw_wisdom)

    @property
    def constitution(self):
        return self.get_attribute_string('constitution')

    @property
    def raw_constitution(self):
        return self._obj['constitution']

    @property
    def constitution_mod(self):
        return self.get_modifier(self.raw_constitution)

    @property
    def charisma(self):
        return self.get_attribute_string('charisma')

    @property
    def raw_charisma(self):
        return self._obj['charisma']

    @property
    def charisma_mod(self):
        return self.get_modifier(self.raw_charisma)

    @cached_property
    def saving_throws(self):
        throws = [(key + ' +' + str(value)) for key, value in self._obj.items() if '_save' in key]
        return ', '.join(throws)

    @cached_property
    def skills(self):
        skills = [(key + '+' + str(value)) for key, value in self._obj.items() if key in SKILLS]
        return ', '.join(skills)

    @property
    def damage_vulnerabilities(self):
        return ', '.join(self._obj['damage_vulnerabilities'])

    @property
    def damage_resistances(self):
        return ', '.join(self._obj['damage_resistances'])

    @property
    def damage_immunities(self):
        return ', '.join(self._obj['damage_immunities'])

    @property
    def condition_immunities(self):
        return ', '.join(self._obj['condition_immunities'])

    @property
    def senses(self):
        return self._obj['senses']

    @property
    def languages(self):
        return self._obj['languages']

    @property
    def abilities(self):
        return [Ability(obj) for obj in self._obj.get('special_abilities', [])]

    @property
    def actions(self):
        return [Action(obj) for obj in self._obj.get('actions', [])]

    @property
    def legendary_actions(self):
        return [Ability(obj) for obj in self._obj.get('legendary_actions', [])]

    def get_modifier(self, value):
        return math.floor((value - 10) / 2)

    def get_attribute_string(self, attr):
        score = self._obj[attr]
        mod = self.get_modifier(score)
        sign = '+' if mod >= 0 else ''
        return f"{score} ({sign}{mod})"

    def as_dict(self):
        return self._obj

    def from_dict(self, value):
        self._obj = value


class Action(object):

    def __init__(self, obj):
        self._obj = obj

    @property
    def name(self):
        return self._obj['name']

    @property
    def description(self):
        return self._obj['desc']

    @property
    def attack_bonus(self):
        return f"[+{self._obj['attack_bonus']}]" if 'attack_bonus' in self._obj else ''

    @property
    def damage(self):
        dice = self._obj.get('damage_dice', '')
        bonus = self._obj.get('damage_bonus', '')
        bonus_str = f'+{bonus}' if bonus else ''
        if dice == '' and bonus == '':
            return ''
        else:
            return f"({dice}{bonus_str})"

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.name} {self.attack_bonus} {self.damage}"

    def as_popup(self):
        return f"{self.name}\n\n{self.description}"


class Ability(object):

    def __init__(self, obj):
        self._obj = obj

    @property
    def name(self):
        return self._obj['name']

    @property
    def description(self):
        return self._obj['desc']

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"[{self.name}]"

    def as_popup(self):
        return f"{self.name}\n\n{self.description}"
