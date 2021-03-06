import logging
import os

import npyscreen
from cached_property import cached_property

from initiative.constants import (
    COMBAT_DISPLAY, ENCOUNTER_EDIT, ENCOUNTER_LIST, FILTERED_SELECT, MAIN, SPELL, SPELL_DISPLAY,
    STAT_DISPLAY, STATS
)
from initiative.models.config import Config
from initiative.ui.combat.combat_display import CombatDisplay
from initiative.ui.encounters.encounter_display import EncounterListDisplay
from initiative.ui.encounters.encounter_edit import EncounterEdit
from initiative.ui.filtered_select.filtered_select import FileListDisplay
from initiative.ui.spell_display.spell_display import SpellDisplay
from initiative.ui.stat_display.stat_display_form import StatDisplay
from pathlib import Path


_log_path = os.path.join(Path.home(), 'app.log')
logging.basicConfig(filename=_log_path, filemode='w', level=logging.DEBUG,
                    format='%(name)s - %(levelname)s - %(message)s')

log = logging.getLogger(__name__)


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, editable=False, name='Main Menu')

        self.add(npyscreen.ButtonPress, name='Encounters',
                 when_pressed_function=lambda: self.parentApp.switchForm(ENCOUNTER_LIST))

        self.add(npyscreen.ButtonPress, name='NPCS',
                 when_pressed_function=lambda: self.switch_to_selection_list(STATS))

        self.add(npyscreen.ButtonPress, name='Spells',
                 when_pressed_function=lambda: self.switch_to_selection_list(SPELL))

    def switch_to_selection_list(self, type_):
        self.parentApp.getForm(FILTERED_SELECT).set_type(type_)
        self.parentApp.switchForm(FILTERED_SELECT)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.config = Config()

        self.addForm(MAIN, MainMenu)
        self.addForm(STAT_DISPLAY, StatDisplay)
        self.addForm(SPELL_DISPLAY, SpellDisplay)
        self.addForm(FILTERED_SELECT, FileListDisplay)
        self.addForm(ENCOUNTER_LIST, EncounterListDisplay)
        self.addForm(ENCOUNTER_EDIT, EncounterEdit)
        self.addForm(COMBAT_DISPLAY, CombatDisplay)

    @cached_property
    def root_dir(self):
        return os.path.dirname(__file__)


def main():
    try:
        App().run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
