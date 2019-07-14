import logging
from textwrap import dedent

import npyscreen

from initiative.custom_mutt import _CustomMutt
from initiative.helpful_controller import HelpfulController
from initiative.models.encounter import Encounter

NO_MEMBERS = ['No Members']

log = logging.getLogger(__name__)


class EncounterMembers(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.edit_display() 
    def actionHighlighted(self, value, keypress):
        pass


class EncounterEditController(HelpfulController):

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

    def _help_message(self):
        return dedent("""
            Actions:
                - :add -> Add a Member to the encounter
                - :remove <member_id> -> Remove a member from the encounter
                - :name <name>-> Set the name of the encounter
                - :save -> Save all edits made to this encounter to disk
                - :q/:quit -> Leave this screen and return to the previous
        """)


class EncounterEdit(_CustomMutt):

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
        self.set_status1_preserve_line(self.encounter.name)
