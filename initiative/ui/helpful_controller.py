import npyscreen
from textwrap import wrap
from prettytable import PrettyTable, ALL


class HelpfulController(npyscreen.ActionControllerSimple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_action(':h(elp)?', self.display_help, False)
        self.add_action(':.*', self.invalid_command, False)
        self.help_width = 60

    def display_help(self, command_line, widget_proxy, live):
        self.parent.set_status2_preserve_line(self.parent.COMMAND_TITLE)
        npyscreen.notify_confirm(self.help_message(), title='Help', wide=True)

    def help_message(self):
        ret = []
        for action in self._action_list:
            ident = str(action['identifier'])
            if ident != "re.compile(':.*')":
                ret.append(ident)
        return ret

    def help_table(self, *rows):
        t = PrettyTable()
        t.hrules = ALL
        t.align = 'l'
        t.field_names = ['Command', 'Description']
        for row in rows:
            t.add_row([
                row[0],
                '\n'.join(wrap(row[1], width=self.help_width))
            ])
        return t.get_string()

    def invalid_command(self, command_line, widget_proxy, live):
        self.show_temp_message()

    def show_temp_message(self, msg='Invalid Command'):
        self.parent.set_temp_status2_preserve_line(msg)

    def process_command_live(self, command_line, control_widget_proxy):
        for action in self._action_list:
            if action['identifier'].match(command_line) and action['live'] is True:
                action['function'](command_line, control_widget_proxy, live=True)
                self.action_performed()
                break

    def process_command_complete(self, command_line, control_widget_proxy):
        for action in self._action_list:
            if action['identifier'].match(command_line):
                action['function'](command_line, control_widget_proxy, live=False)
                self.action_performed()
                break

    def action_performed(self):
        pass
