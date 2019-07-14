import json
import os
import re
from textwrap import dedent

import npyscreen

from initiative.constants import SPELL, SPELL_DISPLAY, STAT_DISPLAY, STATS
from initiative.custom_mutt import _CustomMutt
from initiative.helpful_controller import HelpfulController
from initiative.models.spell_block import SpellBlock
from initiative.models.stat_block import StatBlock


class FileSearcher(object):

    DEFAULT_REGEX = re.compile(r'.*')

    def __init__(self):
        self._directory = None
        self.reset_regex()

    def reset_regex(self):
        self._regex = self.DEFAULT_REGEX

    def set_directory(self, value):
        self._directory = value

    def set_regex(self, value):
        self._regex = re.compile(value)

    def get_files(self):
        files = []
        for path in os.listdir(self._directory):
            if not os.path.basename(path).startswith('__'):
                files.append(path)
        return [path for path in files if self._regex.search(path)]


class FileResults(npyscreen.MultiLineAction):
    def actionHighlighted(self, value, keypress):
        directory = self.parent.get_directory()
        path = os.path.join(directory, value)
        with open(path) as fl:
            data = json.load(fl)
        klass = self.parent.get_block()
        instance = klass(data)
        form_name = self.parent.get_form_name()
        self.parent.parentApp.getForm(form_name).value = instance
        self.parent.parentApp.switchForm(form_name)


class FileListController(HelpfulController):
    def create(self):
        self.add_action('^/.*', self.search, True)

    def search(self, command_line, widget_proxy, live):
        self.parent.searcher.set_regex(command_line[1:])
        self.parent.wMain.values = self.parent.searcher.get_files()
        self.parent.wMain.display()

    def help_message(self):
        return dedent("""
            Press / and begin typing to search.
            Supports regular expressions
            Press <Enter> to return control to list navigation
        """)


class FileListDisplay(_CustomMutt):

    ACTION_CONTROLLER = FileListController
    MAIN_WIDGET_CLASS = FileResults

    def create(self):
        super().create()
        self.searcher = FileSearcher()
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
        })

    def set_type(self, value):
        self._type = value

    def beforeEditing(self):
        self.wStatus1.value = "Listing"
        self.wStatus2.value = "Command"
        self.searcher.set_directory(self.get_directory())
        self.searcher.reset_regex()
        self.wMain.values = self.searcher.get_files()

    def get_block(self):
        blocks = {
            STATS: StatBlock,
            SPELL: SpellBlock,
        }
        return blocks[self._type]

    def get_form_name(self):
        forms = {
            STATS: STAT_DISPLAY,
            SPELL: SPELL_DISPLAY,
        }
        return forms[self._type]

    def get_directory(self):
        directories = {
            STATS: os.path.join(self.parentApp.root_dir, 'monsters'),
            SPELL: os.path.join(self.parentApp.root_dir, 'spells'),
        }
        return directories[self._type]
