import npyscreen

from initiative.ui.spell_display.pager_box import PagerBox


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
        simple_attrs = [
            'level',
            'casting_time',
            'range',
            'components',
            'duration',
            'concentration',
        ]
        for attr in simple_attrs:
            label = attr.title()
            label = attr.replace('_', ' ')
            val = getattr(self.value, attr)
            self.add(npyscreen.TitleFixedText, name=label, value=val)

        self.add(
            PagerBox,
            name='Description',
            contained_widget_arguments={
                'values': self.value.description,
                'scroll_exit': True
            },
            max_height=6
        )

        if len(self.value.higher_levels) > 0:
            self.add(
                PagerBox,
                name='At Higher Levels',
                contained_widget_arguments={
                    'values': self.value.higher_levels,
                    'scroll_exit': True
                },
                max_height=6
            )
