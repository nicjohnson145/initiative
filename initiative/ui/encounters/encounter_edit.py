import logging

import npyscreen

from initiative.models.encounter import Encounter

NO_MEMBERS = 'No Members'
DISPLAYED_MEMBERS = 6
BOX_HEIGHT = DISPLAYED_MEMBERS + 2

log = logging.getLogger(__name__)


class MemberEditMutliLineAction(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.edit_display()

    def actionHighlighted(self, value, keypress):
        pass


class MultiLineBox(npyscreen.BoxTitle):
    _contained_widget = MemberEditMutliLineAction


class EncounterEdit(npyscreen.ActionForm):

    def create(self):
        super().create()
        self.encounter = None
        self.is_new = None
        self.encounter_name = self.add(
            npyscreen.TitleText, name='Encounter Name:', use_two_lines=False
        )
        self.members = self.add(
            MultiLineBox, name='Members', max_height=BOX_HEIGHT
        )

    def beforeEditing(self):
        if self.encounter is None:
            self.encounter = Encounter('<New Encounter>')
        self.populate_from_encounter()

    def populate_from_encounter(self):
        self.encounter_name.value = self.encounter.name
        self.members.values = self.encounter.all_members

    def on_ok(self):
        self.parentApp.switchFormPrevious()
