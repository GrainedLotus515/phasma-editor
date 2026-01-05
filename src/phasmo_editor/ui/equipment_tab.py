"""
Equipment tab for PhasmoEditor.

Provides editing for equipment tiers, unlocks, and loadouts.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..game_data import (
    EQUIPMENT,
    NUM_LOADOUTS,
    EquipmentInfo,
    get_equipment_by_category,
)
from ..save_parser import SaveData
from ..theme import CATPPUCCIN_MOCHA
from .layout_constants import PAGE_MARGIN, ROW_SPACING, SECTION_SPACING
from .widgets import CollapsibleSection, EquipmentCard, FlowLayout


class LoadoutItemRow(QWidget):
    """A row for editing a single equipment item in a loadout."""

    value_changed = Signal()

    def __init__(
        self,
        equipment: EquipmentInfo,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.equipment = equipment
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(12)

        # Name
        name_label = QLabel(self.equipment.display_name)
        name_label.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['text']}; font-size: 12px;")
        name_label.setMinimumWidth(140)
        layout.addWidget(name_label)

        # Quantity
        qty_label = QLabel("Qty:")
        qty_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 11px;"
        )
        layout.addWidget(qty_label)

        self._qty_spin = QSpinBox()
        self._qty_spin.setRange(0, 10)
        self._qty_spin.setFixedWidth(60)
        self._qty_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
                padding: 2px;
            }}
        """)
        self._qty_spin.valueChanged.connect(lambda: self.value_changed.emit())
        layout.addWidget(self._qty_spin)

        # Tier
        tier_label = QLabel("Tier:")
        tier_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 11px;"
        )
        layout.addWidget(tier_label)

        self._tier_combo = QComboBox()
        self._tier_combo.addItems(["T1", "T2", "T3"])
        self._tier_combo.setFixedWidth(60)
        self._tier_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
                padding: 2px 4px;
            }}
        """)
        self._tier_combo.currentIndexChanged.connect(lambda: self.value_changed.emit())
        layout.addWidget(self._tier_combo)

        layout.addStretch()

    def get_quantity(self) -> int:
        return self._qty_spin.value()

    def set_quantity(self, qty: int) -> None:
        self._qty_spin.blockSignals(True)
        self._qty_spin.setValue(qty)
        self._qty_spin.blockSignals(False)

    def get_tier(self) -> int:
        return self._tier_combo.currentIndex() + 1

    def set_tier(self, tier: int) -> None:
        self._tier_combo.blockSignals(True)
        self._tier_combo.setCurrentIndex(max(0, tier - 1))
        self._tier_combo.blockSignals(False)


class RenameLoadoutDialog(QDialog):
    """Dialog for renaming a loadout."""

    def __init__(self, current_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Rename Loadout")
        self.setModal(True)
        self.setMinimumWidth(300)

        layout = QVBoxLayout(self)

        # Name input
        form = QFormLayout()
        self._name_edit = QLineEdit(current_name)
        self._name_edit.setMaxLength(50)
        form.addRow("Name:", self._name_edit)
        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_name(self) -> str:
        return self._name_edit.text().strip()


class LoadoutEditor(CollapsibleSection):
    """Editor for loadout configurations."""

    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Loadouts", expanded=False, parent=parent)
        self._current_loadout = -1
        self._item_rows: dict[str, LoadoutItemRow] = {}
        self._save_data: Optional[SaveData] = None
        self._setup_content()

    def _setup_content(self) -> None:
        # Loadout selector row
        selector_row = QHBoxLayout()

        selector_label = QLabel("Loadout:")
        selector_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['text']}; font-size: 13px;"
        )
        selector_row.addWidget(selector_label)

        self._loadout_combo = QComboBox()
        self._loadout_combo.setMinimumWidth(150)
        # -1 is the in-game "All" (committed) loadout
        self._loadout_combo.addItem("All", -1)
        for i in range(NUM_LOADOUTS):
            self._loadout_combo.addItem(f"Loadout {i + 1}", i)
        self._loadout_combo.currentIndexChanged.connect(self._on_loadout_selected)
        selector_row.addWidget(self._loadout_combo)

        self._rename_btn = QPushButton("Rename...")
        self._rename_btn.setObjectName("secondary_button")
        self._rename_btn.clicked.connect(self._on_rename_clicked)
        selector_row.addWidget(self._rename_btn)

        selector_row.addStretch()

        self._show_nonzero_cb = QPushButton("Show non-zero only")
        self._show_nonzero_cb.setCheckable(True)
        self._show_nonzero_cb.setObjectName("secondary_button")
        self._show_nonzero_cb.setChecked(True)
        self._show_nonzero_cb.clicked.connect(self._apply_visibility_filter)
        selector_row.addWidget(self._show_nonzero_cb)

        selector_widget = QWidget()
        selector_widget.setLayout(selector_row)
        self.add_widget(selector_widget)

        # Scrollable equipment list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(300)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        scroll_content = QWidget()
        self._items_layout = QVBoxLayout(scroll_content)
        self._items_layout.setContentsMargins(0, 0, 0, 0)
        self._items_layout.setSpacing(4)

        # Create rows for all equipment
        for name, equipment in EQUIPMENT.items():
            row = LoadoutItemRow(equipment)
            row.value_changed.connect(self._on_item_changed)
            self._item_rows[name] = row
            self._items_layout.addWidget(row)

        self._items_layout.addStretch()
        scroll.setWidget(scroll_content)
        self.add_widget(scroll)

    @Slot(int)
    def _on_loadout_selected(self, index: int) -> None:
        self._current_loadout = self._loadout_combo.itemData(index)
        self._load_loadout_data()
        self._apply_visibility_filter()

    @Slot()
    def _on_rename_clicked(self) -> None:
        if self._save_data is None:
            return

        if self._current_loadout == -1:
            QMessageBox.information(
                self,
                "Rename Loadout",
                "The 'All' loadout cannot be renamed.",
            )
            return

        current_name = self._save_data.get_loadout_name(self._current_loadout)
        dialog = RenameLoadoutDialog(current_name, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_name()
            if new_name:
                self._save_data.set_loadout_name(self._current_loadout, new_name)
                # Update current item text (index-based, not data-based)
                self._loadout_combo.setItemText(
                    self._loadout_combo.currentIndex(), new_name
                )
                self.data_changed.emit()

    @Slot()
    def _on_item_changed(self) -> None:
        self.data_changed.emit()
        self._apply_visibility_filter()

    def _load_loadout_data(self) -> None:
        if self._save_data is None:
            return

        for name, row in self._item_rows.items():
            qty = self._save_data.get_loadout_equipment_amount(
                self._current_loadout, name
            )
            tier = self._save_data.get_loadout_equipment_tier(
                self._current_loadout, name
            )
            row.set_quantity(qty)
            row.set_tier(tier if tier > 0 else 1)

    def _apply_visibility_filter(self) -> None:
        """Apply non-zero filter to loadout item rows."""
        if self._save_data is None:
            return

        show_nonzero_only = getattr(self, "_show_nonzero_cb", None)
        show_nonzero_only = show_nonzero_only.isChecked() if show_nonzero_only else True

        # In "All" mode, most items are non-zero; avoid hiding too much.

        for name, row in self._item_rows.items():
            if not show_nonzero_only:
                row.setVisible(True)
                continue

            qty = self._save_data.get_loadout_equipment_amount(
                self._current_loadout, name
            )
            row.setVisible(qty > 0)

    def load_data(self, save_data: SaveData) -> None:
        self._save_data = save_data

        # Update loadout names in combo
        # Index 0 is "All" and is not renameable.
        for i in range(NUM_LOADOUTS):
            name = save_data.get_loadout_name(i)
            self._loadout_combo.setItemText(i + 1, name)

        self._load_loadout_data()
        self._apply_visibility_filter()

    def apply_changes(self, save_data: SaveData) -> None:
        # Apply current loadout changes
        for name, row in self._item_rows.items():
            save_data.set_loadout_equipment_amount(
                self._current_loadout, name, row.get_quantity()
            )
            save_data.set_loadout_equipment_tier(
                self._current_loadout, name, row.get_tier()
            )


class EquipmentTab(QWidget):
    """Equipment editing tab."""

    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._cards: dict[str, EquipmentCard] = {}
        self._save_data: Optional[SaveData] = None
        self._current_filter = "all"
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SECTION_SPACING)

        # Toolbar
        toolbar = QHBoxLayout()

        # Filter buttons
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['text']};")
        toolbar.addWidget(filter_label)

        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["All", "Evidence", "Utility"])
        self._filter_combo.currentTextChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self._filter_combo)

        toolbar.addStretch()

        # Action buttons
        self._unlock_all_btn = QPushButton("Unlock All Tiers")
        self._unlock_all_btn.setObjectName("secondary_button")
        self._unlock_all_btn.clicked.connect(self._on_unlock_all)
        toolbar.addWidget(self._unlock_all_btn)

        toolbar_widget = QWidget()
        toolbar_widget.setLayout(toolbar)
        layout.addWidget(toolbar_widget)

        # Equipment grid (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
            "QScrollArea::viewport { background-color: transparent; }"
        )

        self._grid_container = QWidget()
        self._grid_layout = FlowLayout(
            self._grid_container,
            margin=0,
            h_spacing=SECTION_SPACING,
            v_spacing=SECTION_SPACING,
        )
        self._grid_container.setLayout(self._grid_layout)

        # Create equipment cards
        self._create_cards()

        scroll.setWidget(self._grid_container)
        layout.addWidget(scroll)

        # Loadout editor
        self._loadout_editor = LoadoutEditor()
        self._loadout_editor.data_changed.connect(self._on_data_changed)
        layout.addWidget(self._loadout_editor)

    def _create_cards(self) -> None:
        """Create equipment cards and add to flow layout."""
        for name, equipment in EQUIPMENT.items():
            card = EquipmentCard(equipment)
            card.tier_changed.connect(self._on_tier_changed)
            card.unlock_changed.connect(self._on_unlock_changed)
            self._cards[name] = card
            self._grid_layout.addWidget(card)

    def _apply_filter(self) -> None:
        """Apply the current category filter."""
        filter_lower = self._current_filter.lower()

        for name, card in self._cards.items():
            equipment = EQUIPMENT[name]
            if filter_lower == "all":
                card.setVisible(True)
            else:
                card.setVisible(equipment.category == filter_lower)

    @Slot(str)
    def _on_filter_changed(self, text: str) -> None:
        self._current_filter = text.lower()
        self._apply_filter()

    @Slot(str, int)
    def _on_tier_changed(self, equipment_name: str, tier: int) -> None:
        if self._save_data:
            self._save_data.set_equipment_tier(equipment_name, tier)
            self.data_changed.emit()

    @Slot(str, int, bool)
    def _on_unlock_changed(
        self, equipment_name: str, tier: int, unlocked: bool
    ) -> None:
        if self._save_data:
            self._save_data.set_tier_unlocked(equipment_name, tier, unlocked)
            self.data_changed.emit()

    @Slot()
    def _on_unlock_all(self) -> None:
        """Unlock all tiers for all equipment."""
        if self._save_data is None:
            return

        for name, card in self._cards.items():
            card.unlock_all()
            self._save_data.unlock_all_tiers(name)

        self.data_changed.emit()

    @Slot()
    def _on_data_changed(self) -> None:
        self.data_changed.emit()

    def load_data(self, save_data: SaveData) -> None:
        """Load save data into the UI."""
        self._save_data = save_data

        # Load equipment tiers and unlocks
        for name, card in self._cards.items():
            tier = save_data.get_equipment_tier(name)
            card.set_tier(tier)

            unlocks = {t: save_data.get_tier_unlocked(name, t) for t in [1, 2, 3]}
            card.set_all_unlocks(unlocks)

        # Load loadout data
        self._loadout_editor.load_data(save_data)

    def apply_changes(self, save_data: SaveData) -> None:
        """Apply UI changes back to save data."""
        # Equipment changes are applied immediately via signals
        # Just need to apply loadout changes
        self._loadout_editor.apply_changes(save_data)
