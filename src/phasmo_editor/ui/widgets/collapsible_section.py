"""
Collapsible section widget for PhasmoEditor.

A group box that can be expanded/collapsed with a header.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ...theme import CATPPUCCIN_MOCHA
from ..layout_constants import ROW_SPACING, SECTION_SPACING, TIGHT_SPACING


class CollapsibleSection(QWidget):
    """
    A collapsible section widget with a header that can expand/collapse content.
    """

    toggled = Signal(bool)  # Emitted when expanded/collapsed

    def __init__(
        self,
        title: str,
        expanded: bool = True,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self._expanded = expanded
        self._title = title
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(TIGHT_SPACING)

        # Header
        self._header = QFrame()
        self._header.setObjectName("collapsible_header")
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setProperty("expanded", self._expanded)
        self._header.setStyleSheet("")

        header_layout = QHBoxLayout(self._header)
        # Compact header sizing (Material-ish)
        header_layout.setContentsMargins(10, 6, 10, 6)
        header_layout.setSpacing(ROW_SPACING)

        # Arrow indicator
        self._arrow = QLabel()
        self._arrow.setFixedWidth(20)
        self._update_arrow()
        header_layout.addWidget(self._arrow)

        # Title
        self._title_label = QLabel(self._title)
        self._title_label.setStyleSheet("")
        header_layout.addWidget(self._title_label)

        header_layout.addStretch()

        layout.addWidget(self._header)

        # Content container
        self._content_container = QFrame()
        self._content_container.setObjectName("collapsible_content")
        self._content_container.setStyleSheet("")

        self._content_layout = QVBoxLayout(self._content_container)
        self._content_layout.setContentsMargins(12, 12, 12, 12)
        self._content_layout.setSpacing(ROW_SPACING)

        layout.addWidget(self._content_container)

        # Set initial state
        self._content_container.setVisible(self._expanded)

        # Connect header click
        self._header.mousePressEvent = self._on_header_clicked

    def _update_arrow(self) -> None:
        """Update the arrow indicator."""
        if self._expanded:
            self._arrow.setText("▼")
        else:
            self._arrow.setText("▶")
        self._arrow.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['mauve']};")

    def _on_header_clicked(self, event) -> None:
        """Handle header click to toggle expansion."""
        self.toggle()

    def toggle(self) -> None:
        """Toggle the expanded/collapsed state."""
        self._expanded = not self._expanded
        self._content_container.setVisible(self._expanded)
        self._header.setProperty("expanded", self._expanded)
        self._header.style().unpolish(self._header)
        self._header.style().polish(self._header)
        self._update_arrow()
        self.toggled.emit(self._expanded)

    def expand(self) -> None:
        """Expand the section."""
        if not self._expanded:
            self.toggle()

    def collapse(self) -> None:
        """Collapse the section."""
        if self._expanded:
            self.toggle()

    def is_expanded(self) -> bool:
        """Check if the section is expanded."""
        return self._expanded

    def set_title(self, title: str) -> None:
        """Set the section title."""
        self._title = title
        self._title_label.setText(title)

    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the content area."""
        self._content_layout.addWidget(widget)

    def add_layout(self, layout) -> None:
        """Add a layout to the content area."""
        self._content_layout.addLayout(layout)

    def content_layout(self) -> QVBoxLayout:
        """Get the content layout for adding widgets directly."""
        return self._content_layout

    def clear_content(self) -> None:
        """Remove all widgets from the content area."""
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
