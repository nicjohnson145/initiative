import json
import os

import npyscreen
from cached_property import cached_property

from initiative.constants import FILTERED_SELECT, MAIN, SPELL, STAT_DISPLAY, STATS
from initiative.models.stat_block import StatBlock
from initiative.ui.filtered_select.filtered_select import FileListDisplay
from initiative.ui.stat_display.stat_display_form import StatDisplay


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, editable=False, name='Main Menu')

        self.add(npyscreen.ButtonPress, name='Encounters',
                 when_pressed_function=lambda: print('Encounters'))

        self.add(npyscreen.ButtonPress, name='Enemies',
                 when_pressed_function=lambda: self.switch_to_selection_list(STATS))

        self.add(npyscreen.ButtonPress, name='Spells',
                 when_pressed_function=lambda: print('Spells'))

        self.add(npyscreen.ButtonPress, name='Individual',
                 when_pressed_function=lambda: self.switch_to_individual())

    def switch_to_individual(self):
        path = os.path.join(self.parentApp.root_dir, 'monsters', 'aboleth.json')
        with open(path) as fl:
            data = json.load(fl)
        sb = StatBlock(data)
        self.parentApp.getForm(STAT_DISPLAY).value = sb
        self.parentApp.switchForm(STAT_DISPLAY)

    def switch_to_selection_list(self, type_):
        self.parentApp.getForm(FILTERED_SELECT).set_type(type_)
        self.parentApp.switchForm(FILTERED_SELECT)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm(MAIN, MainMenu)
        self.addForm(STAT_DISPLAY, StatDisplay)
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
