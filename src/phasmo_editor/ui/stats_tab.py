"""
Stats tab for PhasmoEditor.

Provides viewing and editing of player statistics.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QGridLayout,
)

from ..game_data import (
    ALL_STATS,
    DICT_STATS,
    GHOST_TYPES,
    MAP_NAMES,
    StatInfo,
    format_stat_value,
)
from ..save_parser import SaveData
from ..theme import CATPPUCCIN_MOCHA
from .layout_constants import SECTION_SPACING
from .widgets import CollapsibleSection, StatRow


class EditModeToggle(QWidget):
    """A subtle toggle switch for edit mode."""

    toggled = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._enabled = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._label = QLabel("Edit Mode:")
        self._label.setStyleSheet(f"""
            color: {CATPPUCCIN_MOCHA["subtext0"]};
            font-size: 11px;
        """)
        layout.addWidget(self._label)

        self._toggle_btn = QPushButton("OFF")
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.setFixedSize(50, 24)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CATPPUCCIN_MOCHA["surface1"]};
                color: {CATPPUCCIN_MOCHA["subtext0"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface2"]};
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:checked {{
                background-color: {CATPPUCCIN_MOCHA["mauve"]};
                color: {CATPPUCCIN_MOCHA["base"]};
                border-color: {CATPPUCCIN_MOCHA["mauve"]};
            }}
        """)
        self._toggle_btn.clicked.connect(self._on_toggle)
        layout.addWidget(self._toggle_btn)

    @Slot()
    def _on_toggle(self) -> None:
        self._enabled = self._toggle_btn.isChecked()
        self._toggle_btn.setText("ON" if self._enabled else "OFF")
        self.toggled.emit(self._enabled)

    def is_enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._toggle_btn.setChecked(enabled)
        self._toggle_btn.setText("ON" if enabled else "OFF")


class GhostStatsTable(QWidget):
    """Table displaying ghost encounter and death statistics."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["Ghost Type", "Encounters", "Deaths"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        self._table.setColumnWidth(1, 100)
        self._table.setColumnWidth(2, 100)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
                gridline-color: {CATPPUCCIN_MOCHA["surface1"]};
            }}
            QTableWidget::item {{
                padding: 4px;
            }}
            QTableWidget::item:alternate {{
                background-color: {CATPPUCCIN_MOCHA["mantle"]};
            }}
            QHeaderView::section {{
                background-color: {CATPPUCCIN_MOCHA["surface1"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                padding: 6px;
                border: none;
                font-weight: bold;
            }}
        """)
        # Allow the table to expand; constraining height makes it look like
        # only one row exists on some layouts.
        self._table.setMinimumHeight(320)
        layout.addWidget(self._table)

    def load_data(self, encounters: dict[str, int], deaths: dict[str, int]) -> None:
        """Load ghost statistics into the table."""
        # Get all unique ghost types
        all_ghosts = set(GHOST_TYPES) | set(encounters.keys()) | set(deaths.keys())
        # Sort by encounters desc, then deaths desc, then name
        all_ghosts = sorted(
            all_ghosts,
            key=lambda g: (
                -(encounters.get(g, 0)),
                -(deaths.get(g, 0)),
                g,
            ),
        )

        self._table.setRowCount(len(all_ghosts))

        for row, ghost in enumerate(all_ghosts):
            # Ghost name
            name_item = QTableWidgetItem(ghost)
            self._table.setItem(row, 0, name_item)

            # Encounters
            enc_count = encounters.get(ghost, 0)
            enc_item = QTableWidgetItem(str(enc_count))
            enc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 1, enc_item)

            # Deaths
            death_count = deaths.get(ghost, 0)
            death_item = QTableWidgetItem(str(death_count))
            death_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if death_count > 0:
                death_item.setForeground(Qt.GlobalColor.red)
            self._table.setItem(row, 2, death_item)


class StatsTab(QWidget):
    """Statistics viewing/editing tab."""

    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._save_data: Optional[SaveData] = None
        self._stat_rows: dict[str, StatRow] = {}
        self._edit_mode = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with edit toggle
        header = QHBoxLayout()
        header.addStretch()

        self._edit_toggle = EditModeToggle()
        self._edit_toggle.toggled.connect(self._on_edit_mode_toggled)
        header.addWidget(self._edit_toggle)

        header_widget = QWidget()
        header_widget.setLayout(header)
        layout.addWidget(header_widget)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background-color: transparent; }"
            "QScrollArea::viewport { background-color: transparent; }"
        )

        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 8, 0, 8)
        content_layout.setSpacing(SECTION_SPACING)

        self._sections_container = QWidget()
        self._grid = QGridLayout(self._sections_container)
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(SECTION_SPACING)
        self._grid.setVerticalSpacing(SECTION_SPACING)
        content_layout.addWidget(self._sections_container)

        # Create sections for each stat category
        self._sections: list[CollapsibleSection] = []
        for category_name, stats in ALL_STATS.items():
            section = self._create_stat_section(category_name, stats)
            self._sections.append(section)

        # Ghost encounters section (always full-width row)
        self._ghost_section = CollapsibleSection("Ghost Encounters", expanded=False)
        self._ghost_table = GhostStatsTable()
        self._ghost_section.add_widget(self._ghost_table)

        self._reflow_sections(columns=3)

        # Reset button at bottom
        reset_row = QHBoxLayout()
        reset_row.addStretch()

        self._reset_btn = QPushButton("Reset All Stats")
        self._reset_btn.setObjectName("danger_button")
        self._reset_btn.clicked.connect(self._on_reset_clicked)
        reset_row.addWidget(self._reset_btn)

        reset_widget = QWidget()
        reset_widget.setLayout(reset_row)
        content_layout.addWidget(reset_widget)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # 3 columns on wide displays, 2 medium, 1 narrow
        width = self.width()
        if width < 1100:
            cols = 1
        elif width < 1600:
            cols = 2
        else:
            cols = 3
        self._reflow_sections(cols)

    def _reflow_sections(self, columns: int) -> None:
        # Clear grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        # Place stat sections
        col = 0
        row = 0
        for section in self._sections:
            self._grid.addWidget(section, row, col)
            col += 1
            if col >= max(1, columns):
                col = 0
                row += 1

        # Add ghost table as full-width row
        row += 1
        self._grid.addWidget(self._ghost_section, row, 0, 1, max(1, columns))

        # Stretch
        for c in range(max(1, columns)):
            self._grid.setColumnStretch(c, 1)
        self._grid.setRowStretch(row + 1, 1)

    def _create_stat_section(
        self, title: str, stats: list[StatInfo]
    ) -> CollapsibleSection:
        """Create a collapsible section for a category of stats."""
        section = CollapsibleSection(title, expanded=True)

        for stat in stats:
            row = StatRow(stat)
            row.value_changed.connect(self._on_stat_value_changed)
            self._stat_rows[stat.field] = row
            section.add_widget(row)

        return section

    @Slot(bool)
    def _on_edit_mode_toggled(self, enabled: bool) -> None:
        """Handle edit mode toggle."""
        self._edit_mode = enabled
        for row in self._stat_rows.values():
            row.set_edit_mode(enabled)

    @Slot(str, object)
    def _on_stat_value_changed(self, field: str, value) -> None:
        """Handle stat value change."""
        if self._save_data:
            # Determine type hint based on value type
            if isinstance(value, float):
                self._save_data.set_value(field, value, "float")
            else:
                self._save_data.set_value(field, value, "int")
            self.data_changed.emit()

    @Slot()
    def _on_reset_clicked(self) -> None:
        """Handle reset all stats button."""
        if self._save_data is None:
            return

        # Confirmation dialog
        result = QMessageBox.warning(
            self,
            "Reset All Stats",
            "Are you sure you want to reset all statistics to zero?\n\n"
            "A backup will be created before resetting.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        # Reset stats
        self._save_data.reset_all_stats()

        # Reload UI
        self.load_data(self._save_data)
        self.data_changed.emit()

        QMessageBox.information(
            self,
            "Stats Reset",
            "All statistics have been reset to zero.",
        )

    def load_data(self, save_data: SaveData) -> None:
        """Load save data into the UI."""
        self._save_data = save_data

        # Load simple stats
        for field, row in self._stat_rows.items():
            stat_info = row.stat_info
            if stat_info.format_type in ("int", "money"):
                value = save_data.get_int(field, 0)
            else:
                value = save_data.get_float(field, 0.0)
            row.set_value(value)

        # Load ghost stats
        encounters = save_data.get_dict_stat("mostCommonGhosts")
        deaths = save_data.get_dict_stat("ghostKills")
        self._ghost_table.load_data(encounters, deaths)

    def apply_changes(self, save_data: SaveData) -> None:
        """Apply UI changes back to save data."""
        # Changes are applied immediately via signals
        pass
