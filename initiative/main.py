import npyscreen


class MainMenu(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.TitleFixedText, editable=False, name='Main Menu')

        self.add(npyscreen.ButtonPress, name='Encounters',
                 when_pressed_function=lambda: print('Encounters'))

        self.add(npyscreen.ButtonPress, name='Enemies',
                 when_pressed_function=lambda: print('Enemies'))

        self.add(npyscreen.ButtonPress, name='Spells',
                 when_pressed_function=lambda: print('Spells'))


class App(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainMenu)


def main():
    try:
        App().run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
