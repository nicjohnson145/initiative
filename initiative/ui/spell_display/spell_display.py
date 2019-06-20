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

        desc = self.add(
            PagerBox,
            name='Description',
            contained_widget_arguments={
                'scroll_exit': True,
            },
            max_height=8
        )

        msg = self.wrap_message(self.value.description, desc)
        desc.entry_widget.values = msg

        if len(self.value.higher_levels) > 0:
            levels = self.add(
                PagerBox,
                name='At Higher Levels',
                contained_widget_arguments={
                    'scroll_exit': True,
                },
                max_height=8
            )
            msg = self.wrap_message(self.value.higher_levels, levels)
            levels.entry_widget.values = msg

    def wrap_message(self, message, widget):
        width = widget.width - 5
        return npyscreen.utilNotify._wrap_message_lines(message, width)
