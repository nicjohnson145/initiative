import npyscreen


class StatDisplay(npyscreen.ActionFormMinimal):

    def create(self):
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
        })
        self.armor_class = self.add(npyscreen.TitleFixedText, name='Armor Class')
        self.hit_points = self.add(npyscreen.TitleFixedText, name='Hit Points')
        self.speed = self.add(npyscreen.TitleFixedText, name='Speed')
        self.stat_grid = self.add(npyscreen.GridColTitles, columns=6, values=[],
                                  col_titles=['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'],
                                  max_height=3)
        self.saving_throws = self.add(npyscreen.TitleFixedText, name='Saving Throws')

    def populate_form(self):
        self.name = self.value.name
        self.armor_class.value = self.value.armor_class
        self.hit_points.value = self.value.hit_points
        self.speed.value = self.value.speed
        self.stat_grid.values = [[
            self.value.strength,
            self.value.dexterity,
            self.value.constitution,
            self.value.intelligence,
            self.value.wisdom,
            self.value.charisma
        ]]
        self.saving_throws.value = self.value.saving_throws

    def beforeEditing(self):
        self.populate_form()

    def on_ok(self):
        self.parentApp.switchFormPrevious()


