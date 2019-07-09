from collections import defaultdict
from initiative.util import rollD20


class Encounter(object):

    def __init__(self, name, active=False):
        self.name = name
        self.members = []
        self.names = set()
        self.active = active

    def add_member(self, member):
        assert(member.name not in self.names)
        self.members.append(member)
        self.names.add(member.name)

    def remove_member(self, name):
        assert(name in self.names)
        index = None
        for idx, member in enumerate(self.members):
            if member.name == name:
                index = idx
                break

        assert(index is not None)
        del self.members[index]
        self.names.remove(name)

    @property
    def alive(self):
        return sorted((m for m in self.members if m.is_alive), key=lambda m: m.initiative)

    def __str__(self):
        pass


class Member(object):

    def __init__(self, name, stat_block=None, is_player=False, initiative=None):
        if not is_player:
            assert(stat_block is not None)
        else:
            assert(initiative is not None)

        self.name = name
        self.piece_name = ''
        self.stat_block = stat_block
        self.current_hp = self.stat_block.hit_points
        self.is_player = is_player
        self.used_slots = defaultdict(int)
        self.is_alive = True
        if initiative is None:
            self.roll_initiative()
        else:
            self.initiative = int(initiative)
        self.active = False

    def use_spell(self, level):
        self.used_slots[level] += 1

    def roll_initiative(self):
        self.initiative = rollD20() + self.stat_block.dexterity

    def heal(self, amt):
        self.current_hp += amt

    def damage(self, amt):
        self.current_hp -= amt

    def set_piece_name(self, name):
        self.piece_name = name

