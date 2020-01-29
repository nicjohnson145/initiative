import random
import string

import npyscreen

from initiative.constants import ENCOUNTER_ADDITION, FILTERED_SELECT


def roll_d20():
    return random.randrange(1, 21)


def wrap_message(message, widget):
    width = widget.width - 5
    return npyscreen.utilNotify._wrap_message_lines(message, width)  # pylint: disable=W0212


def make_string_file_safe(s):
    def safe_char(c):
        if c.isalnum() or c in ('-', '_', '.'):
            return c
        elif c in string.whitespace:
            return '_'
        else:
            return ''

    return ''.join(safe_char(c) for c in s)


def add_to_encounter(parentApp, encounter):
    form = parentApp.getForm(FILTERED_SELECT)
    form.set_type(ENCOUNTER_ADDITION)
    form.encounter = encounter
    parentApp.switchForm(FILTERED_SELECT)

