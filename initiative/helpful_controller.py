import npyscreen


class HelpfulController(npyscreen.ActionControllerSimple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_action(':h(elp)?', self.display_help, False)
        self.add_action(':.*', self.show_invalid, False)

    def display_help(self, command_line, widget_proxy, live):
        self.parent.set_status2_preserve_line(self.parent.COMMAND_TITLE)
        npyscreen.notify_confirm(self.help_message(), title='Help', wide=True)

    def help_message(self):
        return [str(a['identifier']) for a in self._action_list if a['identifier'] != ':.*']

    def show_invalid(self, command_line, widget_proxy, live):
        self.parent.set_temp_status2_preserve_line('Invalid Command')
