import logging
import os
from collections import defaultdict
import json

from initiative.constants import ENCOUNTER_EXT
from initiative.models.stat_block import StatBlock
from initiative.util import make_string_file_safe, roll_d20

log = logging.getLogger(__name__)

PIECE_NAME_LEN = 20
NAME_LEN = 22


class Encounter(object):

    @classmethod
    def empty(cls):
        return cls(None)

    @classmethod
    def from_dict(cls, value, encounterRoot):
        e = Encounter.empty()
        e._from_dict(value, encounterRoot)  # pylint: disable=W0212
        return e

    def __init__(self, name, location=None, active=False):
        self.name = name
        self.members_by_base_name = defaultdict(list)
        self.members = []
        self._active = active
        self.location = location
        self.turn_index = 0

    def add_member(self, member):
        if len(self.members) > 0 and member.initiative > self.current_turn_member.initiative:
            self.__next_index()
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
        has_higher_initiative = member.initiative > self.current_turn_member.initiative
        is_current = member == self.current_turn_member
        is_last = self.turn_index == len(self.members) - 1

        if has_higher_initiative:
            self.__previous_index()

        self._remove_member_from_list(self.members, member)
        if not has_higher_initiative and (is_current and is_last):
            self.__next_index()

        by_base = self.members_by_base_name[member.base_name]
        self._remove_member_from_list(by_base, member)
        if len(by_base) == 0:
            del self.members_by_base_name[member.base_name]
        else:
            self.calculate_instance(by_base)
        self.maintain_order()
        self.indicate_turn()

    def _remove_member_from_list(self, member_list, member):
        index = None
        for i, m in enumerate(member_list):
            if m == member:
                index = i
                break
        assert index is not None
        del member_list[index]

    def maintain_order(self):
        self.members.sort(key=lambda m: m.initiative, reverse=True)

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

    def indicate_turn(self):
        self.current_turn_member.current_turn = True

    def advance_turn(self):
        if len(self.alive) <= 1:
            return

        self.current_turn_member.current_turn = False
        self.__next_index()
        while not self.current_turn_member.is_alive:
            self.__next_index()
        self.indicate_turn()

    def __next_index(self):
        self.turn_index += 1
        if self.turn_index >= len(self.members):
            self.turn_index = 0

    def __previous_index(self):
        self.turn_index -= 1
        if self.turn_index == -1:
            self.turn_index = len(self.members) - 1

    def as_dict(self, encounterRoot):
        return {
            'name': self.name,
            'members': [m.as_dict() for m in self.members],
            'active': self._active,
            'location': os.path.relpath(self.location, encounterRoot),
            'turn_index': self.turn_index,
            'stat_blocks': self.__get_stat_block_dict(),
        }

    def __get_stat_block_dict(self):
        stat_blocks = {}
        for member in self.members:
            if member.is_player:
                continue

            block = member.stat_block
            if block.name not in stat_blocks:
                stat_blocks[block.name] = block.as_dict()

        return stat_blocks

    def _from_dict(self, value, encounterRoot):
        members = self.__build_members(value)
        members_by_base = self.__build_members_by_base(members)
        self.name = value['name']
        self.members_by_base_name = members_by_base
        self.members = members
        self._active = value['active']
        self.location = os.path.join(encounterRoot, value['location'])
        self.turn_index = value['turn_index']

    def __build_members(self, value):
        members = []
        stat_blocks = value['stat_blocks']
        for member_dict in value['members']:
            is_player = member_dict['is_player']
            member_dict['stat_block'] = None if is_player else stat_blocks[member_dict['block_name']]
            members.append(Member.from_dict(member_dict))

        return members

    def __build_members_by_base(self, member_list):
        members_by_base = defaultdict(list)
        for m in member_list:
            members_by_base[m.base_name].append(m)

        return members_by_base

    def save(self, encounterRoot):
        # Try getting the JSON string first to avoid writing a zeroed out file if there's an error
        json_str = json.dumps(self.as_dict(encounterRoot), indent=4)
        with open(self.path, 'w') as fl:
            fl.write(json_str)

    @classmethod
    def load(self, filepath, encounterRoot):
        with open(filepath, 'r') as fl:
            return Encounter.from_dict(json.load(fl), encounterRoot)


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
        active = '*' if self.current_turn else ' '
        if self.is_player:
            return f"{active}|{self.name}"
        else:
            return '|'.join([
                f'{active}',
                "{:<2}".format(self.initiative),
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
            'is_player': self.is_player,
            'used_slots': dict(self.used_slots),
            'current_hp': self.current_hp,
            'hit_points': self.hit_points,
            'initiative': self.initiative,
            'is_alive': self.is_alive,
            'current_turn': self.current_turn,
            'block_name': None if self.is_player else self.stat_block.name
        }

    def _from_dict(self, value):
        self.base_name = value['base_name']
        self.name = value['name']
        self.piece_name = value['piece_name']
        self.is_player = value['is_player']
        self.stat_block = None if self.is_player else StatBlock(value['stat_block'])
        self.used_slots = defaultdict(int, value['used_slots'])
        self.current_hp = value['current_hp']
        self.hit_points = value['hit_points']
        self.initiative = value['initiative']
        self.is_alive = value['is_alive']
        self.current_turn = value['current_turn']
