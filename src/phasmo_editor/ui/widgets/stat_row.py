"""
Stat row widget for PhasmoEditor.

Displays a single statistic with optional editing capability.
"""

from typing import Optional, Union

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpinBox,
    QWidget,
)

from ...game_data import StatInfo, format_stat_value
from ...theme import CATPPUCCIN_MOCHA
from ..layout_constants import ROW_SPACING


class StatRow(QWidget):
    """
    A row displaying a statistic value with optional edit mode.
    """

    value_changed = Signal(str, object)  # field_name, new_value

    def __init__(
        self,
        stat_info: StatInfo,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.stat_info = stat_info
        self._value: Union[int, float] = 0
        self._edit_mode = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(ROW_SPACING)

        # Label
        self._label = QLabel(f"{self.stat_info.display_name}:")
        self._label.setStyleSheet(f"""
            color: {CATPPUCCIN_MOCHA["subtext1"]};
            font-size: 13px;
        """)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._label, 2)

        # Value display (read-only mode)
        self._value_label = QLabel()
        self._value_label.setStyleSheet(f"""
            color: {CATPPUCCIN_MOCHA["text"]};
            font-size: 13px;
            font-weight: bold;
        """)
        self._value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._value_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        self._value_label.setMinimumWidth(120)
        layout.addWidget(self._value_label, 0)

        # Value spinbox (edit mode) - integer
        self._int_spinbox = QSpinBox()
        self._int_spinbox.setRange(0, 999_999_999)
        self._int_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }}
            QSpinBox:focus {{
                border-color: {CATPPUCCIN_MOCHA["mauve"]};
            }}
        """)
        self._int_spinbox.valueChanged.connect(self._on_int_value_changed)
        self._int_spinbox.setVisible(False)
        self._int_spinbox.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._int_spinbox, 0)

        # Value spinbox (edit mode) - float
        self._float_spinbox = QDoubleSpinBox()
        self._float_spinbox.setRange(0, 999_999_999)
        self._float_spinbox.setDecimals(2)
        self._float_spinbox.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 100px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {CATPPUCCIN_MOCHA["mauve"]};
            }}
        """)
        self._float_spinbox.valueChanged.connect(self._on_float_value_changed)
        self._float_spinbox.setVisible(False)
        self._float_spinbox.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )
        layout.addWidget(self._float_spinbox, 0)

        # No stretch here; label handles expansion

    def _on_int_value_changed(self, value: int) -> None:
        """Handle integer value change."""
        self._value = value
        self.value_changed.emit(self.stat_info.field, value)

    def _on_float_value_changed(self, value: float) -> None:
        """Handle float value change."""
        self._value = value
        self.value_changed.emit(self.stat_info.field, value)

    def set_value(self, value: Union[int, float]) -> None:
        """Set the statistic value."""
        self._value = value

        # Update display label
        formatted = format_stat_value(value, self.stat_info.format_type)
        self._value_label.setText(formatted)

        # Update spinbox
        if self.stat_info.format_type in ("int", "money"):
            self._int_spinbox.blockSignals(True)
            self._int_spinbox.setValue(int(value))
            self._int_spinbox.blockSignals(False)
        else:
            self._float_spinbox.blockSignals(True)
            self._float_spinbox.setValue(float(value))
            self._float_spinbox.blockSignals(False)

    def get_value(self) -> Union[int, float]:
        """Get the current value."""
        return self._value

    def set_edit_mode(self, enabled: bool) -> None:
        """Enable or disable edit mode."""
        self._edit_mode = enabled

        # Show/hide appropriate widgets
        self._value_label.setVisible(not enabled)

        if self.stat_info.format_type in ("int", "money"):
            self._int_spinbox.setVisible(enabled)
            self._float_spinbox.setVisible(False)
        else:
            self._int_spinbox.setVisible(False)
            self._float_spinbox.setVisible(enabled)

    def is_edit_mode(self) -> bool:
        """Check if edit mode is enabled."""
        return self._edit_mode
