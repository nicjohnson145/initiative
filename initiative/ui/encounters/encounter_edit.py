import logging

import npyscreen
import curses

from initiative.models.encounter import Encounter

NO_MEMBERS = ['No Members']

log = logging.getLogger(__name__)


class EncounterMembers(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.edit_display()

    def actionHighlighted(self, value, keypress):
        pass


class EncounterEditController(npyscreen.ActionControllerSimple):

    def create(self):
        self.add_action(':add', self.add_member, False)
        self.add_action(':remove', self.remove_member, False)
        self.add_action(':name', self.name_encounter, False)
        self.add_action(':save', self.save_encounter, False)
        self.add_action(':q(uit)?', self.quit, False)

    def add_member(self, command_line, widget_proxy, live):
        pass

    def remove_member(self, command_line, widget_proxy, live):
        pass

    def name_encounter(self, command_line, widget_proxy, live):
        name = command_line.replace(':name', '').strip()
        self.parent.set_encounter_name(name)

    def save_encounter(self, command_line, widget_proxy, live):
        pass

    def quit(self, command_line, widget_proxy, live):
        if self.parent.pending_edits:
            msg = 'You have edits pending on this encounter, do you want to exit without saving?'
            val = npyscreen.notify_yes_no(msg, title="Pending Edits")
            log.info(val)
        self.parent.parentApp.switchFormPrevious()


class EncounterEdit(npyscreen.FormMuttActiveTraditional):

    ACTION_CONTROLLER = EncounterEditController
    MAIN_WIDGET_CLASS = EncounterMembers

    def create(self):
        super().create()
        self.encounter = None
        self.pending_edits = False

    def beforeEditing(self):
        self.wStatus2.value = 'Command'
        if self.encounter is None:
            self.as_new_encounter()
        else:
            self.from_encounter()

    def as_new_encounter(self):
        self.wStatus1.value = '<New Encounter>'
        self.wMain.values = NO_MEMBERS

    def from_encounter(self):
        self.wStatus1.value = self.encounter.name
        self.wMain.values = self.encounter.all_members

    def set_encounter_name(self, name):
        if self.encounter is None:
            self.encounter = Encounter(name)
        else:
            self.encounter.name = name
        self.pending_edits = True
        self.set_status_preserve_line('wStatus1', self.encounter.name)

    def set_status_preserve_line(self, attr, value):
        status = getattr(self, attr)
        status.value = value
        status.update()
        line_start = len(status.value) + 1
        line_end = self.columns - line_start - 1
        self.curses_pad.hline(status.rely, line_start, curses.ACS_HLINE, line_end)
