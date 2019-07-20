import npyscreen


class HelpfulController(npyscreen.ActionControllerSimple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_action(':h(elp)?', self.display_help, False)
        self.add_action(':.*', self.show_invalid, False)

    def display_help(self, _command_line, _widget_proxy, _live):
        self.parent.set_status2_preserve_line(self.parent.COMMAND_TITLE)
        npyscreen.notify_confirm(self.help_message(), title='Help', wide=True)

    def help_message(self):
        ret = []
        for action in self._action_list:
            ident = str(action['identifier'])
            if ident != "re.compile(':.*')":
                ret.append(ident)
        return ret

    def show_invalid(self, _command_line, _widget_proxy, _live):
        self.parent.set_temp_status2_preserve_line('Invalid Command')

    def process_command_live(self, command_line, control_widget_proxy):
        for action in self._action_list:
            if action['identifier'].match(command_line) and action['live'] is True:
                action['function'](command_line, control_widget_proxy, live=True)
                break

    def process_command_complete(self, command_line, control_widget_proxy):
        for action in self._action_list:
            if action['identifier'].match(command_line):
                action['function'](command_line, control_widget_proxy, live=False)
                break
