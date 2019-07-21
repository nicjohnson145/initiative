import npyscreen

from initiative.constants import STAT_DISPLAY
from initiative.ui.custom_mutt import _CustomMutt
from initiative.ui.helpful_controller import HelpfulController
from initiative.util import add_to_encounter
from initiative.models.encounter import Member


class CombatLines(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.combat_display() if isinstance(member, Member) else str(member)

    def actionHighlighted(self, member, _keypress):
        if not member.is_player:
            self.parent.parentApp.getForm(STAT_DISPLAY).value = member.stat_block
            self.parent.parentApp.switchForm(STAT_DISPLAY)


class CombatController(HelpfulController):

    def create(self):
        self.add_action(':d(amage)?$', self.damage_member, False)
        self.add_action(':h(eal)?$', self.heal_member, False)
        self.add_action(':activate$', self.activate_member, False)
        self.add_action(':deactivate$', self.deactivate_member, False)
        self.add_action(':add$', self.add_member, False)
        self.add_action(':remove$', self.remove_member, False)
        self.add_action(':p(layers)?$', self.add_players, False)
        self.add_action(':change$', self.change_attribute, False)
        self.add_action(':t(urn)?$', self.turn, False)

    def damage_member(self, command_line, widget_proxy, live):
        pass

    def heal_member(self, command_line, widget_proxy, live):
        pass

    def activate_member(self, command_line, widget_proxy, live):
        pass

    def deactivate_member(self, command_line, widget_proxy, live):
        pass

    def add_member(self, command_line, widget_proxy, live):
        add_to_encounter(self.parent.parentApp, self.parent.encounter)

    def remove_member(self, command_line, widget_proxy, live):
        self.parent.encounter.remove_member(self.parent.selected)
        self.parent.update()

    def add_players(self, command_line, widget_proxy, live):
        pass

    def change_attribute(self, command_line, widget_proxy, live):
        pass

    def turn(self, command_line, widget_proxy, live):
        pass


class CombatDisplay(_CustomMutt):

    ACTION_CONTROLLER = CombatController
    MAIN_WIDGET_CLASS = CombatLines

    def create(self):
        super().create()
        self.encounter = None

    def beforeEditing(self):
        self.update()

    def update(self):
        self.wMain.values = self.encounter.alive
        self.wMain.update()

    @property
    def selected(self):
        return self.wMain.values[self.wMain.cursor_line]
