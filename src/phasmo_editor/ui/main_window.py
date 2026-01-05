"""
Main window for PhasmoEditor.

Provides the main application window with tabs for different editing sections.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..config import get_config, save_config
from ..save_parser import SaveData, SaveParser
from ..theme import CATPPUCCIN_MOCHA, get_stylesheet_path
from ..theme.theme_manager import get_theme_manager
from .equipment_tab import EquipmentTab
from .general_tab import GeneralTab
from .settings_tab import SettingsTab
from .stats_tab import StatsTab


class HeaderWidget(QWidget):
    """Header widget with gradient background and title."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("header_widget")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Title
        self.title_label = QLabel("PhasmoEditor")
        self.title_label.setObjectName("header_title")
        layout.addWidget(self.title_label)

        # Subtitle
        self.subtitle_label = QLabel("Phasmophobia Save Editor")
        self.subtitle_label.setObjectName("header_subtitle")
        layout.addWidget(self.subtitle_label)


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    save_loaded = Signal(SaveData)
    save_modified = Signal()

    def __init__(self, save_path: Optional[Path] = None):
        super().__init__()
        self.parser = SaveParser(save_path)
        self.save_data: Optional[SaveData] = None
        self.has_unsaved_changes = False

        self._setup_ui()
        self._apply_theme()
        self._connect_signals()
        self._restore_geometry()

        # Try to auto-load save file
        self._try_auto_load()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("PhasmoEditor - Phasmophobia Save Editor")
        self.setMinimumSize(900, 650)
        self.resize(1100, 750)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.header = HeaderWidget()
        main_layout.addWidget(self.header)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # File controls
        file_controls = self._create_file_controls()
        content_layout.addWidget(file_controls)

        # Tab widget
        self.tab_widget = QTabWidget()
        content_layout.addWidget(self.tab_widget)

        # Create tabs
        self.general_tab = GeneralTab()
        self.tab_widget.addTab(self.general_tab, "General")

        self.equipment_tab = EquipmentTab()
        self.tab_widget.addTab(self.equipment_tab, "Equipment")

        self.stats_tab = StatsTab()
        self.tab_widget.addTab(self.stats_tab, "Stats")

        self.settings_tab = SettingsTab(self.parser)
        self.tab_widget.addTab(self.settings_tab, "Settings")

        main_layout.addWidget(content)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("Ready - Load a save file to begin")

    def _create_file_controls(self) -> QWidget:
        """Create file control buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Load button
        self.load_btn = QPushButton("Load Save")
        self.load_btn.setObjectName("secondary_button")
        self.load_btn.clicked.connect(self._on_load_clicked)
        layout.addWidget(self.load_btn)

        # Browse button
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setObjectName("secondary_button")
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        layout.addWidget(self.browse_btn)

        # Spacer
        layout.addStretch()

        # Current file label (styled like a chip)
        self.file_label = QLabel("No file loaded")
        self.file_label.setObjectName("file_chip")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.file_label, 1)

        # Backup button
        self.backup_btn = QPushButton("Create Backup")
        self.backup_btn.setObjectName("secondary_button")
        self.backup_btn.setEnabled(False)
        self.backup_btn.clicked.connect(self._on_backup_clicked)
        layout.addWidget(self.backup_btn)

        # Save button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setObjectName("primary_button")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._on_save_clicked)
        layout.addWidget(self.save_btn)

        return widget

    def _apply_theme(self) -> None:
        """Apply the theme from config."""
        config = get_config()
        manager = get_theme_manager()

        # Try to apply saved theme
        if not manager.apply_theme(config.theme, QApplication.instance()):
            # Fallback to default theme
            stylesheet_path = get_stylesheet_path()
            if stylesheet_path.exists():
                with open(stylesheet_path, "r") as f:
                    stylesheet = f.read()
                self.setStyleSheet(stylesheet)

            # Set background color
            self.setStyleSheet(
                self.styleSheet()
                + f"\nQMainWindow {{ background-color: {CATPPUCCIN_MOCHA['base']}; }}"
            )

    def _restore_geometry(self) -> None:
        """Restore window geometry from config."""
        config = get_config()

        if config.window.maximized:
            self.showMaximized()
        else:
            self.resize(config.window.width, config.window.height)
            if config.window.x is not None and config.window.y is not None:
                self.move(config.window.x, config.window.y)

    def _save_geometry(self) -> None:
        """Save window geometry to config."""
        config = get_config()

        if self.isMaximized():
            config.window.maximized = True
        else:
            config.window.maximized = False
            config.window.width = self.width()
            config.window.height = self.height()
            config.window.x = self.x()
            config.window.y = self.y()

        save_config()

    def _connect_signals(self) -> None:
        """Connect internal signals."""
        self.save_loaded.connect(self._on_save_loaded)
        self.save_modified.connect(self._on_save_modified)

        # Connect tab signals
        self.general_tab.data_changed.connect(self._on_tab_data_changed)
        self.equipment_tab.data_changed.connect(self._on_tab_data_changed)
        self.stats_tab.data_changed.connect(self._on_tab_data_changed)

        # Settings tab signals
        self.settings_tab.save_path_changed.connect(self._on_save_path_changed)
        self.settings_tab.backup_restored.connect(self._on_backup_restored)
        self.settings_tab.json_imported.connect(self._on_json_imported)

    def _try_auto_load(self) -> None:
        """Try to auto-load save file from default location."""
        if self.parser.save_path.exists():
            self._load_save_file(self.parser.save_path)

    def _load_save_file(self, path: Path) -> None:
        """Load a save file."""
        try:
            self.parser.save_path = path
            self.save_data = self.parser.load()
            self.save_loaded.emit(self.save_data)
            self._update_status(f"Loaded: {path.name}")
            self.file_label.setText(str(path.name))
        except FileNotFoundError:
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Save file not found:\n{path}",
            )
        except ValueError as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load save file:\n{e}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Unexpected error loading save:\n{e}",
            )

    def _update_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_bar.showMessage(message)

    # Slots
    @Slot()
    def _on_load_clicked(self) -> None:
        """Handle load button click."""
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        self._load_save_file(self.parser.save_path)

    @Slot()
    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Save File",
            str(self.parser.paths["dir"]),
            "Save Files (*.txt);;All Files (*)",
        )
        if file_path:
            self._load_save_file(Path(file_path))

    @Slot()
    def _on_backup_clicked(self) -> None:
        """Handle backup button click."""
        try:
            backup_path = self.parser.create_timestamped_backup()
            self._update_status(f"Backup created: {backup_path.name}")
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup saved to:\n{backup_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Backup Error",
                f"Failed to create backup:\n{e}",
            )

    @Slot()
    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        if self.save_data is None:
            return

        try:
            # Auto-backup if enabled
            config = get_config()
            if config.auto_backup:
                self.parser.create_timestamped_backup()

            # Collect changes from tabs
            self.general_tab.apply_changes(self.save_data)
            self.equipment_tab.apply_changes(self.save_data)
            self.stats_tab.apply_changes(self.save_data)

            # Save to file
            self.parser.save(self.save_data)
            self.has_unsaved_changes = False
            self.save_btn.setEnabled(False)
            self._update_status("Changes saved successfully!")

            QMessageBox.information(
                self,
                "Saved",
                "Changes saved successfully!",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save changes:\n{e}",
            )

    @Slot(SaveData)
    def _on_save_loaded(self, save_data: SaveData) -> None:
        """Handle save loaded signal."""
        self.backup_btn.setEnabled(True)
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)

        # Update all tabs
        self.general_tab.load_data(save_data)
        self.equipment_tab.load_data(save_data)
        self.stats_tab.load_data(save_data)
        self.settings_tab.load_data(save_data)

    @Slot()
    def _on_save_modified(self) -> None:
        """Handle save modified signal."""
        self.has_unsaved_changes = True
        self.save_btn.setEnabled(True)
        self._update_status("Unsaved changes")

    @Slot()
    def _on_tab_data_changed(self) -> None:
        """Handle data change from tabs."""
        self.save_modified.emit()

    @Slot(Path)
    def _on_save_path_changed(self, path: Path) -> None:
        """Handle save path change from settings."""
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if result != QMessageBox.StandardButton.Yes:
                return

        self._load_save_file(path)

    @Slot()
    def _on_backup_restored(self) -> None:
        """Handle backup restoration from settings."""
        # Reload the save file
        self._load_save_file(self.parser.save_path)

    @Slot()
    def _on_json_imported(self) -> None:
        """Handle JSON import from settings."""
        # Reload the save file
        self._load_save_file(self.parser.save_path)

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if self.has_unsaved_changes:
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )
            if result == QMessageBox.StandardButton.Save:
                self._on_save_clicked()
            elif result == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        # Save window geometry
        self._save_geometry()
        event.accept()
