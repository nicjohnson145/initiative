import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)

CONFIG_ROOT = os.path.join(Path.home(), '.config/initiative')
CONFIG_FILE = os.path.join(CONFIG_ROOT, 'config.json')
DEFAULT_ENCOUNTER_STORAGE = os.path.join(CONFIG_ROOT, 'encounters')
DEFAULT_SPELL_STORAGE = os.path.join(CONFIG_ROOT, 'spells')
DEFAULT_NPC_STORAGE = os.path.join(CONFIG_ROOT, 'npcs')

EXTRA_NPCS_PATH = 'extra_npcs_path'
EXTRA_SPELLS_PATH = 'extra_spells_path'
ENCOUNTER_PATH = 'encounter_path'
AUTOSAVE_ENCOUNTERS = 'autosave_encounters'


class Config(object):

    def __init__(self):
        if os.path.isfile(CONFIG_FILE):
            with open(CONFIG_FILE) as fl:
                try:
                    self.config = json.load(fl)
                except json.JSONDecodeError as ex:
                    log.error(ex, exc_info=True)
                    self.config = {}
        else:
            self.config = {}

    def _ensure_path(self, attr, default):
        path = self.config.get(attr, default)
        os.makedirs(path, exist_ok=True)
        return path

    @property
    def encounter_path(self):
        return self._ensure_path(ENCOUNTER_PATH, DEFAULT_ENCOUNTER_STORAGE)

    @property
    def extra_npcs_path(self):
        return self._ensure_path(EXTRA_NPCS_PATH, DEFAULT_NPC_STORAGE)

    @property
    def extra_spells_path(self):
        return self._ensure_path(EXTRA_SPELLS_PATH, DEFAULT_SPELL_STORAGE)

    @property
    def autosave_encounters(self):
        return self.config.get(AUTOSAVE_ENCOUNTERS, False)
