import curses

import npyscreen


class _CustomMutt(npyscreen.FormMuttActiveTraditional):

    def set_status1_preserve_line(self, value):
        self.set_status_preserve_line(self.wStatus1, value)

    def set_status2_preserve_line(self, value):
        self.set_status_preserve_line(self.wStatus2, value)

    def set_status_preserve_line(self, attr, value):
        status = getattr(self, attr) if isinstance(attr, str) else attr
        status.value = value
        status.update()
        line_start = len(value) + 1
        line_end = self.columns - line_start - 1
        self.curses_pad.hline(status.rely, line_start, curses.ACS_HLINE, line_end)
