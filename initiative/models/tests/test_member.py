from testfixtures import compare
from initiative.models.encounter import Member
from initiative.models.stat_block import StatBlock


class TestMember(object):

    def test_as_dict_from_dict_same_object(self):
        s = StatBlock({'hit_points': 50, 'dexterity': 14})
        m = Member.npc('base', s)

        d = m.as_dict()
        new = Member.empty()
        new.from_dict(d)

        compare(actual=new.base_name, expected=m.base_name)
        compare(actual=new.name, expected=m.name)
        compare(actual=new.piece_name, expected=m.piece_name)
        compare(actual=new.is_player, expected=m.is_player)
        compare(actual=new.used_slots, expected=m.used_slots)
        compare(actual=new.current_hp, expected=m.current_hp)
        compare(actual=new.hit_points, expected=m.hit_points)
        compare(actual=new.initiative, expected=m.initiative)
        compare(actual=new.is_alive, expected=m.is_alive)
        compare(actual=new.current_turn, expected=m.current_turn)
