import os
import pickle
import re

import npyscreen

NO_FILES = ['No encounters']


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
        pass


class EncounterListController(npyscreen.ActionControllerSimple):
    def create(self):
        self.add_action('^/.*', self.search, True)
        self.add_action('^:add', self.create_encounter, False)
        self.add_action('^:reset', self.reset_encounter, False)
        self.add_action('^:edit', self.edit_encounter, False)

    def search(self, command_line, widget_proxy, live):
        self.parent.searcher.set_regex(command_line[1:])
        self.parent.wMain.values = self.parent.searcher.get_files()
        self.parent.wMain.update(clear=True)

    def create_encounter(self, command_line, widget_proxy, live):
        pass

    def reset_encounter(self, command_line, widget_proxy, live):
        pass

    def edit_encounter(self, command_line, widget_proxy, live):
        pass


class EncounterListDisplay(npyscreen.FormMuttActiveTraditional):

    ACTION_CONTROLLER = EncounterListController
    MAIN_WIDGET_CLASS = EncounterResults

    def create(self):
        super().create()
        self.searcher = EncounterSearcher(self.parentApp.config.encounter_path)
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
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

