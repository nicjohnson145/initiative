import random
import string

import npyscreen


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
