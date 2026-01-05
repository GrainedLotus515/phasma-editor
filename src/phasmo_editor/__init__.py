"""
PhasmoEditor - Phasmophobia Save File Editor

A Python tool for editing Phasmophobia save files with a modern GUI.
Supports editing money, level, prestige, equipment unlocks, and more.

Original C# version by stth12/PhasmoEditor
Python port with GUI enhancements
"""

__version__ = "2.0.0"
__author__ = "stth12"

from .crypto import decrypt, decrypt_file, encrypt, encrypt_to_file
from .game_data import EQUIPMENT, PRESTIGE_TITLES, prestige_to_roman
from .save_parser import SaveData, SaveParser

__all__ = [
    "decrypt",
    "decrypt_file",
    "encrypt",
    "encrypt_to_file",
    "EQUIPMENT",
    "PRESTIGE_TITLES",
    "prestige_to_roman",
    "SaveData",
    "SaveParser",
]
