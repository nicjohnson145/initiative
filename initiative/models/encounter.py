import logging
import os
from collections import OrderedDict, defaultdict

from initiative.util import make_string_file_safe, roll_d20
from initiative.constants import ENCOUNTER_EXT

log = logging.getLogger(__name__)


class Encounter(object):

    @classmethod
    def empty(cls):
        return cls(None)

    def __init__(self, name, location=None, active=False):
        self.name = name
        self.members = OrderedDict()
        self.names = set()
        self.active = active
        self.instances = defaultdict(int)
        self.location = location

    def get_name(self, name):
        if self.instances[name] == 0:
            # I haven't seen this name before, don't append a number
            self.instances[name] += 1
            return name
        elif self.instances[name] == 1:
            # I've seen this name exactly once, need to rename the first to include a number
            old = self.members.pop(name)
            old.name += '_1'
            self.members[old.name] = old
        self.instances[name] += 1
        return name + '_' + str(self.instances[name])

    def add_member(self, member):
        assert(member.name not in self.members)
        self.members[member.name] = member

    def remove_member(self, name):
        assert(name in self.names)
        del self.members[name]

    @property
    def alive(self):
        return sorted((m for m in self.members.values() if m.is_alive), key=lambda m: m.initiative)

    @property
    def all_members(self):
        return list(self.members.values())

    @property
    def filename(self):
        return make_string_file_safe(self.name) + ENCOUNTER_EXT

    @property
    def valid(self):
        return self.name is not None

    @property
    def path(self):
        log.info(self.location)
        log.info(self.filename)
        return os.path.join(self.location, self.filename)


class Member(object):

    def __init__(self, name, stat_block=None, is_player=False, initiative=None):
        if is_player:
            assert(initiative is not None)
        else:
            assert(stat_block is not None)

        self.name = name
        self.piece_name = ''
        self.stat_block = stat_block
        self.is_player = is_player
        self.used_slots = defaultdict(int)
        self.current_hp = 0 if is_player else self.stat_block.hit_points
        self.hit_points = 0 if is_player else self.stat_block.hit_points
        self.initiative = self.roll_initiative() if initiative is None else int(initiative)
        self.is_alive = True
        self._active = False

    @classmethod
    def player(cls, name, initiative):
        return cls(name, is_player=True, initiative=initiative)

    @classmethod
    def npc(cls, name, stat_block):
        return cls(name, stat_block=stat_block)

    def use_spell(self, level):
        self.used_slots[level] += 1

    def roll_initiative(self):
        self.initiative = roll_d20() + self.stat_block.raw_dexterity

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
        active = '+' if self._active else '-'
        return f"{active}|{self.piece_name:.18}|{self.name}|{self.spell_slot_str}"
