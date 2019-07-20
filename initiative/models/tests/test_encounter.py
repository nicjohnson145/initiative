from nose.tools import nottest
from testfixtures import compare

from initiative.models.encounter import Encounter, Member


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
