import curses
import logging

import npyscreen

from initiative.constants import COMBAT_DISPLAY, ENCOUNTER_EDIT, ENCOUNTER_EXT, MAIN
from initiative.models.encounter import Encounter
from initiative.ui.custom_mutt import _CustomMutt
from initiative.ui.helpful_controller import HelpfulController
from initiative.ui.mutli_directory_seacher import MultiDirectorySearcher

NO_ENCOUNTER = 'No encounters'
NO_FILES = [NO_ENCOUNTER]

log = logging.getLogger(__name__)

E_KEY = ord('e')
R_KEY = ord('r')
NOOP_ARGS = [None, None, None]


class EncounterSearcher(MultiDirectorySearcher):

    def considered_file(self, filename):
        return filename.endswith(ENCOUNTER_EXT)


class EncounterResults(npyscreen.MultiLineAction):
    def actionHighlighted(self, _value, keypress):
        dispatch = {
            E_KEY: self.parent.action_controller.edit_encounter,
            curses.ascii.NL: self.parent.action_controller.start_encounter,
            curses.ascii.CR: self.parent.action_controller.start_encounter,
            curses.ascii.SP: self.parent.action_controller.start_encounter,
        }
        func = dispatch.get(keypress, lambda *args: None)
        func(*NOOP_ARGS)


class EncounterListController(HelpfulController):
    def create(self):
        self.add_action('^/.*', self.search, True)
        self.add_action('^:(add|create|new)', self.create_encounter, False)
        self.add_action('^:edit', self.edit_encounter, False)
        self.add_action('^:start$', self.start_encounter, False)
        self.add_action('^:q(uit)?', self.quit, False)

    def help_message(self):
        return self.help_table(
            ['/<search>', 'Filter by search criteria'],
            [':(add|create|new)', 'Create a new encounter'],
            [':edit', 'Edit selected encounter'],
            [':start', 'Start selected encounter'],
            [':q(uit)', 'Quit'],
        )

    def search(self, command_line, widget_proxy, live):
        self.parent.searcher.set_regex(command_line[1:])
        self.parent.wMain.values = self.parent.searcher.get_files()
        self.parent.wMain.update(clear=True)

    def create_encounter(self, command_line, widget_proxy, live):
        self.parent.parentApp.getForm(ENCOUNTER_EDIT).encounter = Encounter.empty()
        self.parent.parentApp.switchForm(ENCOUNTER_EDIT)

    def edit_encounter(self, command_line, widget_proxy, live):
        enc = self.load_encounter(self.parent.selected)
        self.parent.parentApp.getForm(ENCOUNTER_EDIT).encounter = enc
        self.parent.parentApp.switchForm(ENCOUNTER_EDIT)

    def load_encounter(self, file):
        return Encounter.load(file.full_path, self.parent.parentApp.config.encounter_path)

    def quit(self, command_line, widget_proxy, live):
        self.parent.parentApp.switchForm(MAIN)

    def start_encounter(self, command_line, widget_proxy, live):
        if self.parent.selected != NO_ENCOUNTER:
            encounter = self.load_encounter(self.parent.selected)
            self.parent.parentApp.getForm(COMBAT_DISPLAY).encounter = encounter
            self.parent.parentApp.switchForm(COMBAT_DISPLAY)


class EncounterListDisplay(_CustomMutt):

    ACTION_CONTROLLER = EncounterListController
    MAIN_WIDGET_CLASS = EncounterResults

    def create(self):
        super().create()
        self.searcher = EncounterSearcher()
        self.searcher.set_directories(self.parentApp.config.encounter_path)
        self.add_handlers({
            E_KEY: self.wMain.h_act_on_highlighted,
            R_KEY: self.wMain.h_act_on_highlighted,
        })

    def beforeEditing(self):
        self.wStatus1.value = "Encounters"
        self.wStatus2.value = "Command"
        self.searcher.reset_regex()
        self.searcher.refresh()
        files = self.searcher.get_files()
        if len(files) == 0:
            self.wMain.values = NO_FILES
        else:
            self.wMain.values = files

