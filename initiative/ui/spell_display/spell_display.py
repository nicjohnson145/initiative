import npyscreen


class SpellDisplay(npyscreen.ActionFormMinimal):

    def create(self):
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
        })

    def beforeEditing(self):
        self.populate_form()

    def populate_form(self):
        self._clear_all_widgets()

        self.name = self.value.name
