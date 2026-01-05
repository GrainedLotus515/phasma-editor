"""
General tab for PhasmoEditor.

Provides editing for Money, Level, Experience, and Prestige.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QGridLayout,
)

from ..game_data import (
    MAX_LEVEL,
    MAX_PRESTIGE,
    PRESTIGE_TITLES,
    format_level_display,
    get_experience_for_level,
    get_level_for_experience,
    prestige_to_roman,
)
from ..save_parser import SaveData
from ..theme import CATPPUCCIN_MOCHA
from .layout_constants import SECTION_SPACING


class SectionCard(QFrame):
    """A card-style container for a section of controls."""

    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("card")
        self._setup_ui(title)

    def _setup_ui(self, title: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title_label = QLabel(title)
        title_label.setObjectName("section_title")
        layout.addWidget(title_label)

        # Content container
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        layout.addWidget(self.content)

    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the card content."""
        self.content_layout.addWidget(widget)


class MoneySection(SectionCard):
    """Money editing section."""

    value_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Money", parent)
        self._setup_controls()

    def _setup_controls(self) -> None:
        # Money input
        input_row = QHBoxLayout()

        self.money_spin = QSpinBox()
        self.money_spin.setRange(0, 999_999_999)
        self.money_spin.setSingleStep(1000)
        self.money_spin.setPrefix("$")
        self.money_spin.valueChanged.connect(self._on_value_changed)
        input_row.addWidget(self.money_spin)

        # Quick presets
        preset_label = QLabel("Quick:")
        preset_label.setObjectName("description")
        input_row.addWidget(preset_label)

        presets = [("$10K", 10_000), ("$100K", 100_000), ("$1M", 1_000_000)]
        for label, value in presets:
            btn = QLabel(
                f'<a href="{value}" style="color: {CATPPUCCIN_MOCHA["mauve"]}">{label}</a>'
            )
            btn.setOpenExternalLinks(False)
            btn.linkActivated.connect(self._on_preset_clicked)
            input_row.addWidget(btn)

        input_row.addStretch()

        widget = QWidget()
        widget.setLayout(input_row)
        self.add_widget(widget)

    @Slot(str)
    def _on_preset_clicked(self, value: str) -> None:
        self.money_spin.setValue(int(value))

    @Slot()
    def _on_value_changed(self) -> None:
        self.value_changed.emit()

    def get_value(self) -> int:
        return self.money_spin.value()

    def set_value(self, value: int) -> None:
        self.money_spin.blockSignals(True)
        self.money_spin.setValue(value)
        self.money_spin.blockSignals(False)


class LevelSection(SectionCard):
    """Level and Experience editing section."""

    value_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Level & Experience", parent)
        self._setup_controls()

    def _setup_controls(self) -> None:
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        # Level input
        level_row = QHBoxLayout()
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, MAX_LEVEL)
        self.level_spin.valueChanged.connect(self._on_level_changed)
        level_row.addWidget(self.level_spin)

        self.level_display = QLabel()
        self.level_display.setObjectName("value_display")
        level_row.addWidget(self.level_display)
        level_row.addStretch()

        level_widget = QWidget()
        level_widget.setLayout(level_row)
        form.addRow("Level:", level_widget)

        # Experience input
        xp_row = QHBoxLayout()
        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 999_999_999)
        self.xp_spin.setSingleStep(100)
        self.xp_spin.valueChanged.connect(self._on_xp_changed)
        xp_row.addWidget(self.xp_spin)

        self.xp_label = QLabel()
        self.xp_label.setObjectName("description")
        xp_row.addWidget(self.xp_label)
        xp_row.addStretch()

        xp_widget = QWidget()
        xp_widget.setLayout(xp_row)
        form.addRow("Experience:", xp_widget)

        # Sync info
        sync_label = QLabel(
            "Tip: The game uses Experience to calculate level. "
            "Changing level will auto-calculate the required XP."
        )
        sync_label.setObjectName("description")
        sync_label.setWordWrap(True)
        form.addRow("", sync_label)

        form_widget = QWidget()
        form_widget.setLayout(form)
        self.add_widget(form_widget)

        # Store prestige for display formatting
        self._prestige = 0

    def set_prestige(self, prestige: int) -> None:
        """Set prestige for level display formatting."""
        self._prestige = prestige
        self._update_display()

    @Slot()
    def _on_level_changed(self) -> None:
        # Auto-calculate XP for level
        level = self.level_spin.value()
        xp = get_experience_for_level(level)

        self.xp_spin.blockSignals(True)
        self.xp_spin.setValue(xp)
        self.xp_spin.blockSignals(False)

        self._update_display()
        self.value_changed.emit()

    @Slot()
    def _on_xp_changed(self) -> None:
        # Auto-calculate level from XP
        xp = self.xp_spin.value()
        level = get_level_for_experience(xp)

        self.level_spin.blockSignals(True)
        self.level_spin.setValue(level)
        self.level_spin.blockSignals(False)

        self._update_display()
        self.value_changed.emit()

    def _update_display(self) -> None:
        level = self.level_spin.value()
        xp = self.xp_spin.value()

        # Update level display with prestige format
        self.level_display.setText(format_level_display(level, self._prestige))

        # Show XP needed for next level
        next_level_xp = get_experience_for_level(level + 1)
        xp_to_next = next_level_xp - xp
        if xp_to_next > 0:
            self.xp_label.setText(f"({xp_to_next:,} XP to level {level + 1})")
        else:
            self.xp_label.setText("(Max effective)")

    def get_level(self) -> int:
        return self.level_spin.value()

    def get_experience(self) -> int:
        return self.xp_spin.value()

    def set_values(self, level: int, experience: int) -> None:
        self.level_spin.blockSignals(True)
        self.xp_spin.blockSignals(True)

        self.level_spin.setValue(level)
        self.xp_spin.setValue(experience)

        self.level_spin.blockSignals(False)
        self.xp_spin.blockSignals(False)

        self._update_display()


class PrestigeSection(SectionCard):
    """Prestige editing section."""

    value_changed = Signal()
    prestige_changed = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Prestige", parent)
        self._setup_controls()

    def _setup_controls(self) -> None:
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)

        # Prestige combo box
        prestige_row = QHBoxLayout()

        self.prestige_combo = QComboBox()
        for i in range(MAX_PRESTIGE + 1):
            title = PRESTIGE_TITLES.get(i, "Commissioner")
            roman = prestige_to_roman(i)
            if roman:
                display = f"{roman} - {title}"
            else:
                display = f"0 - {title}"
            self.prestige_combo.addItem(display, i)

        self.prestige_combo.currentIndexChanged.connect(self._on_prestige_changed)
        prestige_row.addWidget(self.prestige_combo)

        # Badge indicator for animated badges (11-20)
        self.badge_label = QLabel()
        self.badge_label.setObjectName("description")
        prestige_row.addWidget(self.badge_label)
        prestige_row.addStretch()

        prestige_widget = QWidget()
        prestige_widget.setLayout(prestige_row)
        form.addRow("Prestige:", prestige_widget)

        # Slider for quick selection
        slider_row = QHBoxLayout()

        self.prestige_slider = QSlider(Qt.Orientation.Horizontal)
        self.prestige_slider.setRange(0, MAX_PRESTIGE)
        self.prestige_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.prestige_slider.setTickInterval(5)
        self.prestige_slider.valueChanged.connect(self._on_slider_changed)
        slider_row.addWidget(self.prestige_slider)

        slider_widget = QWidget()
        slider_widget.setLayout(slider_row)
        form.addRow("", slider_widget)

        # Info
        info_label = QLabel(
            "Prestige levels 11-20 have animated badges. "
            "Prestige resets your level but keeps equipment unlocks."
        )
        info_label.setObjectName("description")
        info_label.setWordWrap(True)
        form.addRow("", info_label)

        form_widget = QWidget()
        form_widget.setLayout(form)
        self.add_widget(form_widget)

    @Slot()
    def _on_prestige_changed(self) -> None:
        prestige = self.prestige_combo.currentData()

        self.prestige_slider.blockSignals(True)
        self.prestige_slider.setValue(prestige)
        self.prestige_slider.blockSignals(False)

        self._update_badge_label(prestige)
        self.prestige_changed.emit(prestige)
        self.value_changed.emit()

    @Slot(int)
    def _on_slider_changed(self, value: int) -> None:
        self.prestige_combo.blockSignals(True)
        self.prestige_combo.setCurrentIndex(value)
        self.prestige_combo.blockSignals(False)

        self._update_badge_label(value)
        self.prestige_changed.emit(value)
        self.value_changed.emit()

    def _update_badge_label(self, prestige: int) -> None:
        if prestige >= 11:
            self.badge_label.setText("(Animated Badge)")
            self.badge_label.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['mauve']};")
        else:
            self.badge_label.setText("")

    def get_value(self) -> int:
        return self.prestige_combo.currentData()

    def set_value(self, value: int) -> None:
        self.prestige_combo.blockSignals(True)
        self.prestige_slider.blockSignals(True)

        self.prestige_combo.setCurrentIndex(value)
        self.prestige_slider.setValue(value)

        self.prestige_combo.blockSignals(False)
        self.prestige_slider.blockSignals(False)

        self._update_badge_label(value)


class GeneralTab(QWidget):
    """General editing tab containing Money, Level, Experience, and Prestige."""

    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SECTION_SPACING)

        # Responsive grid for sections
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setHorizontalSpacing(SECTION_SPACING)
        self._grid.setVerticalSpacing(SECTION_SPACING)
        layout.addLayout(self._grid)

        # Create sections
        self.money_section = MoneySection()
        self.level_section = LevelSection()
        self.prestige_section = PrestigeSection()

        # Add sections (default 2-column layout)
        self._apply_layout(columns=2)

        layout.addStretch()

    def resizeEvent(self, event) -> None:
        """Reflow layout based on available width."""
        super().resizeEvent(event)

        # Compact breakpoints: 1 col < 1000px, else 2 cols
        columns = 1 if self.width() < 1000 else 2
        self._apply_layout(columns)

    def _apply_layout(self, columns: int) -> None:
        """Apply grid layout with specified columns."""
        # Clear existing
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        if columns <= 1:
            self._grid.addWidget(self.money_section, 0, 0)
            self._grid.addWidget(self.level_section, 1, 0)
            self._grid.addWidget(self.prestige_section, 2, 0)
            self._grid.setColumnStretch(0, 1)
            return

        # 2-column layout
        self._grid.addWidget(self.money_section, 0, 0)
        self._grid.addWidget(self.level_section, 0, 1)
        self._grid.addWidget(self.prestige_section, 1, 0, 1, 2)

        self._grid.setColumnStretch(0, 1)
        self._grid.setColumnStretch(1, 1)

    def _connect_signals(self) -> None:
        self.money_section.value_changed.connect(self._on_data_changed)
        self.level_section.value_changed.connect(self._on_data_changed)
        self.prestige_section.value_changed.connect(self._on_data_changed)
        self.prestige_section.prestige_changed.connect(self._on_prestige_changed)

    @Slot()
    def _on_data_changed(self) -> None:
        self.data_changed.emit()

    @Slot(int)
    def _on_prestige_changed(self, prestige: int) -> None:
        self.level_section.set_prestige(prestige)

    def load_data(self, save_data: SaveData) -> None:
        """Load save data into the UI."""
        self.money_section.set_value(save_data.money)
        self.level_section.set_values(save_data.level, save_data.experience)
        self.prestige_section.set_value(save_data.prestige_index)

        # Update level display with prestige
        self.level_section.set_prestige(save_data.prestige_index)

    def apply_changes(self, save_data: SaveData) -> None:
        """Apply UI changes back to save data."""
        save_data.money = self.money_section.get_value()
        save_data.level = self.level_section.get_level()
        save_data.experience = self.level_section.get_experience()
        save_data.prestige_index = self.prestige_section.get_value()
