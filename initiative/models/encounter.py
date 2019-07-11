from collections import defaultdict
from initiative.util import rollD20


class Encounter(object):

    def __init__(self, name, active=False):
        self.name = name
        self.members = []
        self.names = set()
        self.active = active
        self.instances = defaultdict(int)

    def get_instance_for_name(self, name):
        self.instances[name] += 1
        return self.instances[name]

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

    @property
    def all_members(self):
        return self.members

    def __str__(self):
        pass


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

    @classmethod
    def player(cls, name, initiative):
        return cls(name, is_player=True, initiative=initiative)

    @classmethod
    def npc(cls, name, stat_block):
        return cls(name, stat_block=stat_block)

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
