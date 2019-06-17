import json
import os

import npyscreen

from initiative.constants import MAIN, STAT_DISPLAY
from initiative.stat_block import StatBlock
from initiative.stat_display_form import StatDisplay


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, editable=False, name='Main Menu')

        self.add(npyscreen.ButtonPress, name='Encounters',
                 when_pressed_function=lambda: print('Encounters'))

        self.add(npyscreen.ButtonPress, name='Enemies',
                 when_pressed_function=lambda: print('Enemies'))

        self.add(npyscreen.ButtonPress, name='Spells',
                 when_pressed_function=lambda: print('Spells'))

        self.add(npyscreen.ButtonPress, name='Individual',
                 when_pressed_function=lambda: self.switch_to_individual())

    def switch_to_individual(self):
        current_dir = os.path.dirname(__file__)
        path = os.path.join(current_dir, 'monsters', 'aboleth.json')
        with open(path) as fl:
            data = json.load(fl)
        sb = StatBlock(data)
        self.parentApp.getForm(STAT_DISPLAY).value = sb
        self.parentApp.switchForm(STAT_DISPLAY)


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm(MAIN, MainMenu)
        self.addForm(STAT_DISPLAY, StatDisplay)


def main():
    try:
        App().run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
