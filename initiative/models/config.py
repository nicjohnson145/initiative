import os
from pathlib import Path
import json

DEFAULT_ENCOUNTER_STORAGE = os.path.expanduser('~/.config/initiative/encounters')

EXTRA_NPCS_PATH = 'extra_npcs_path'
EXTRA_SPELLS_PATH = 'extra_spells_path'
ENCOUNTER_PATH = 'encounter_path'
AUTOSAVE_ENCOUNTERS = 'autosave_encounters'


class Config(object):

    def __init__(self):
        self.config_path = os.path.join(Path.home(), '.config/initiative.json')
        if os.path.isfile(self.config_path):
            with open(self.config_path) as fl:
                try:
                    self.config = json.load(fl)
                except json.JSONDecodeError:
                    self.config = {}
        else:
            self.config = {}
        os.makedirs(self.encounter_path, exist_ok=True)

    @property
    def encounter_path(self):
        return self.config.get(ENCOUNTER_PATH, DEFAULT_ENCOUNTER_STORAGE)

    @property
    def extra_npcs_path(self):
        return self.config.get(EXTRA_NPCS_PATH)

    @property
    def extra_spells_path(self):
        return self.config.get(EXTRA_SPELLS_PATH)

    @property
    def autosave_encounters(self):
        return self.config.get(AUTOSAVE_ENCOUNTERS, True)
