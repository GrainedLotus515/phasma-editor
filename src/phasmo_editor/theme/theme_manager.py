"""
Theme manager for PhasmoEditor.

Handles loading, switching, and discovering themes.
Themes are XML files in qt-material format with optional QSS overrides.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..config import get_themes_dir
from . import THEME_DIR


@dataclass
class ThemeInfo:
    """Information about a theme."""

    name: str  # Display name
    id: str  # Internal identifier (directory name)
    xml_path: Path  # Path to theme.xml
    qss_path: Optional[Path]  # Path to styles.qss (optional)
    is_builtin: bool  # Whether this is a built-in theme


class ThemeManager:
    """
    Manages theme discovery, loading, and switching.

    Themes can be:
    1. Built-in: Located in src/phasmo_editor/theme/
    2. User themes: Located in ~/.config/phasmo-editor/themes/{theme_name}/
    """

    def __init__(self):
        self._themes: dict[str, ThemeInfo] = {}
        self._current_theme: Optional[str] = None
        self._discover_themes()

    def _discover_themes(self) -> None:
        """Discover all available themes."""
        self._themes.clear()

        # Built-in theme (Catppuccin Mocha)
        builtin_xml = THEME_DIR / "catppuccin_mocha.xml"
        builtin_qss = THEME_DIR / "styles.qss"

        if builtin_xml.exists():
            self._themes["catppuccin_mocha"] = ThemeInfo(
                name="Catppuccin Mocha",
                id="catppuccin_mocha",
                xml_path=builtin_xml,
                qss_path=builtin_qss if builtin_qss.exists() else None,
                is_builtin=True,
            )

        # User themes
        user_themes_dir = get_themes_dir()
        if user_themes_dir.exists():
            for theme_dir in user_themes_dir.iterdir():
                if not theme_dir.is_dir():
                    continue

                xml_path = theme_dir / "theme.xml"
                if not xml_path.exists():
                    continue

                qss_path = theme_dir / "styles.qss"
                theme_id = theme_dir.name

                # Use directory name as display name, with underscores replaced
                display_name = theme_id.replace("_", " ").title()

                self._themes[theme_id] = ThemeInfo(
                    name=display_name,
                    id=theme_id,
                    xml_path=xml_path,
                    qss_path=qss_path if qss_path.exists() else None,
                    is_builtin=False,
                )

    def refresh(self) -> None:
        """Re-discover themes (call after user adds new themes)."""
        self._discover_themes()

    def get_available_themes(self) -> list[ThemeInfo]:
        """Get list of all available themes."""
        # Sort with built-in themes first, then alphabetically
        return sorted(
            self._themes.values(),
            key=lambda t: (not t.is_builtin, t.name.lower()),
        )

    def get_theme(self, theme_id: str) -> Optional[ThemeInfo]:
        """Get a theme by ID."""
        return self._themes.get(theme_id)

    def get_current_theme(self) -> Optional[str]:
        """Get the current theme ID."""
        return self._current_theme

    def load_theme_stylesheet(self, theme_id: str) -> Optional[str]:
        """
        Load the QSS stylesheet for a theme.

        Args:
            theme_id: The theme identifier

        Returns:
            Combined QSS stylesheet string, or None if theme not found
        """
        theme = self._themes.get(theme_id)
        if theme is None:
            return None

        # Read base QSS from built-in theme (for common styles)
        base_qss = ""
        builtin = self._themes.get("catppuccin_mocha")
        if builtin and builtin.qss_path and builtin.qss_path.exists():
            base_qss = builtin.qss_path.read_text(encoding="utf-8")

        # If this is the built-in theme, just return the base
        if theme.is_builtin:
            return base_qss

        # For user themes, we need to apply color substitutions
        # Read the XML to get colors
        colors = self._parse_theme_xml(theme.xml_path)
        if colors:
            # Replace color placeholders in base QSS
            # The base QSS uses Catppuccin colors directly, so we'd need to
            # substitute them. For now, just use the theme's custom QSS if available.
            pass

        # Read theme-specific QSS if available
        theme_qss = ""
        if theme.qss_path and theme.qss_path.exists():
            theme_qss = theme.qss_path.read_text(encoding="utf-8")
            return theme_qss  # Use theme's custom QSS

        return base_qss

    def _parse_theme_xml(self, xml_path: Path) -> dict[str, str]:
        """
        Parse a qt-material theme XML file to extract colors.

        Args:
            xml_path: Path to the theme XML file

        Returns:
            Dictionary mapping color names to hex values
        """
        import xml.etree.ElementTree as ET

        colors = {}
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            for color_elem in root.findall("color"):
                name = color_elem.get("name")
                value = color_elem.text
                if name and value:
                    colors[name] = value.strip()
        except Exception as e:
            print(f"Warning: Failed to parse theme XML: {e}")

        return colors

    def apply_theme(self, theme_id: str, app) -> bool:
        """
        Apply a theme to the application.

        Args:
            theme_id: The theme identifier
            app: QApplication instance

        Returns:
            True if successful, False otherwise
        """
        theme = self._themes.get(theme_id)
        if theme is None:
            return False

        stylesheet = self.load_theme_stylesheet(theme_id)
        if stylesheet:
            app.setStyleSheet(stylesheet)
            self._current_theme = theme_id
            return True

        return False

    def get_user_themes_dir(self) -> Path:
        """Get the directory where user themes should be placed."""
        return get_themes_dir()

    def create_theme_template(self, theme_name: str) -> Path:
        """
        Create a template theme directory for the user.

        Args:
            theme_name: Name for the new theme

        Returns:
            Path to the created theme directory
        """
        theme_id = theme_name.lower().replace(" ", "_")
        theme_dir = get_themes_dir() / theme_id
        theme_dir.mkdir(parents=True, exist_ok=True)

        # Create template XML
        xml_content = """<resources>
    <!-- Custom theme for PhasmoEditor -->
    <!-- See qt-material documentation for available color names -->

    <!-- Primary Colors -->
    <color name="primaryColor">#cba6f7</color>
    <color name="primaryLightColor">#b4befe</color>
    <color name="primaryDarkColor">#9876c4</color>
    <color name="secondaryColor">#b4befe</color>
    <color name="secondaryLightColor">#cdd6f4</color>
    <color name="secondaryDarkColor">#8c8fc7</color>

    <!-- Text Colors -->
    <color name="primaryTextColor">#cdd6f4</color>
    <color name="secondaryTextColor">#bac2de</color>

    <!-- Background Colors -->
    <color name="backgroundColor">#1e1e2e</color>
    <color name="secondaryBackgroundColor">#181825</color>

    <!-- Status Colors -->
    <color name="danger">#f38ba8</color>
    <color name="warning">#f9e2af</color>
    <color name="success">#a6e3a1</color>
</resources>
"""
        (theme_dir / "theme.xml").write_text(xml_content, encoding="utf-8")

        # Create template QSS (copy from built-in)
        builtin = self._themes.get("catppuccin_mocha")
        if builtin and builtin.qss_path and builtin.qss_path.exists():
            qss_content = builtin.qss_path.read_text(encoding="utf-8")
            # Add header comment
            qss_content = f"""/*
 * Custom theme: {theme_name}
 * 
 * Edit the colors in theme.xml and the styles below.
 * The color values from theme.xml are NOT automatically applied to this file.
 * You need to manually update the hex color codes in this stylesheet.
 */

{qss_content}
"""
            (theme_dir / "styles.qss").write_text(qss_content, encoding="utf-8")

        self._discover_themes()
        return theme_dir


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
