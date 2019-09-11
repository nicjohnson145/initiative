import re

import npyscreen

from initiative.constants import ENCOUNTER_LIST, FILTERED_SELECT, SPELL, STAT_DISPLAY
from initiative.models.encounter import Member
from initiative.ui.custom_mutt import _CustomMutt
from initiative.ui.helpful_controller import HelpfulController
from initiative.util import add_to_encounter


class CombatLines(npyscreen.MultiLineAction):

    def display_value(self, member):
        return member.combat_display() if isinstance(member, Member) else str(member)

    def actionHighlighted(self, member, _keypress):
        if not member.is_player:
            self.parent.parentApp.getForm(STAT_DISPLAY).value = member.stat_block
            self.parent.parentApp.switchForm(STAT_DISPLAY)


class CombatController(HelpfulController):

    digit_re = re.compile(r':.* +(?P<amt>\d+)')
    players_re = re.compile(r':p(layers)? +(?P<player_string>.*)')
    piece_re = re.compile(r':p(iece)? (?P<piece_name>.*)')
    change_re = re.compile(r':c(hange)? (?P<attribute>\b.*\b) (?P<new_value>\b.*\b)')
    changeable_attrs = set(['initiative'])

    def create(self):
        self.add_action(':d(amage)', self.damage_member, False)
        self.add_action(':h(eal)', self.heal_member, False)
        self.add_action(':res(surect)?$', self.resurrect_member, False)
        self.add_action(':k(ill)?$', self.kill_member, False)
        self.add_action(':add$', self.add_member, False)
        self.add_action(':remove$', self.remove_member, False)
        self.add_action(':players?', self.add_players, False)
        self.add_action(':p(iece)?', self.set_piece_name, False)
        self.add_action(':use_spell', self.use_spell, False)
        self.add_action(':spells$', self.search_spells, False)
        self.add_action(':c(hange)?', self.change_attribute, False)
        self.add_action(':t(urn)?$', self.turn, False)
        self.add_action(':autosave$', self.toggle_autosave, False)
        self.add_action(':q(uit)?!?$', self.quit, False)

    def help_message(self):
        return self.help_table(
            ['d(amage) <int>', 'Damage the selected member'],
            ['h(eal) <int>', 'Heal the selected member'],
            ['res(surect)', 'TBD'],
            ['k(ill)', 'Kill the selected member and remove them from the encounter'],
            ['add', 'Add a member to the encounter'],
            ['remove', 'Remove selected member from encounter'],
            ['players <name>-<initiative>,....', 'Add players to encounter'],
            ['use_spell <int>', 'Indicate a used spell slot on the selected member'],
            ['spells', 'Search spells'],
            [
                'c(hange) <attr> <value>',
                ("Change an attribute about the selected memeber. Currently supported attributes "
                 "are " + ','.join(self.changeable_attrs))
            ],
            ['t(urn)', 'Incrememt the trun indicator'],
            ['q(uit)', 'Save and quit'],
            ['q(uit)!', 'Quit without saving'],
        )

    def action_performed(self):
        if self.parent.parentApp.config.autosave_encounters:
            self.parent.encounter.save()

    def damage_member(self, command_line, widget_proxy, live):
        self._health_interation('damage', command_line)
        self.action_performed()

    def heal_member(self, command_line, widget_proxy, live):
        self._health_interation('heal', command_line)
        self.action_performed()

    def _health_interation(self, attr, cmd_line):
        match = self.digit_re.search(cmd_line)
        if match:
            func = getattr(self.parent.selected, attr)
            func(int(match.group('amt')))
            self.parent.update()

    def resurrect_member(self, command_line, widget_proxy, live):
        pass

    def kill_member(self, command_line, widget_proxy, live):
        self.parent.selected.is_alive = False
        self.parent.update()
        self.action_performed()

    def add_member(self, command_line, widget_proxy, live):
        add_to_encounter(self.parent.parentApp, self.parent.encounter)
        self.action_performed()

    def remove_member(self, command_line, widget_proxy, live):
        self.parent.encounter.remove_member(self.parent.selected)
        self.parent.update()
        self.action_performed()

    def add_players(self, command_line, widget_proxy, live):
        match = self.players_re.search(command_line)
        if match:
            s = match.group('player_string')
            pairs = s.split(',')
            for pair in pairs:
                name, initiative = pair.split('-')
                player = Member.player(name, initiative)
                self.parent.encounter.add_member(player)
        self.parent.harsh_update()
        self.action_performed()

    def set_piece_name(self, command_line, widget_proxy, live):
        match = self.piece_re.search(command_line)
        if match:
            self.parent.selected.set_piece_name(match.group('piece_name'))
            self.parent.update()
            self.action_performed()

    def use_spell(self, command_line, widget_proxy, live):
        if not self.parent.selected.is_player:
            match = self.digit_re.search(command_line)
            if match:
                self.parent.selected.use_spell(int(match.group('amt')))
                self.parent.update()
            else:
                self.show_temp_message(msg='Invalid Args')
        self.action_performed()

    def search_spells(self, command_line, widget_proxy, live):
        self.parent.parentApp.getForm(FILTERED_SELECT).set_type(SPELL)
        self.parent.parentApp.switchForm(FILTERED_SELECT)

    def change_attribute(self, command_line, widget_proxy, live):
        match = self.change_re.search(command_line)
        if match:
            attr = match.group('attribute')
            new_value = match.group('new_value')

            if attr not in self.changeable_attrs:
                self.show_temp_message(msg=f"Cannot change attribute {attr}")

            if attr == 'initiative':
                try:
                    self.parent.selected.set_initiative(int(new_value))
                    self.parent.update()
                    self.action_performed()
                except ValueError as ex:
                    self.show_temp_message(msg=str(ex))

    def turn(self, command_line, widget_proxy, live):
        self.parent.encounter.advance_turn()
        self.parent.update()
        self.action_performed()

    def toggle_autosave(self, command_line, widget_proxy, live):
        pass

    def quit(self, command_line, widget_proxy, live):
        if '!' not in command_line:
            self.parent.encounter.save()
        self.parent.parentApp.switchForm(ENCOUNTER_LIST)


class CombatDisplay(_CustomMutt):

    ACTION_CONTROLLER = CombatController
    MAIN_WIDGET_CLASS = CombatLines

    def create(self):
        super().create()
        self.encounter = None

    def beforeEditing(self):
        self.wStatus1.value = '' if self.encounter is None else self.encounter.name
        self.wStatus2.value = "Command"
        self.encounter.indicate_turn()
        self.update()

    def harsh_update(self):
        self.wMain.values = []
        self.wMain.display()
        self.update()

    def update(self):
        self.wMain.values = self.encounter.alive
        self.wMain.update(clear=True)
