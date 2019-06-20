import os

import npyscreen
from cached_property import cached_property

from initiative.constants import FILTERED_SELECT, MAIN, SPELL, SPELL_DISPLAY, STAT_DISPLAY, STATS
from initiative.ui.filtered_select.filtered_select import FileListDisplay
from initiative.ui.spell_display.spell_display import SpellDisplay
from initiative.ui.stat_display.stat_display_form import StatDisplay


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, editable=False, name='Main Menu')

        self.add(npyscreen.ButtonPress, name='Encounters',
                 when_pressed_function=lambda: print('Encounters'))

        self.add(npyscreen.ButtonPress, name='Enemies',
                 when_pressed_function=lambda: self.switch_to_selection_list(STATS))

        self.add(npyscreen.ButtonPress, name='Spells',
                 when_pressed_function=lambda: self.switch_to_selection_list(SPELL))

    def switch_to_selection_list(self, type_):
        self.parentApp.getForm(FILTERED_SELECT).set_type(type_)
        self.parentApp.switchForm(FILTERED_SELECT)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm(MAIN, MainMenu)
        self.addForm(STAT_DISPLAY, StatDisplay)
        self.addForm(SPELL_DISPLAY, SpellDisplay)
        self.addForm(FILTERED_SELECT, FileListDisplay)

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
