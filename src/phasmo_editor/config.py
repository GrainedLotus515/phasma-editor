"""
Configuration management for PhasmoEditor.

Handles user preferences persistence (theme, window geometry, etc.).
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the configuration directory for PhasmoEditor."""
    if sys.platform == "win32":
        import os

        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path.home() / ".config"

    config_dir = base / "phasmo-editor"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_themes_dir() -> Path:
    """Get the user themes directory."""
    themes_dir = get_config_dir() / "themes"
    themes_dir.mkdir(parents=True, exist_ok=True)
    return themes_dir


@dataclass
class WindowGeometry:
    """Window geometry settings."""

    width: int = 1000
    height: int = 700
    x: Optional[int] = None
    y: Optional[int] = None
    maximized: bool = False


@dataclass
class Config:
    """Application configuration."""

    theme: str = "catppuccin_mocha"
    auto_backup: bool = True
    window: WindowGeometry = field(default_factory=WindowGeometry)
    last_save_path: Optional[str] = None

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_file = get_config_dir() / "config.json"

        if not config_file.exists():
            return cls()

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Parse window geometry
            window_data = data.pop("window", {})
            window = WindowGeometry(**window_data)

            return cls(window=window, **data)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Warning: Failed to load config: {e}")
            return cls()

    def save(self) -> None:
        """Save configuration to file."""
        config_file = get_config_dir() / "config.json"

        data = {
            "theme": self.theme,
            "auto_backup": self.auto_backup,
            "window": asdict(self.window),
            "last_save_path": self.last_save_path,
        }

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save config: {e}")

    def set_window_geometry(
        self,
        width: int,
        height: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
        maximized: bool = False,
    ) -> None:
        """Update window geometry settings."""
        self.window.width = width
        self.window.height = height
        self.window.x = x
        self.window.y = y
        self.window.maximized = maximized


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def save_config() -> None:
    """Save the global configuration."""
    if _config is not None:
        _config.save()
