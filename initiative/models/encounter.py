import logging
import os
from collections import defaultdict

from initiative.constants import ENCOUNTER_EXT
from initiative.models.stat_block import StatBlock
from initiative.util import make_string_file_safe, roll_d20

log = logging.getLogger(__name__)

PIECE_NAME_LEN = 18
NAME_LEN = 15


class Encounter(object):

    @classmethod
    def empty(cls):
        return cls(None)

    @classmethod
    def from_dict(cls, value):
        e = Encounter.empty()
        e._from_dict(value)  # pylint: disable=W0212
        return e

    def __init__(self, name, location=None, active=False):
        self.name = name
        self.members_by_base_name = defaultdict(list)
        self.members = []
        self._active = active
        self.location = location
        self.turn_index = 0

    def add_member(self, member):
        self.members.append(member)
        by_base = self.members_by_base_name[member.base_name]
        by_base.append(member)
        self.calculate_instance(by_base)
        self.maintain_order()

    def calculate_instance(self, member_list):
        if len(member_list) == 1:
            member_list[0].name = member_list[0].base_name
        else:
            for index, member in enumerate(member_list):
                member.name = member.base_name + '_' + str(index + 1)

    def remove_member(self, member):
        self._remove_member_from_list(self.members, member)
        by_base = self.members_by_base_name[member.base_name]
        self._remove_member_from_list(by_base, member)
        if len(by_base) == 0:
            del self.members_by_base_name[member.base_name]
        else:
            self.calculate_instance(by_base)
        self.maintain_order()

    def _remove_member_from_list(self, member_list, member):
        index = None
        for i, m in enumerate(member_list):
            if m == member:
                index = i
                break
        assert index is not None
        del member_list[index]

    def maintain_order(self):
        self.members.sort(key=lambda m: m.initiative)

    @property
    def alive(self):
        return list(filter(lambda m: m.is_alive, self.members))

    @property
    def all_members(self):
        return self.members

    @property
    def filename(self):
        return make_string_file_safe(self.name) + ENCOUNTER_EXT

    @property
    def valid(self):
        return self.name is not None

    @property
    def path(self):
        return os.path.join(self.location, self.filename)

    @property
    def current_turn_member(self):
        return self.members[self.turn_index]

    def advance_turn(self):
        self.current_turn_member.current_turn = False

    def as_dict(self):
        return {
            'name': self.name,
            'members_by_base_name': self.__members_by_base_name_to_dict(),
            'members': [m.as_dict() for m in self.members],
            'active': self._active,
            'location': self.location,
            'turn_index': self.turn_index,
        }

    def __members_by_base_name_to_dict(self):
        return {name: [m.as_dict() for m in l] for name, l in self.members_by_base_name.items()}

    def _from_dict(self, value):
        self.name = value['name']
        self.members_by_base_name = self.__members_by_base_name_from_dict(value['members_by_base_name'])  # noqa
        self.members = [Member.from_dict(d) for d in value['members']]
        self._active = value['active']
        self.location = value['location']
        self.turn_index = value['turn_index']

    def __members_by_base_name_from_dict(self, value):
        return {name: [Member.from_dict(d) for d in l] for name, l in value.items()}


class Member(object):

    def __init__(self, base_name=None, name=None, stat_block=None, is_player=False, initiative=None):  # noqa
        self.base_name = base_name
        self.name = base_name if name is None else name
        self.piece_name = ' ' * PIECE_NAME_LEN
        self.stat_block = stat_block
        self.is_player = is_player
        self.used_slots = defaultdict(int)
        self.current_hp = 0 if stat_block is None else self.stat_block.hit_points
        self.hit_points = 0 if stat_block is None else self.stat_block.hit_points
        self.set_initiative(initiative)
        self.is_alive = True
        self.current_turn = False

    @classmethod
    def empty(cls):
        return cls(initiative=1)

    @classmethod
    def from_dict(cls, value):
        m = Member.empty()
        m._from_dict(value)  # pylint: disable=W0212
        return m

    @classmethod
    def player(cls, base_name, initiative):
        return cls(base_name, is_player=True, initiative=initiative)

    @classmethod
    def npc(cls, base_name, stat_block):
        return cls(base_name, stat_block=stat_block)

    def use_spell(self, level):
        self.used_slots[level] += 1

    def set_initiative(self, value=None):
        self.initiative = self.roll_initiative() if value is None else int(value)

    def roll_initiative(self):
        return roll_d20() + self.stat_block.dexterity_mod

    def heal(self, amt):
        self.current_hp += amt

    def damage(self, amt):
        self.current_hp -= amt

    def set_piece_name(self, name):
        self.piece_name = name

    @property
    def spell_slot_str(self):
        return ' '.join([f'{level}[{uses}]' for level, uses in sorted(self.used_slots.items())])

    def edit_display(self):
        return self.name

    def combat_display(self):
        active = '+' if self.current_turn else '-'
        if self.is_player:
            return f"{active}|{self.name}"
        else:
            return '|'.join([
                f'{active}',
                ('{:<%s}' % PIECE_NAME_LEN).format(self.piece_name),
                ('{:<%s}' % NAME_LEN).format(self.name),
                '{:<3} / {:<3}'.format(self.current_hp, self.hit_points),
                f'{self.spell_slot_str}',
            ])

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.__class__.__name__ + f"(name='{self.name}')"

    def as_dict(self):
        return {
            'base_name': self.base_name,
            'name': self.name,
            'piece_name': self.piece_name,
            'stat_block': self.stat_block.as_dict(),
            'is_player': self.is_player,
            'used_slots': dict(self.used_slots),
            'current_hp': self.current_hp,
            'hit_points': self.hit_points,
            'initiative': self.initiative,
            'is_alive': self.is_alive,
            'current_turn': self.current_turn,
        }

    def _from_dict(self, value):
        self.base_name = value['base_name']
        self.name = value['name']
        self.piece_name = value['piece_name']
        self.stat_block = StatBlock(value['stat_block'])
        self.is_player = value['is_player']
        self.used_slots = defaultdict(int, value['used_slots'])
        self.current_hp = value['current_hp']
        self.hit_points = value['hit_points']
        self.initiative = value['initiative']
        self.is_alive = value['is_alive']
        self.current_turn = value['current_turn']
