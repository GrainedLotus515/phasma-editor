"""
Theme module for PhasmoEditor.

Provides Catppuccin Mocha theming with purple (Mauve) accents.
"""

from pathlib import Path

# Theme directory
THEME_DIR = Path(__file__).parent

# Catppuccin Mocha colors
CATPPUCCIN_MOCHA = {
    # Accent colors
    "rosewater": "#f5e0dc",
    "flamingo": "#f2cdcd",
    "pink": "#f5c2e7",
    "mauve": "#cba6f7",  # Primary accent
    "red": "#f38ba8",
    "maroon": "#eba0ac",
    "peach": "#fab387",
    "yellow": "#f9e2af",
    "green": "#a6e3a1",
    "teal": "#94e2d5",
    "sky": "#89dceb",
    "sapphire": "#74c7ec",
    "blue": "#89b4fa",
    "lavender": "#b4befe",  # Secondary accent (for gradients)
    # Neutral colors
    "text": "#cdd6f4",
    "subtext1": "#bac2de",
    "subtext0": "#a6adc8",
    "overlay2": "#9399b2",
    "overlay1": "#7f849c",
    "overlay0": "#6c7086",
    "surface2": "#585b70",
    "surface1": "#45475a",
    "surface0": "#313244",
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
}


def get_theme_xml_path() -> Path:
    """Get path to the Catppuccin theme XML file."""
    return THEME_DIR / "catppuccin_mocha.xml"


def get_stylesheet_path() -> Path:
    """Get path to the custom QSS stylesheet."""
    return THEME_DIR / "styles.qss"


def get_gradient_css(
    start_color: str, end_color: str, direction: str = "horizontal"
) -> str:
    """
    Generate a Qt gradient CSS string.

    Args:
        start_color: Starting color (hex)
        end_color: Ending color (hex)
        direction: "horizontal" or "vertical"

    Returns:
        Qt gradient CSS string
    """
    if direction == "horizontal":
        return f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {start_color}, stop:1 {end_color})"
    return f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {start_color}, stop:1 {end_color})"
