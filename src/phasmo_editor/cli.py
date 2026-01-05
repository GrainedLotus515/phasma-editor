"""
CLI interface for PhasmoEditor.

Provides a command-line interface for editing save files without GUI.
"""

import sys
from pathlib import Path
from typing import Optional

from .game_data import (
    PRESTIGE_TITLES,
    format_level_display,
    get_experience_for_level,
    prestige_to_roman,
)
from .save_parser import SaveData, SaveParser


def print_header() -> None:
    """Print CLI header."""
    print()
    print("  ╔═══════════════════════════════════════╗")
    print("  ║         PhasmoEditor CLI              ║")
    print("  ║    Phasmophobia Save File Editor      ║")
    print("  ╚═══════════════════════════════════════╝")
    print()


def print_save_info(save_data: SaveData) -> None:
    """Print current save file information."""
    prestige = save_data.prestige_index
    level = save_data.level

    print("\n  ┌─ Current Save Data ─────────────────────┐")
    print(f"  │  Money:      ${save_data.money:,}")
    print(f"  │  Level:      {format_level_display(level, prestige)} ({level})")
    print(f"  │  Experience: {save_data.experience:,} XP")

    title = PRESTIGE_TITLES.get(prestige, "Commissioner")
    roman = prestige_to_roman(prestige)
    if roman:
        print(f"  │  Prestige:   {roman} - {title}")
    else:
        print(f"  │  Prestige:   {title} (none)")
    print("  └──────────────────────────────────────────┘\n")


def prompt_int(
    prompt: str, current: int, min_val: int = 0, max_val: int = 999_999_999
) -> Optional[int]:
    """Prompt for an integer value."""
    print(f"  {prompt}")
    print(f"  Current: {current:,}")
    print(f"  Enter new value (or press Enter to skip): ", end="")

    user_input = input().strip()
    if not user_input:
        return None

    try:
        value = int(user_input.replace(",", "").replace("$", ""))
        if value < min_val or value > max_val:
            print(f"  Value must be between {min_val} and {max_val}")
            return None
        return value
    except ValueError:
        print("  Invalid input. Please enter a number.")
        return None


def prompt_prestige(current: int) -> Optional[int]:
    """Prompt for prestige value."""
    print("\n  Available Prestige Levels:")
    for i in range(21):
        title = PRESTIGE_TITLES.get(i, "Commissioner")
        roman = prestige_to_roman(i)
        marker = " <--" if i == current else ""
        if roman:
            print(f"    {i:2}: {roman} - {title}{marker}")
        else:
            print(f"    {i:2}: {title}{marker}")

    print(f"\n  Enter prestige level 0-20 (or press Enter to skip): ", end="")

    user_input = input().strip()
    if not user_input:
        return None

    try:
        value = int(user_input)
        if value < 0 or value > 20:
            print("  Prestige must be between 0 and 20")
            return None
        return value
    except ValueError:
        print("  Invalid input. Please enter a number.")
        return None


def run_cli(save_path: Optional[Path] = None) -> int:
    """Run the CLI interface."""
    print_header()

    # Initialize parser
    parser = SaveParser(save_path)

    # Check if save file exists
    if not parser.save_path.exists():
        print(f"  Error: Save file not found at:")
        print(f"  {parser.save_path}")
        print()
        print("  Use --file to specify a custom path.")
        return 1

    print(f"  Save file: {parser.save_path}")

    # Create backup
    try:
        backup_path = parser.create_timestamped_backup()
        print(f"  Backup created: {backup_path.name}")
    except Exception as e:
        print(f"  Warning: Could not create backup: {e}")

    # Load save file
    print("  Loading save file...")
    try:
        save_data = parser.load()
        print("  Save file loaded successfully!")
    except Exception as e:
        print(f"  Error loading save file: {e}")
        return 1

    # Show current data
    print_save_info(save_data)

    # Edit fields
    changes_made = False

    # Money
    new_money = prompt_int("Money:", save_data.money)
    if new_money is not None:
        save_data.money = new_money
        changes_made = True
        print("  Money updated!")

    # Level
    print()
    new_level = prompt_int("Level:", save_data.level, min_val=1, max_val=9999)
    if new_level is not None:
        save_data.level = new_level
        save_data.experience = get_experience_for_level(new_level)
        changes_made = True
        print(f"  Level updated! Experience set to {save_data.experience:,}")

    # Prestige
    print()
    new_prestige = prompt_prestige(save_data.prestige_index)
    if new_prestige is not None:
        save_data.prestige_index = new_prestige
        changes_made = True
        print("  Prestige updated!")

    # Save changes
    if changes_made:
        print("\n  Saving changes...")
        try:
            parser.save(save_data)
            print("  Changes saved successfully!")
        except Exception as e:
            print(f"  Error saving: {e}")
            return 1

        # Show updated data
        print_save_info(save_data)
    else:
        print("\n  No changes made.")

    print("  Thank you for using PhasmoEditor!")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
