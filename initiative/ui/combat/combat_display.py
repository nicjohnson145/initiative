import re

import npyscreen

from initiative.constants import ENCOUNTER_LIST, STAT_DISPLAY
from initiative.models.encounter import Member
from initiative.ui.custom_mutt import _CustomMutt
from initiative.ui.helpful_controller import HelpfulController
from initiative.util import add_to_encounter


class CombatLines(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.combat_display() if isinstance(member, Member) else str(member)

    def actionHighlighted(self, member, _keypress):
        if not member.is_player:
            self.parent.parentApp.getForm(STAT_DISPLAY).value = member.stat_block
            self.parent.parentApp.switchForm(STAT_DISPLAY)


class CombatController(HelpfulController):

    digit_re = re.compile(r':.* +(?P<amt>\d+)')
    players_re = re.compile(r':p(layers)? +(?P<player_string>.*)')

    def create(self):
        self.add_action(':d(amage)', self.damage_member, False)
        self.add_action(':h(eal)', self.heal_member, False)
        self.add_action(':res(surect)?$', self.resurrect_member, False)
        self.add_action(':k(ill)?$', self.kill_member, False)
        self.add_action(':add$', self.add_member, False)
        self.add_action(':remove$', self.remove_member, False)
        self.add_action(':p(layers)?', self.add_players, False)
        self.add_action(':c(hange)?', self.change_attribute, False)
        self.add_action(':t(urn)?$', self.turn, False)
        self.add_action(':q(uit)?!?$', self.quit, False)

    def damage_member(self, command_line, widget_proxy, live):
        self._health_interation('damage', command_line)

    def heal_member(self, command_line, widget_proxy, live):
        self._health_interation('heal', command_line)

    def _health_interation(self, attr, cmd_line):
        match = self.digit_re.search(cmd_line)
        if match:
            func = getattr(self.parent.selected, attr)
            func(int(match.group('amt')))
            self.parent.update()

    def resurrect_member(self, command_line, widget_proxy, live):
        pass

    def kill_member(self, command_line, widget_proxy, live):
        self.parent.selected.is_alive = False
        self.parent.update()

    def add_member(self, command_line, widget_proxy, live):
        add_to_encounter(self.parent.parentApp, self.parent.encounter)

    def remove_member(self, command_line, widget_proxy, live):
        self.parent.encounter.remove_member(self.parent.selected)
        self.parent.update()

    def add_players(self, command_line, widget_proxy, live):
        match = self.players_re.search(command_line)
        if match:
            s = match.group('player_string')
            pairs = s.split(',')
            for pair in pairs:
                name, initiative = pair.split('-')
                player = Member.player(name, initiative)
                self.parent.encounter.add_member(player)
        self.parent.harsh_update()

    def change_attribute(self, command_line, widget_proxy, live):
        pass

    def turn(self, command_line, widget_proxy, live):
        self.parent.encounter.advance_turn()
        self.parent.update()

    def quit(self, command_line, widget_proxy, live):
        if '!' not in command_line:
            self.parent.encounter.save()
        self.parent.parentApp.switchForm(ENCOUNTER_LIST)


class CombatDisplay(_CustomMutt):

    ACTION_CONTROLLER = CombatController
    MAIN_WIDGET_CLASS = CombatLines

    def create(self):
        super().create()
        self.encounter = None

    def beforeEditing(self):
        self.encounter.indicate_turn()
        self.update()

    def harsh_update(self):
        self.wMain.values = []
        self.wMain.display()
        self.update()

    def update(self):
        self.wMain.values = self.encounter.alive
        self.wMain.update(clear=True)
