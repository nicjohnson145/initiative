import curses
import logging
import os
import re

import npyscreen

from initiative.constants import ENCOUNTER_EDIT
from initiative.custom_mutt import _CustomMutt
from initiative.helpful_controller import HelpfulController
from initiative.models.encounter import Encounter, Member

NO_FILES = ['No encounters']

log = logging.getLogger(__name__)

E_KEY = ord('e')
R_KEY = ord('r')
NOOP_ARGS = [None, None, None]


class EncounterSearcher(object):

    DEFAULT_REGEX = re.compile(r'.*')

    def __init__(self, directory):
        self._directory = directory
        self.reset_regex()

    def reset_regex(self):
        self._regex = self.DEFAULT_REGEX

    def set_regex(self, value):
        self._regex = re.compile(value)

    def get_files(self):
        found_files = []
        for root, _, files in os.walk(self._directory):
            rel_path = os.path.relpath(root, start=self._directory)
            rel_path = '' if rel_path == '.' else rel_path
            for file in files:
                path = os.path.join(rel_path, file)
                if file.endswith('.encounter') and self._regex.search(path):
                    found_files.append(path)
        return found_files


class EncounterResults(npyscreen.MultiLineAction):
    def actionHighlighted(self, value, keypress):
        dispatch = {
            E_KEY: self.parent.action_controller.edit_encounter,
            R_KEY: self.parent.action_controller.reset_encounter,
            curses.ascii.NL: self.parent.action_controller.edit_encounter,
            curses.ascii.CR: self.parent.action_controller.edit_encounter,
            curses.ascii.SP: self.parent.action_controller.edit_encounter,
        }
        func = dispatch.get(keypress, lambda *args: None)
        func(*NOOP_ARGS)


class EncounterListController(HelpfulController):
    def create(self):
        self.add_action('^/.*', self.search, True)
        self.add_action('^:(add|create)', self.create_encounter, False)
        self.add_action('^:reset', self.reset_encounter, False)
        self.add_action('^:edit', self.edit_encounter, False)

    def search(self, command_line, widget_proxy, live):
        self.parent.searcher.set_regex(command_line[1:])
        self.parent.wMain.values = self.parent.searcher.get_files()
        self.parent.wMain.update(clear=True)

    def create_encounter(self, command_line, widget_proxy, live):
        self.parent.parentApp.getForm(ENCOUNTER_EDIT).encounter = Encounter.empty()
        self.parent.parentApp.switchForm(ENCOUNTER_EDIT)

    def reset_encounter(self, command_line, widget_proxy, live):
        log.info("reset")

    def edit_encounter(self, command_line, widget_proxy, live):
        enc = Encounter('Mistshore')
        enc.add_member(Member.player('player1', 5))
        enc.add_member(Member.player('player2', 6))
        enc.add_member(Member.player('player3', 7))
        self.parent.parentApp.getForm(ENCOUNTER_EDIT).encounter = enc
        self.parent.parentApp.switchForm(ENCOUNTER_EDIT)


class EncounterListDisplay(_CustomMutt):

    ACTION_CONTROLLER = EncounterListController
    MAIN_WIDGET_CLASS = EncounterResults

    def create(self):
        super().create()
        self.searcher = EncounterSearcher(self.parentApp.config.encounter_path)
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
            E_KEY: self.wMain.h_act_on_highlighted,
            R_KEY: self.wMain.h_act_on_highlighted,
        })

    def beforeEditing(self):
        self.wStatus1.value = "Encounters"
        self.wStatus2.value = "Command"
        self.searcher.reset_regex()
        files = self.searcher.get_files()
        if len(files) == 0:
            self.wMain.values = NO_FILES
        else:
            self.wMain.values = files

    @property
    def selected(self):
        return self.wMain.values[self.wMain.cursor_line]
