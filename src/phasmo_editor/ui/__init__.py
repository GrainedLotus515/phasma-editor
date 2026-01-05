"""
UI module for PhasmoEditor.

Provides the graphical user interface using PySide6.
"""

from .equipment_tab import EquipmentTab
from .general_tab import GeneralTab
from .main_window import MainWindow
from .settings_tab import SettingsTab
from .stats_tab import StatsTab

__all__ = [
    "MainWindow",
    "GeneralTab",
    "EquipmentTab",
    "StatsTab",
    "SettingsTab",
]
