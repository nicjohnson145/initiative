import curses

import npyscreen

from initiative.ui.stat_display.grid_box import GridBox

BUTTON_COLUMNS = 4
BOX_HEIGHT = 5
ENTRY_HEIGHT = BOX_HEIGHT - 2


class StatDisplay(npyscreen.ActionFormMinimal):

    def create(self):
        self.add_handlers({
            'q': lambda *args: self.parentApp.switchFormPrevious(),
        })

    def populate_form(self):
        self._clear_all_widgets()

        self.name = self.value.name
        self.add(npyscreen.TitleFixedText, name='Armor Class', value=self.value.armor_class)
        self.add(npyscreen.TitleFixedText, name='Hit Points', value=self.value.hit_points)
        self.add(npyscreen.TitleFixedText, name='Speed', value=self.value.speed)

        self.nextrely += 1
        stat_grid_values = [[
            self.value.strength,
            self.value.dexterity,
            self.value.constitution,
            self.value.intelligence,
            self.value.wisdom,
            self.value.charisma
        ]]
        self.add(npyscreen.GridColTitles, columns=6, values=stat_grid_values, max_height=3,
                 col_titles=['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA'])
        self.nextrely += 1

        self.conditional_single_line_display('saving_throws', 'Saving Throws')
        self.conditional_single_line_display('damage_vulnerabilities', 'Damage Vulnerabilities')
        self.conditional_single_line_display('damage_resistances', 'Damage Resistances')
        self.conditional_single_line_display('damage_immunities', 'Damage Immunities')
        self.conditional_single_line_display('condition_immunities', 'Condition Immunities')
        self.conditional_single_line_display('senses', 'Senses')
        self.conditional_single_line_display('languages', 'Languages')

        if len(self.value.abilities) > 0:
            self._create_grid_box('Abilities', 'abilities', self.display_ability)

        self._create_grid_box('Actions', 'actions', self.display_action)

        if len(self.value.legendary_actions) > 0:
            self._create_grid_box('Legendary Actions', 'legendary_actions', self.display_ability)

    def _create_grid_box(self, name, attribute, handler):
        box = self.add(GridBox, name=name, max_height=BOX_HEIGHT)
        entry = box.entry_widget
        entry.columns = BUTTON_COLUMNS
        entry.max_height = ENTRY_HEIGHT
        entry.set_grid_values_from_flat_list(getattr(self.value, attribute))
        entry.add_handlers({
            curses.ascii.NL: handler
        })

    def display_ability(self, *args):
        self._display_popup('abilities')

    def display_action(self, *args):
        self._display_popup('actions')

    def _display_popup(self, attr):
        widget = getattr(self, attr)
        row, column = widget.edit_cell
        msg = widget.values[row][column].as_popup()
        npyscreen.notify_confirm(msg, wide=True)

    def conditional_single_line_display(self, attr, title):
        longKwargs = {
            'begin_entry_at': 23,
            'use_two_lines': False
        }
        if len(getattr(self.value, attr)) > 0:
            self.add(
                npyscreen.TitleFixedText,
                name=title,
                value=getattr(self.value, attr),
                **longKwargs
            )

    def beforeEditing(self):
        self.populate_form()

    def on_ok(self):
        self.parentApp.switchFormPrevious()

