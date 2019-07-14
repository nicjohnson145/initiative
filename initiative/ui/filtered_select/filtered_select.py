import json
import os
import re
from textwrap import dedent
from cached_property import cached_property

import npyscreen

from initiative.constants import ENCOUNTER_ADDITION, SPELL, SPELL_DISPLAY, STAT_DISPLAY, STATS
from initiative.custom_mutt import _CustomMutt
from initiative.helpful_controller import HelpfulController
from initiative.models.spell_block import SpellBlock
from initiative.models.stat_block import StatBlock
from initiative.models.encounter import Member


class File(object):

    def __init__(self, full_path, root):
        self.full_path = full_path
        self.root = root

    @cached_property
    def display_name(self):
        return os.path.relpath(self.full_path, self.root)

    @cached_property
    def sort_name(self):
        return os.path.basename(self.full_path)

    def __str__(self):
        return self.display_name


class FileSearcher(object):

    DEFAULT_REGEX = re.compile(r'.*')

    def __init__(self):
        self._directories = None
        self._files = []
        self.reset_regex()

    def reset_regex(self):
        self._regex = self.DEFAULT_REGEX

    def set_directories(self, *directories):
        self._directories = directories
        self._files = self.walk_fs()

    def refresh(self):
        self._files = self.walk_fs()

    def walk_fs(self):
        objs = []
        for directory in self._directories:
            objs.extend(self._walk_directory(directory))
        return objs

    def _walk_directory(self, directory):
        objs = []
        for root, _, files in os.walk(directory):
            for file in files:
                if self.consideredFile(file):
                    full_path = os.path.join(root, file)
                    objs.append(File(full_path, directory))
        return objs

    def consideredFile(self, filename):
        if filename.startswith('.'):
            return False
        elif filename.startswith('__'):
            return False
        return True

    def set_regex(self, value):
        self._regex = re.compile(value)

    def get_files(self):
        files = [file for file in self._files if self._regex.search(file.display_name)]
        return sorted(files, key=lambda x: x.sort_name)


class FileResults(npyscreen.MultiLineAction):
    def actionHighlighted(self, value, keypress):
        if self.parent.type_ in (STATS, SPELL):
            self.display_block(value)
        elif self.parent.type_ == ENCOUNTER_ADDITION:
            self.add_to_encounter(value)

    def display_block(self, value):
        instance = self._load_value(value)
        form_name = self.parent.get_form_name()
        self.parent.parentApp.getForm(form_name).value = instance
        self.parent.parentApp.switchForm(form_name)

    def add_to_encounter(self, value):
        encounter = self.parent.encounter
        stat_block = self._load_value(value)
        instance = encounter.get_instance_for_name(stat_block.name)
        name = f"{stat_block.name}_{instance}"
        encounter.add_member(Member.npc(name, stat_block))
        self.parent.parentApp.switchFormPrevious()

    def _load_value(self, value):
        with open(value.full_path) as fl:
            data = json.load(fl)
        klass = self.parent.get_block()
        return klass(data)


class FileListController(HelpfulController):
    def create(self):
        self.add_action('^/.*', self.search, True)

    def search(self, command_line, widget_proxy, live):
        self.parent.searcher.set_regex(command_line[1:])
        self.parent.wMain.values = self.parent.searcher.get_files()
        self.parent.wMain.display()

    def help_message(self):
        base = dedent("""
            Press / and begin typing to search.
            Supports regular expressions
            Press <Enter> to return control to list navigation
        """)
        return base


class FileListDisplay(_CustomMutt):

    ACTION_CONTROLLER = FileListController
    MAIN_WIDGET_CLASS = FileResults

    def create(self):
        super().create()
        self.encounter = None
        self.searcher = FileSearcher()
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
        })

    def set_type(self, value):
        self.type_ = value

    def beforeEditing(self):
        self.wStatus1.value = "Listing"
        self.wStatus2.value = "Command"
        self.searcher.set_directories(*self.get_directories())
        self.searcher.reset_regex()
        self.wMain.values = self.searcher.get_files()

    def get_block(self):
        blocks = {
            STATS: StatBlock,
            SPELL: SpellBlock,
            ENCOUNTER_ADDITION: StatBlock,
        }
        return blocks[self.type_]

    def get_form_name(self):
        forms = {
            STATS: STAT_DISPLAY,
            SPELL: SPELL_DISPLAY,
            ENCOUNTER_ADDITION: None,
        }
        return forms[self.type_]

    def get_directories(self):
        directories = {
            STATS: [
                os.path.join(self.parentApp.root_dir, 'monsters'),
                self.parentApp.config.extra_npcs_path,
            ],
            SPELL: [
                os.path.join(self.parentApp.root_dir, 'spells'),
            ],
            ENCOUNTER_ADDITION: [
                os.path.join(self.parentApp.root_dir, 'monsters'),
                self.parentApp.config.extra_npcs_path,
            ],
        }
        return directories[self.type_]
