from nose.plugins.attrib import attr
from nose.tools import nottest
from testfixtures import compare

from initiative.models.encounter import Encounter, Member
from initiative.util import expected_failure


class TestEncounter(object):

    @nottest
    def make_testee(self):
        return Encounter.empty()

    def test_add_member_single_member_no_suffix(self):
        testee = self.make_testee()
        m = Member.player('player', initiative=5)
        testee.add_member(m)

        actual = testee.all_members
        expected = [
            Member.player('player', initiative=5)
        ]
        compare(actual=actual, expected=expected)

    def test_add_member_multiple_of_same_has_suffix(self):
        testee = self.make_testee()
        testee.add_member(Member.player('player', initiative=5))
        testee.add_member(Member.player('player', initiative=5))

        actual = testee.all_members
        expected = [
            Member.player('player_1', initiative=5),
            Member.player('player_2', initiative=5),
        ]
        compare(actual=actual, expected=expected)

    def test_remove_member_maintains_order(self):
        testee = self.make_testee()
        testee.add_member(Member.player('player', initiative=5))
        testee.add_member(Member.player('player', initiative=5))
        testee.add_member(Member.player('non-player', initiative=5))
        testee.add_member(Member.player('player', initiative=5))

        actual = testee.all_members
        expected = [
            Member.player('player_1', initiative=5),
            Member.player('player_2', initiative=5),
            Member.player('non-player', initiative=5),
            Member.player('player_3', initiative=5),
        ]
        compare(actual=actual, expected=expected)

        testee.remove_member(
            Member(base_name='player', name='player_2', initiative=5, is_player=True)
        )

        actual = testee.all_members
        expected = [
            Member.player('player_1', initiative=5),
            Member.player('non-player', initiative=5),
            Member.player('player_2', initiative=5),
        ]
        compare(actual=actual, expected=expected)

        testee.remove_member(
            Member(base_name='player', name='player_1', initiative=5, is_player=True)
        )

        actual = testee.all_members
        expected = [
            Member.player('non-player', initiative=5),
            Member.player('player', initiative=5),
        ]
        compare(actual=actual, expected=expected)

    @nottest
    def setup_turn_test(self, turn_index=1):
        e = Encounter.empty()
        members = [
            Member.player('player', initiative=15),
            Member.player('player', initiative=10),  # it's this guys turn
            Member.player('player', initiative=5),
        ]
        list(map(e.add_member, members))
        e.turn_index = turn_index
        return e, members

    def test_add_member_before_current_turn_maintains_turn_index(self):
        encounter, members = self.setup_turn_test()
        encounter.add_member(Member.player('not_a_player', initiative=12))
        compare(actual=encounter.current_turn_member.name, expected=members[1].name)

    def test_add_member_after_current_turn_maintains_turn_index(self):
        encounter, members = self.setup_turn_test()
        encounter.add_member(Member.player('not_a_player', initiative=8))
        compare(actual=encounter.current_turn_member.name, expected=members[1].name)

    def test_remove_member_before_current_turn_maintains_turn_index(self):
        encounter, members = self.setup_turn_test()
        encounter.remove_member(members[0])
        compare(actual=encounter.current_turn_member.name, expected=members[1].name)

    def test_remove_member_after_current_turn_maintains_turn_index(self):
        encounter, members = self.setup_turn_test()
        encounter.remove_member(members[2])
        compare(actual=encounter.current_turn_member.name, expected=members[1].name)

    @attr('current')
    def test_remove_member_current_turn_in_middle_advances_turn(self):
        encounter, members = self.setup_turn_test()
        encounter.remove_member(members[1])
        compare(actual=encounter.current_turn_member.name, expected=members[2].name)

    def test_remove_member_current_turn_at_end_advances_turn_to_start(self):
        encounter, members = self.setup_turn_test(turn_index=2)
        encounter.remove_member(members[2])
        compare(actual=encounter.current_turn_member.name, expected=members[0].name)
