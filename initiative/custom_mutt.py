import curses
import logging
import npyscreen
from datetime import datetime, timedelta

STATUS_1 = 'status1'
STATUS_2 = 'status2'
STATUS_LINES = [
    STATUS_1,
    STATUS_2,
]

log = logging.getLogger(__name__)


class _CustomMutt(npyscreen.FormMuttActiveTraditional):

    COMMAND_TITLE = 'Command'
    TEMP_DISPLAY_DURATION = timedelta(seconds=1.5)
    KEYPRESS_TIMEOUT = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_time = None
        self.displaying_invalid = False
        self.keypress_timeout = 1

    def set_status1_preserve_line(self, value):
        self.__set_status_preserve_line(self.wStatus1, value)

    def set_status2_preserve_line(self, value):
        self.__set_status_preserve_line(self.wStatus2, value)
        self.__reset_invalid()

    def __set_status_preserve_line(self, attr, value):
        status = getattr(self, attr) if isinstance(attr, str) else attr
        status.value = value
        status.update()
        line_start = len(value) + 1
        line_end = self.columns - line_start - 1
        self.curses_pad.hline(status.rely, line_start, curses.ACS_HLINE, line_end)

    def set_temp_status2_preserve_line(self, value):
        self.__set_temp_status_preserve_line(self.wStatus2, value)

    def __set_temp_status_preserve_line(self, attr, value):
        self.__set_status_preserve_line(attr, value)
        self.reset_time = datetime.now() + self.TEMP_DISPLAY_DURATION
        self.displaying_invalid = True

    def while_waiting(self):
        if self.displaying_invalid:
            if datetime.now() >= self.reset_time:
                self.set_status2_preserve_line(self.COMMAND_TITLE)
                self.__reset_invalid()

    def __reset_invalid(self):
        self.reset_time = None
        self.displaying_invalid = False

