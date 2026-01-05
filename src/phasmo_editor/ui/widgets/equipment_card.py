"""
Equipment card widget for PhasmoEditor.

Displays an equipment item with tier selector and unlock checkboxes.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from ...game_data import EquipmentInfo
from ...theme import CATPPUCCIN_MOCHA


class EquipmentCard(QFrame):
    """
    A card widget displaying an equipment item with tier controls.
    """

    tier_changed = Signal(str, int)  # equipment_name, new_tier
    unlock_changed = Signal(str, int, bool)  # equipment_name, tier, unlocked

    def __init__(
        self,
        equipment: EquipmentInfo,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.equipment = equipment
        self._current_tier = 1
        self._unlocks = {1: False, 2: False, 3: False}
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        self.setObjectName("equipment_card")
        self.setStyleSheet("")
        # Keep a consistent card width so the grid forms more columns.
        self.setFixedWidth(220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Equipment name
        self._name_label = QLabel(self.equipment.display_name)
        self._name_label.setObjectName("equipment_card_title")
        self._name_label.setStyleSheet("")
        self._name_label.setWordWrap(True)
        layout.addWidget(self._name_label)

        # Category badge
        category_color = (
            CATPPUCCIN_MOCHA["mauve"]
            if self.equipment.category == "evidence"
            else CATPPUCCIN_MOCHA["teal"]
        )
        self._category_label = QLabel(self.equipment.category.capitalize())
        self._category_label.setObjectName(
            "chip_evidence" if self.equipment.category == "evidence" else "chip_utility"
        )
        self._category_label.setStyleSheet("")
        self._category_label.setFixedHeight(18)
        layout.addWidget(self._category_label, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addSpacing(4)

        # Tier selector
        tier_label = QLabel("Tier:")
        tier_label.setObjectName("field_label")
        tier_label.setStyleSheet("")
        layout.addWidget(tier_label)

        tier_row = QHBoxLayout()
        tier_row.setSpacing(4)

        self._tier_group = QButtonGroup(self)
        self._tier_buttons: dict[int, QRadioButton] = {}

        for tier in [1, 2, 3]:
            btn = QRadioButton(f"T{tier}")
            btn.setObjectName("tier_radio")
            btn.setStyleSheet("")
            self._tier_group.addButton(btn, tier)
            self._tier_buttons[tier] = btn
            tier_row.addWidget(btn)

        tier_row.addStretch()
        layout.addLayout(tier_row)

        # Tier unlocks
        unlock_label = QLabel("Unlocked:")
        unlock_label.setObjectName("field_label")
        unlock_label.setStyleSheet("")
        layout.addWidget(unlock_label)

        unlock_row = QHBoxLayout()
        unlock_row.setSpacing(8)

        self._unlock_checks: dict[int, QCheckBox] = {}

        for tier in [1, 2, 3]:
            cb = QCheckBox(f"T{tier}")
            cb.setObjectName("tier_unlock")
            cb.setStyleSheet("")
            cb.stateChanged.connect(
                lambda state, t=tier: self._on_unlock_changed(t, state)
            )
            self._unlock_checks[tier] = cb
            unlock_row.addWidget(cb)

        unlock_row.addStretch()
        layout.addLayout(unlock_row)

        layout.addStretch()

        # Connect tier selection
        self._tier_group.buttonClicked.connect(self._on_tier_clicked)

        # Set default tier
        self._tier_buttons[1].setChecked(True)

    def _on_tier_clicked(self, button: QRadioButton) -> None:
        """Handle tier radio button click."""
        tier = self._tier_group.id(button)
        if tier != self._current_tier:
            self._current_tier = tier
            self.tier_changed.emit(self.equipment.name, tier)

    def _on_unlock_changed(self, tier: int, state: int) -> None:
        """Handle unlock checkbox state change."""
        unlocked = state == Qt.CheckState.Checked.value
        self._unlocks[tier] = unlocked
        self.unlock_changed.emit(self.equipment.name, tier, unlocked)

    def set_tier(self, tier: int) -> None:
        """Set the current tier (1-3)."""
        if tier in self._tier_buttons:
            self._current_tier = tier
            self._tier_buttons[tier].setChecked(True)

    def get_tier(self) -> int:
        """Get the current tier."""
        return self._current_tier

    def set_unlock(self, tier: int, unlocked: bool) -> None:
        """Set whether a tier is unlocked."""
        if tier in self._unlock_checks:
            self._unlocks[tier] = unlocked
            self._unlock_checks[tier].blockSignals(True)
            self._unlock_checks[tier].setChecked(unlocked)
            self._unlock_checks[tier].blockSignals(False)

    def get_unlock(self, tier: int) -> bool:
        """Get whether a tier is unlocked."""
        return self._unlocks.get(tier, False)

    def set_all_unlocks(self, unlocks: dict[int, bool]) -> None:
        """Set all tier unlocks at once."""
        for tier, unlocked in unlocks.items():
            self.set_unlock(tier, unlocked)

    def unlock_all(self) -> None:
        """Unlock all tiers."""
        for tier in [1, 2, 3]:
            self.set_unlock(tier, True)
            self.unlock_changed.emit(self.equipment.name, tier, True)
