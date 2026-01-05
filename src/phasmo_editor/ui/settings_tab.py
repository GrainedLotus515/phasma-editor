"""
Settings tab for PhasmoEditor.

Provides theme selection, backup management, and advanced tools.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..config import get_config, get_themes_dir, save_config
from ..save_parser import SaveData, SaveParser
from ..theme import CATPPUCCIN_MOCHA
from ..theme.theme_manager import get_theme_manager
from PySide6.QtWidgets import QSizePolicy

from .layout_constants import ROW_SPACING, SECTION_SPACING
from .widgets import CollapsibleSection


class SaveFileSection(CollapsibleSection):
    """Section for save file management."""

    path_changed = Signal(Path)

    def __init__(self, parser: SaveParser, parent: Optional[QWidget] = None):
        super().__init__("Save File", expanded=True, parent=parent)
        self._parser = parser
        self._setup_content()

    def _setup_content(self) -> None:
        # Path display
        path_row = QHBoxLayout()

        path_label = QLabel("Path:")
        path_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 12px;"
        )
        path_row.addWidget(path_label)

        self._path_display = QLabel()
        self._path_display.setStyleSheet(f"""
            color: {CATPPUCCIN_MOCHA["text"]};
            font-size: 12px;
            background-color: {CATPPUCCIN_MOCHA["surface0"]};
            padding: 6px 10px;
            border-radius: 4px;
        """)
        self._path_display.setWordWrap(True)
        self._path_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        path_row.addWidget(self._path_display, 1)

        path_widget = QWidget()
        path_widget.setLayout(path_row)
        self.add_widget(path_widget)

        # Buttons
        btn_row = QHBoxLayout()

        self._browse_btn = QPushButton("Browse...")
        self._browse_btn.setObjectName("secondary_button")
        self._browse_btn.clicked.connect(self._on_browse)
        btn_row.addWidget(self._browse_btn)

        self._open_folder_btn = QPushButton("Open Folder")
        self._open_folder_btn.setObjectName("secondary_button")
        self._open_folder_btn.clicked.connect(self._on_open_folder)
        btn_row.addWidget(self._open_folder_btn)

        btn_row.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        self.add_widget(btn_widget)

        self._update_path_display()

    def _update_path_display(self) -> None:
        path = self._parser.save_path
        self._path_display.setText(str(path))

    @Slot()
    def _on_browse(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Save File",
            str(self._parser.paths["dir"]),
            "Save Files (*.txt);;All Files (*)",
        )
        if file_path:
            self._parser.save_path = Path(file_path)
            self._update_path_display()
            self.path_changed.emit(Path(file_path))

    @Slot()
    def _on_open_folder(self) -> None:
        folder = self._parser.save_path.parent
        if folder.exists():
            if sys.platform == "win32":
                subprocess.run(["explorer", str(folder)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)])
            else:
                subprocess.run(["xdg-open", str(folder)])


class ThemeSection(CollapsibleSection):
    """Section for theme selection."""

    theme_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("Theme", expanded=True, parent=parent)
        self._setup_content()

    def _setup_content(self) -> None:
        # Theme selector
        selector_row = QHBoxLayout()

        selector_label = QLabel("Current Theme:")
        selector_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 12px;"
        )
        selector_row.addWidget(selector_label)

        self._theme_combo = QComboBox()
        self._theme_combo.setMinimumWidth(200)
        self._theme_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self._populate_themes()
        self._theme_combo.currentIndexChanged.connect(self._on_theme_selected)
        selector_row.addWidget(self._theme_combo)

        selector_row.addStretch()

        selector_widget = QWidget()
        selector_widget.setLayout(selector_row)
        self.add_widget(selector_widget)

        # Info label
        info_label = QLabel("Theme changes apply immediately.")
        info_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 11px;"
        )
        self.add_widget(info_label)

        # Buttons
        btn_row = QHBoxLayout()

        self._open_themes_btn = QPushButton("Open Themes Folder")
        self._open_themes_btn.setObjectName("secondary_button")
        self._open_themes_btn.clicked.connect(self._on_open_themes_folder)
        btn_row.addWidget(self._open_themes_btn)

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setObjectName("secondary_button")
        self._refresh_btn.clicked.connect(self._on_refresh)
        btn_row.addWidget(self._refresh_btn)

        btn_row.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        self.add_widget(btn_widget)

        # Help text
        help_label = QLabel(
            "To add custom themes, create a folder in the themes directory\n"
            "with a theme.xml file (qt-material format) and optional styles.qss."
        )
        help_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['overlay0']}; font-size: 11px;"
        )
        help_label.setWordWrap(True)
        self.add_widget(help_label)

    def _populate_themes(self) -> None:
        self._theme_combo.clear()
        manager = get_theme_manager()
        config = get_config()

        for theme in manager.get_available_themes():
            suffix = " (built-in)" if theme.is_builtin else ""
            self._theme_combo.addItem(f"{theme.name}{suffix}", theme.id)

            # Select current theme
            if theme.id == config.theme:
                self._theme_combo.setCurrentIndex(self._theme_combo.count() - 1)

    @Slot(int)
    def _on_theme_selected(self, index: int) -> None:
        theme_id = self._theme_combo.itemData(index)
        if theme_id:
            self.theme_changed.emit(theme_id)

    @Slot()
    def _on_open_themes_folder(self) -> None:
        folder = get_themes_dir()
        folder.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            subprocess.run(["explorer", str(folder)])
        elif sys.platform == "darwin":
            subprocess.run(["open", str(folder)])
        else:
            subprocess.run(["xdg-open", str(folder)])

    @Slot()
    def _on_refresh(self) -> None:
        manager = get_theme_manager()
        manager.refresh()
        self._populate_themes()


class BackupsSection(CollapsibleSection):
    """Section for backup management."""

    backup_restored = Signal()

    def __init__(self, parser: SaveParser, parent: Optional[QWidget] = None):
        super().__init__("Backups", expanded=True, parent=parent)
        self._parser = parser
        self._setup_content()

    def _setup_content(self) -> None:
        # Auto-backup toggle
        auto_row = QHBoxLayout()

        self._auto_backup_cb = QCheckBox("Auto-backup on save")
        self._auto_backup_cb.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['text']};")
        self._auto_backup_cb.setChecked(get_config().auto_backup)
        self._auto_backup_cb.stateChanged.connect(self._on_auto_backup_changed)
        auto_row.addWidget(self._auto_backup_cb)

        auto_row.addStretch()

        auto_widget = QWidget()
        auto_widget.setLayout(auto_row)
        self.add_widget(auto_widget)

        # Backup list
        list_label = QLabel("Recent Backups:")
        list_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['subtext0']}; font-size: 12px;"
        )
        self.add_widget(list_label)

        self._backup_list = QListWidget()
        self._backup_list.setMaximumHeight(150)
        self._backup_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {CATPPUCCIN_MOCHA["surface0"]};
                color: {CATPPUCCIN_MOCHA["text"]};
                border: 1px solid {CATPPUCCIN_MOCHA["surface1"]};
                border-radius: 4px;
            }}
            QListWidget::item {{
                padding: 6px;
            }}
            QListWidget::item:selected {{
                background-color: {CATPPUCCIN_MOCHA["surface1"]};
            }}
        """)
        self.add_widget(self._backup_list)

        # Buttons
        btn_row = QHBoxLayout()

        self._create_btn = QPushButton("Create Backup Now")
        self._create_btn.setObjectName("secondary_button")
        self._create_btn.clicked.connect(self._on_create_backup)
        btn_row.addWidget(self._create_btn)

        self._restore_btn = QPushButton("Restore Selected")
        self._restore_btn.setObjectName("secondary_button")
        self._restore_btn.clicked.connect(self._on_restore_backup)
        btn_row.addWidget(self._restore_btn)

        self._delete_btn = QPushButton("Delete Selected")
        self._delete_btn.setObjectName("danger_button")
        self._delete_btn.clicked.connect(self._on_delete_backup)
        btn_row.addWidget(self._delete_btn)

        btn_row.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        self.add_widget(btn_widget)

        self._refresh_backup_list()

    def _refresh_backup_list(self) -> None:
        self._backup_list.clear()
        backups = self._parser.list_backups()

        for backup in backups[:20]:  # Show last 20
            item = QListWidgetItem(backup.name)
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self._backup_list.addItem(item)

    @Slot(int)
    def _on_auto_backup_changed(self, state: int) -> None:
        config = get_config()
        config.auto_backup = state == Qt.CheckState.Checked.value
        save_config()

    @Slot()
    def _on_create_backup(self) -> None:
        try:
            backup_path = self._parser.create_timestamped_backup()
            self._refresh_backup_list()
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup saved to:\n{backup_path.name}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup:\n{e}")

    @Slot()
    def _on_restore_backup(self) -> None:
        item = self._backup_list.currentItem()
        if item is None:
            QMessageBox.warning(
                self, "No Selection", "Please select a backup to restore."
            )
            return

        backup_path = item.data(Qt.ItemDataRole.UserRole)

        result = QMessageBox.question(
            self,
            "Restore Backup",
            f"Restore from {backup_path.name}?\n\n"
            "This will overwrite your current save file.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                self._parser.restore_backup(backup_path)
                self.backup_restored.emit()
                QMessageBox.information(
                    self, "Restored", "Backup restored successfully!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore backup:\n{e}")

    @Slot()
    def _on_delete_backup(self) -> None:
        item = self._backup_list.currentItem()
        if item is None:
            QMessageBox.warning(
                self, "No Selection", "Please select a backup to delete."
            )
            return

        backup_path = item.data(Qt.ItemDataRole.UserRole)

        result = QMessageBox.question(
            self,
            "Delete Backup",
            f"Delete {backup_path.name}?\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            try:
                backup_path.unlink()
                self._refresh_backup_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete backup:\n{e}")


class AdvancedSection(CollapsibleSection):
    """Section for advanced tools."""

    json_imported = Signal()

    def __init__(self, parser: SaveParser, parent: Optional[QWidget] = None):
        super().__init__("Advanced", expanded=False, parent=parent)
        self._parser = parser
        self._save_data: Optional[SaveData] = None
        self._setup_content()

    def _setup_content(self) -> None:
        # Buttons
        btn_row = QHBoxLayout()

        self._export_btn = QPushButton("Export Decrypted JSON")
        self._export_btn.setObjectName("secondary_button")
        self._export_btn.clicked.connect(self._on_export_json)
        btn_row.addWidget(self._export_btn)

        self._import_btn = QPushButton("Import from JSON")
        self._import_btn.setObjectName("secondary_button")
        self._import_btn.clicked.connect(self._on_import_json)
        btn_row.addWidget(self._import_btn)

        btn_row.addStretch()

        btn_widget = QWidget()
        btn_widget.setLayout(btn_row)
        self.add_widget(btn_widget)

        # Warning
        warning_label = QLabel(
            "Warning: Importing invalid JSON may corrupt your save file.\n"
            "Always create a backup before importing!"
        )
        warning_label.setStyleSheet(
            f"color: {CATPPUCCIN_MOCHA['peach']}; font-size: 11px;"
        )
        warning_label.setWordWrap(True)
        self.add_widget(warning_label)

    def set_save_data(self, save_data: SaveData) -> None:
        self._save_data = save_data

    @Slot()
    def _on_export_json(self) -> None:
        if self._save_data is None:
            QMessageBox.warning(self, "No Data", "No save data loaded.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            str(self._parser.paths["dir"] / "SaveFile_Export.json"),
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                json_str = self._save_data.to_json(compact=False)
                Path(file_path).write_text(json_str, encoding="utf-8")
                QMessageBox.information(
                    self, "Exported", f"JSON exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export:\n{e}")

    @Slot()
    def _on_import_json(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import JSON",
            str(self._parser.paths["dir"]),
            "JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        result = QMessageBox.warning(
            self,
            "Import JSON",
            "This will replace your current save data.\n\n"
            "A backup will be created first. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        try:
            # Create backup first
            self._parser.create_timestamped_backup()

            # Import JSON
            import json

            json_str = Path(file_path).read_text(encoding="utf-8")
            raw_json = json.loads(json_str)

            self._save_data = SaveData(
                raw_json=raw_json, file_path=self._parser.save_path
            )
            self._parser.save(self._save_data)

            self.json_imported.emit()
            QMessageBox.information(self, "Imported", "JSON imported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import:\n{e}")


class AboutSection(CollapsibleSection):
    """Section with about information."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__("About", expanded=False, parent=parent)
        self._setup_content()

    def _setup_content(self) -> None:
        info = QLabel(
            "PhasmoEditor v2.0.0\n\n"
            "A save file editor for Phasmophobia.\n\n"
            "Original C# version by stth12\n"
            "Python port with GUI enhancements\n\n"
            "github.com/stth12/PhasmoEditor"
        )
        info.setStyleSheet(f"color: {CATPPUCCIN_MOCHA['text']}; font-size: 12px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        self.add_widget(info)


class SettingsTab(QWidget):
    """Settings tab for PhasmoEditor."""

    theme_changed = Signal(str)
    save_path_changed = Signal(Path)
    backup_restored = Signal()
    json_imported = Signal()

    def __init__(self, parser: SaveParser, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._parser = parser
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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

        # Save file section
        self._save_file_section = SaveFileSection(self._parser)
        self._save_file_section.path_changed.connect(self.save_path_changed.emit)
        content_layout.addWidget(self._save_file_section)

        # Theme section
        self._theme_section = ThemeSection()
        self._theme_section.theme_changed.connect(self._on_theme_changed)
        content_layout.addWidget(self._theme_section)

        # Backups section
        self._backups_section = BackupsSection(self._parser)
        self._backups_section.backup_restored.connect(self.backup_restored.emit)
        content_layout.addWidget(self._backups_section)

        # Advanced section
        self._advanced_section = AdvancedSection(self._parser)
        self._advanced_section.json_imported.connect(self.json_imported.emit)
        content_layout.addWidget(self._advanced_section)

        # About section
        self._about_section = AboutSection()
        content_layout.addWidget(self._about_section)

        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    @Slot(str)
    def _on_theme_changed(self, theme_id: str) -> None:
        # Save to config
        config = get_config()
        config.theme = theme_id
        save_config()

        # Apply theme
        manager = get_theme_manager()
        app = QApplication.instance()
        if app:
            manager.apply_theme(theme_id, app)

        self.theme_changed.emit(theme_id)

    def set_save_data(self, save_data: SaveData) -> None:
        """Set the save data for advanced operations."""
        self._advanced_section.set_save_data(save_data)

    def load_data(self, save_data: SaveData) -> None:
        """Load save data into the UI."""
        self.set_save_data(save_data)

    def apply_changes(self, save_data: SaveData) -> None:
        """Apply UI changes back to save data."""
        # Settings don't modify save data directly
        pass
