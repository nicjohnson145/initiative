import curses
import logging
import os
import pickle
from textwrap import dedent

import npyscreen

from initiative.constants import ENCOUNTER_ADDITION, FILTERED_SELECT, STAT_DISPLAY
from initiative.ui.custom_mutt import _CustomMutt
from initiative.ui.helpful_controller import HelpfulController
from initiative.models.encounter import Encounter, Member

NO_MEMBERS = ['No Members']
NEW_ENCOUNTER = 'New-Encounter'

log = logging.getLogger(__name__)


class RelativeFileComplete(npyscreen.Autocomplete):

    SHOW_HIDDEN_FILES = False

    def auto_complete(self, _key_press):
        # Incase there's a ~ in there
        self.value = os.path.expanduser(self.value)
        if os.path.exists(self.value) and not self.value.endswith('/'):
            self.value += '/'

        head, tail = os.path.split(self.value)
        dirs = [f for f in os.listdir(head) if self.filter_files(head, tail, f)]
        if len(dirs) == 0:
            curses.beep()
        elif len(dirs) == 1:
            self.value = os.path.join(head, dirs[0]) + '/'
        else:
            new_tail = dirs[self.get_choice(dirs)]
            self.value = os.path.join(head, new_tail) + '/'
        self.cursor_position = len(self.value)

    def filter_files(self, head, tail, file):
        if not self.SHOW_HIDDEN_FILES and file.startswith('.'):
            return False
        isDir = os.path.isdir(os.path.join(head, file))
        return isDir and tail in file


class TitleRelativeFileComplete(npyscreen.TitleText):
    _entry_type = RelativeFileComplete


class EncounterMembers(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.edit_display() if isinstance(member, Member) else str(member)

    def actionHighlighted(self, member, keypress):
        if keypress in (curses.ascii.NL, curses.ascii.CR):
            if not member.is_player:
                self.display_stat_block(member.stat_block)

    def display_stat_block(self, stat_block):
        self.parent.parentApp.getForm(STAT_DISPLAY).value = stat_block
        self.parent.parentApp.switchForm(STAT_DISPLAY)


class EncounterEditController(HelpfulController):

    def create(self):
        self.add_action(':add', self.add_member, False)
        self.add_action(':remove', self.remove_member, False)
        self.add_action(':name', self.name_encounter, False)
        self.add_action(':s(ave)?!?', self.save_encounter, False)
        self.add_action(':q(uit)?', self.quit, False)

    def add_member(self, _command_line, _widget_proxy, _live):
        if self.confirmed_valid():
            form = self.parent.parentApp.getForm(FILTERED_SELECT)
            form.set_type(ENCOUNTER_ADDITION)
            form.encounter = self.parent.encounter
            self.parent.parentApp.switchForm(FILTERED_SELECT)

    def confirmed_valid(self):
        if not self.parent.encounter.valid:
            msg = "Must name encounter before adding members"
            npyscreen.notify_confirm(msg, title='Invalid Encounter')
            return False
        return True

    def remove_member(self, _command_line, _widget_proxy, _live):
        pass

    def name_encounter(self, command_line, _widget_proxy, _live):
        name = command_line.replace(':name', '').strip()
        self.parent.set_encounter_name(name)

    def save_encounter(self, command_line, _widget_proxy, _live):
        if self.confirmed_valid():
            encounter = self.parent.encounter
            if '!' in command_line or encounter.location is None:
                self.prompt_file_location()
            self.save_file_location()

    def prompt_file_location(self):
        location, name = self._show_file_dialog()
        self.parent.encounter.name = name
        self.parent.encounter.location = location
        os.makedirs(location, exist_ok=True)

    def _show_file_dialog(self):
        form = npyscreen.PopupWide(name="Encounter Save", color='STANDOUT')
        # Not sure what this does yet, modeling off the utilNotify code in npyscreen
        form.preserve_selected_widget = True

        locationwidget = form.add(TitleRelativeFileComplete, name="Location")
        locationwidget.value = self._get_starting_location()

        namewidget = form.add(npyscreen.TitleText, name='Name')
        namewidget.value = self.parent.encounter.name

        form.editw = 0
        form.edit()
        return locationwidget.value, namewidget.value

    def _get_starting_location(self):
        if self.parent.encounter.location is None:
            return self.parent.parentApp.config.encounter_path
        else:
            return self.parent.encounter.location

    def save_file_location(self):
        with open(self.parent.encounter.path, 'wb') as fl:
            pickle.dump(self.parent.encounter, fl, fix_imports=False)
        self.parent.pending_edits = False

    def quit(self, _command_line, _widget_proxy, _live):
        if self.parent.pending_edits:
            msg = 'You have edits pending on this encounter, do you want to exit without saving?'
            exit_anyway = npyscreen.notify_yes_no(msg, title="Pending Edits")
            if not exit_anyway:
                return
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
        self.encounter = Encounter.empty()
        self.pending_edits = False

    def beforeEditing(self):
        self.wStatus2.value = 'Command'
        if self.encounter.valid:
            self.from_encounter()
        else:
            self.as_new_encounter()

    def as_new_encounter(self):
        self.wStatus1.value = NEW_ENCOUNTER
        self.wMain.values = NO_MEMBERS

    def from_encounter(self):
        self.wStatus1.value = self.encounter.name
        self.wMain.values = self.encounter.all_members

    def set_encounter_name(self, name):
        self.encounter.name = name
        self.pending_edits = True
        self.set_status1_preserve_line(self.encounter.name)

    def show_members(self):
        self.wMain.values = self.encounter.all_members
        self.wMain.update()
