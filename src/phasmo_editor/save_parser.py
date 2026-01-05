"""
Save file parser for Phasmophobia.

Handles loading, parsing, repairing, and saving Phasmophobia save files.
Includes JSON repair for .NET serialization quirks.
"""

import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .crypto import decrypt_file, encrypt_to_file


def get_default_save_paths() -> dict[str, Path]:
    """
    Get Phasmophobia save file paths for the current platform.

    Returns:
        Dictionary with paths for save_dir, save_file, and backup
    """
    if sys.platform == "win32":
        import os

        user_profile = os.environ.get("USERPROFILE", "")
        save_dir = (
            Path(user_profile)
            / "AppData"
            / "LocalLow"
            / "Kinetic Games"
            / "Phasmophobia"
        )
    elif sys.platform == "linux":
        # Steam Proton path
        save_dir = (
            Path.home()
            / ".steam"
            / "steam"
            / "steamapps"
            / "compatdata"
            / "739630"
            / "pfx"
            / "drive_c"
            / "users"
            / "steamuser"
            / "AppData"
            / "LocalLow"
            / "Kinetic Games"
            / "Phasmophobia"
        )
    else:
        # Fallback to current directory
        save_dir = Path.cwd()

    return {
        "dir": save_dir,
        "save_file": save_dir / "SaveFile.txt",
        "backup": save_dir / "SaveFileBackup.txt",
    }


def repair_json(text: str) -> str:
    """
    Attempt to repair common JSON issues from .NET serialization.

    Fixes:
    - Unquoted numeric keys like {0:39,42:4} -> {"0":39,"42":4}
    - Trailing commas before } or ]

    Args:
        text: Raw JSON text that may have issues

    Returns:
        Repaired JSON text
    """
    # Fix unquoted numeric keys in dictionary-style objects
    # Pattern: { followed by number and colon
    text = re.sub(r"(\{)(\d+):", r'\1"\2":', text)
    # Pattern: comma followed by number and colon
    text = re.sub(r",(\d+):", r',"\1":', text)

    # Fix trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    return text


@dataclass
class SaveData:
    """Container for parsed save data with helper methods."""

    raw_json: dict[str, Any] = field(default_factory=dict)
    file_path: Optional[Path] = None

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the save data.

        Handles the Phasmophobia save format where values are nested:
        {"FieldName": {"__type": "int", "value": 123}}

        Args:
            key: The field name to get
            default: Default value if not found

        Returns:
            The value, or default if not found
        """
        if key not in self.raw_json:
            return default

        field_data = self.raw_json[key]
        if isinstance(field_data, dict) and "value" in field_data:
            return field_data["value"]
        return field_data

    def set_value(self, key: str, value: Any, type_hint: str = "int") -> None:
        """
        Set a value in the save data.

        Args:
            key: The field name to set
            value: The value to set
            type_hint: The __type hint (int, bool, string, float, etc.)
        """
        if key in self.raw_json and isinstance(self.raw_json[key], dict):
            self.raw_json[key]["value"] = value
        else:
            self.raw_json[key] = {"__type": type_hint, "value": value}

    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer value."""
        val = self.get_value(key, default)
        return int(val) if val is not None else default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean value."""
        val = self.get_value(key, default)
        return bool(val) if val is not None else default

    def get_str(self, key: str, default: str = "") -> str:
        """Get a string value."""
        val = self.get_value(key, default)
        return str(val) if val is not None else default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get a float value."""
        val = self.get_value(key, default)
        return float(val) if val is not None else default

    # Convenience properties for common fields
    @property
    def money(self) -> int:
        return self.get_int("PlayersMoney", 0)

    @money.setter
    def money(self, value: int) -> None:
        self.set_value("PlayersMoney", value, "int")

    @property
    def level(self) -> int:
        return self.get_int("NewLevel", 1)

    @level.setter
    def level(self, value: int) -> None:
        self.set_value("NewLevel", value, "int")

    @property
    def experience(self) -> int:
        return self.get_int("Experience", 0)

    @experience.setter
    def experience(self, value: int) -> None:
        self.set_value("Experience", value, "int")

    @property
    def prestige_index(self) -> int:
        return self.get_int("PrestigeIndex", 0)

    @prestige_index.setter
    def prestige_index(self, value: int) -> None:
        self.set_value("PrestigeIndex", value, "int")

    @property
    def prestige_theme(self) -> bool:
        return self.get_bool("PrestigeTheme", False)

    @prestige_theme.setter
    def prestige_theme(self, value: bool) -> None:
        self.set_value("PrestigeTheme", value, "bool")

    def to_json(self, compact: bool = True) -> str:
        """
        Convert save data back to JSON string.

        Args:
            compact: If True, use compact formatting (game default)

        Returns:
            JSON string
        """
        if compact:
            return json.dumps(self.raw_json, separators=(",", ":"))
        return json.dumps(self.raw_json, indent=2)

    # =========================================================================
    # EQUIPMENT HELPERS
    # =========================================================================

    @staticmethod
    def _decode_equipment_tier(raw: int) -> int:
        """Decode raw tier values from save file to display tier (1-3).

        Phasmophobia stores tiers as 0-based values in multiple fields:
            0 -> Tier 1, 1 -> Tier 2, 2 -> Tier 3

        Some older/edge cases may already be 1-based; handle gracefully.
        """
        if raw in (0, 1, 2):
            return raw + 1
        if raw in (1, 2, 3):
            return raw
        return max(1, min(3, int(raw)))

    @staticmethod
    def _encode_equipment_tier(display_tier: int) -> int:
        """Encode display tier (1-3) to raw 0-based save value."""
        tier = max(1, min(3, int(display_tier)))
        return tier - 1

    def get_equipment_tier(self, equipment_name: str) -> int:
        """Get the equipped tier for an equipment item (matches in-game 'All').

        Prefers the committed tier field (e.g. 'EMFReader-1Tier') since that is
        what the in-game loadout uses.
        """
        committed_field = f"{equipment_name}-1Tier"
        if committed_field in self.raw_json:
            raw = self.get_int(committed_field, 0)
            return self._decode_equipment_tier(raw)

        raw = self.get_int(f"{equipment_name}Tier", 0)
        return self._decode_equipment_tier(raw)

    def set_equipment_tier(self, equipment_name: str, tier: int) -> None:
        """Set the equipped tier for an equipment item.

        Writes both the committed tier field and the base tier field for
        consistency.
        """
        raw = self._encode_equipment_tier(tier)
        self.set_value(f"{equipment_name}-1Tier", raw, "int")
        self.set_value(f"{equipment_name}Tier", raw, "int")

    def get_tier_unlocked(self, equipment_name: str, tier: int) -> bool:
        """Check if a specific tier is unlocked for an equipment item."""
        tier_names = {1: "One", 2: "Two", 3: "Three"}
        field = f"{equipment_name}Tier{tier_names[tier]}UnlockOwned"
        return self.get_bool(field, False)

    def set_tier_unlocked(self, equipment_name: str, tier: int, unlocked: bool) -> None:
        """Set whether a specific tier is unlocked for an equipment item."""
        tier_names = {1: "One", 2: "Two", 3: "Three"}
        field = f"{equipment_name}Tier{tier_names[tier]}UnlockOwned"
        self.set_value(field, unlocked, "bool")

    def unlock_all_tiers(self, equipment_name: str) -> None:
        """Unlock all tiers for an equipment item."""
        for tier in [1, 2, 3]:
            self.set_tier_unlocked(equipment_name, tier, True)

    # =========================================================================
    # LOADOUT HELPERS
    # =========================================================================

    def get_loadout_name(self, loadout: int) -> str:
        """Get the name of a loadout.

        loadout:
            -1 -> "All" (committed loadout)
             0 -> Loadout 1
             1 -> Loadout 2
        """
        if loadout == -1:
            return "All"
        return self.get_str(f"Loadout{loadout}Name", f"Loadout {loadout + 1}")

    def set_loadout_name(self, loadout: int, name: str) -> None:
        """Set the name of a loadout (0 or 1)."""
        if loadout == -1:
            return
        self.set_value(f"Loadout{loadout}Name", name, "string")

    def get_loadout_equipment_amount(self, loadout: int, equipment_name: str) -> int:
        """Get the quantity of an equipment item in a loadout."""
        if loadout == -1:
            return self.get_committed_amount(equipment_name)
        return self.get_int(f"{equipment_name}{loadout}Amount", 0)

    def set_loadout_equipment_amount(
        self, loadout: int, equipment_name: str, amount: int
    ) -> None:
        """Set the quantity of an equipment item in a loadout."""
        if loadout == -1:
            self.set_committed_amount(equipment_name, amount)
            return
        self.set_value(f"{equipment_name}{loadout}Amount", amount, "int")

    def get_loadout_equipment_tier(self, loadout: int, equipment_name: str) -> int:
        """Get the tier of an equipment item in a loadout (1-3)."""
        if loadout == -1:
            return self.get_equipment_tier(equipment_name)

        raw = self.get_int(f"{equipment_name}{loadout}Tier", 0)
        # Loadout tiers use the same 0-based encoding.
        return self._decode_equipment_tier(raw)

    def set_loadout_equipment_tier(
        self, loadout: int, equipment_name: str, tier: int
    ) -> None:
        """Set the tier of an equipment item in a loadout."""
        if loadout == -1:
            self.set_equipment_tier(equipment_name, tier)
            return

        raw = self._encode_equipment_tier(tier)
        self.set_value(f"{equipment_name}{loadout}Tier", raw, "int")

    def get_committed_amount(self, equipment_name: str) -> int:
        """Get the committed quantity of an equipment item."""
        return self.get_int(f"committed{equipment_name}Amount", 0)

    def set_committed_amount(self, equipment_name: str, amount: int) -> None:
        """Set the committed quantity of an equipment item."""
        self.set_value(f"committed{equipment_name}Amount", amount, "int")

    def get_committed_tier(self, equipment_name: str) -> int:
        """Get the committed tier of an equipment item (1-3)."""
        raw = self.get_int(f"{equipment_name}-1Tier", 0)
        return self._decode_equipment_tier(raw)

    def set_committed_tier(self, equipment_name: str, tier: int) -> None:
        """Set the committed tier of an equipment item."""
        raw = self._encode_equipment_tier(tier)
        self.set_value(f"{equipment_name}-1Tier", raw, "int")

    # =========================================================================
    # STATS HELPERS
    # =========================================================================

    def get_dict_stat(self, key: str) -> dict[str, int]:
        """
        Get a dictionary statistic (e.g., ghostKills, mostCommonGhosts).

        Returns:
            Dictionary mapping keys to values
        """
        val = self.get_value(key, {})
        if isinstance(val, dict):
            return {str(k): int(v) for k, v in val.items()}
        return {}

    def set_dict_stat(self, key: str, value: dict[str, int]) -> None:
        """Set a dictionary statistic."""
        # Preserve the original type hint if it exists
        if key in self.raw_json and isinstance(self.raw_json[key], dict):
            self.raw_json[key]["value"] = value
        else:
            self.set_value(key, value, "dict")

    def reset_all_stats(self) -> None:
        """Reset all statistics to zero."""
        from .game_data import ALL_STATS, DICT_STATS

        # Reset simple stats
        for stat_list in ALL_STATS.values():
            for stat in stat_list:
                if stat.format_type in ("int", "money"):
                    self.set_value(stat.field, 0, "int")
                elif stat.format_type in ("float", "time", "distance"):
                    self.set_value(stat.field, 0.0, "float")

        # Reset dictionary stats
        for key in DICT_STATS:
            val = self.get_value(key, None)
            if val is not None and isinstance(val, dict):
                # Zero out all values but keep the keys
                zeroed = {k: 0 for k in val.keys()}
                self.set_dict_stat(key, zeroed)


class SaveParser:
    """
    Parser for Phasmophobia save files.

    Handles the full workflow of loading, parsing, modifying, and saving.
    """

    def __init__(self, save_path: Optional[Path] = None):
        """
        Initialize the parser.

        Args:
            save_path: Path to save file. If None, uses default location.
        """
        self.paths = get_default_save_paths()
        self.save_path = save_path or self.paths["save_file"]
        self.save_data: Optional[SaveData] = None

    def load(self) -> SaveData:
        """
        Load and decrypt the save file.

        Returns:
            SaveData object with parsed data

        Raises:
            FileNotFoundError: If save file doesn't exist
            ValueError: If decryption or parsing fails
        """
        if not self.save_path.exists():
            raise FileNotFoundError(f"Save file not found: {self.save_path}")

        # Decrypt
        decrypted_text = decrypt_file(self.save_path)

        # Parse JSON (with repair if needed)
        try:
            raw_json = json.loads(decrypted_text)
        except json.JSONDecodeError:
            # Try to repair JSON
            repaired_text = repair_json(decrypted_text)
            try:
                raw_json = json.loads(repaired_text)
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse save file JSON: {e}")

        self.save_data = SaveData(raw_json=raw_json, file_path=self.save_path)
        return self.save_data

    def create_backup(self, suffix: str = "") -> Path:
        """
        Create a backup of the save file.

        Args:
            suffix: Optional suffix for backup filename

        Returns:
            Path to backup file
        """
        if not self.save_path.exists():
            raise FileNotFoundError(f"Save file not found: {self.save_path}")

        if suffix:
            backup_path = self.save_path.parent / f"SaveFileBackup_{suffix}.txt"
        else:
            backup_path = self.paths["backup"]

        shutil.copy(self.save_path, backup_path)
        return backup_path

    def create_timestamped_backup(self) -> Path:
        """Create a backup with timestamp suffix."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.create_backup(timestamp)

    def save(self, save_data: Optional[SaveData] = None) -> None:
        """
        Save the data back to the save file.

        Args:
            save_data: SaveData to save. Uses self.save_data if None.
        """
        data = save_data or self.save_data
        if data is None:
            raise ValueError("No save data to save")

        json_str = data.to_json(compact=True)
        encrypt_to_file(json_str, self.save_path)

    def restore_backup(self, backup_path: Optional[Path] = None) -> None:
        """
        Restore from a backup file.

        Args:
            backup_path: Path to backup. Uses default backup if None.
        """
        backup = backup_path or self.paths["backup"]
        if not backup.exists():
            raise FileNotFoundError(f"Backup file not found: {backup}")

        shutil.copy(backup, self.save_path)

    def list_backups(self) -> list[Path]:
        """List all backup files in the save directory."""
        save_dir = self.save_path.parent
        backups = list(save_dir.glob("SaveFileBackup*.txt"))
        return sorted(backups, key=lambda p: p.stat().st_mtime, reverse=True)
