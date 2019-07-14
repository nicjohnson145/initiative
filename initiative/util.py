import random
import npyscreen


def rollD20():
    return random.randrange(1, 21)


def wrap_message(self, message, widget):
    width = widget.width - 5
    return npyscreen.utilNotify._wrap_message_lines(message, width)
