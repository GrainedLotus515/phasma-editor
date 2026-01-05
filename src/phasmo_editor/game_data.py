"""
Game data constants for Phasmophobia.

Contains level unlock requirements, prestige titles, equipment data,
statistics field mappings, and other game-specific constants.
"""

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# PRESTIGE DATA
# =============================================================================

PRESTIGE_TITLES: dict[int, str] = {
    0: "Intern",
    1: "Recruit",
    2: "Investigator",
    3: "Pvt. Investigator",
    4: "Detective",
    5: "Technician",
    6: "Specialist",
    7: "Analyst",
    8: "Agent",
    9: "Operator",
    10: "Commissioner",
    11: "Commissioner",  # Animated badge
    12: "Commissioner",
    13: "Commissioner",
    14: "Commissioner",
    15: "Commissioner",
    16: "Commissioner",
    17: "Commissioner",
    18: "Commissioner",
    19: "Commissioner",
    20: "Commissioner",
}

# Roman numerals for prestige display
ROMAN_NUMERALS = [
    "",
    "I",
    "II",
    "III",
    "IV",
    "V",
    "VI",
    "VII",
    "VIII",
    "IX",
    "X",
    "XI",
    "XII",
    "XIII",
    "XIV",
    "XV",
    "XVI",
    "XVII",
    "XVIII",
    "XIX",
    "XX",
]

MAX_PRESTIGE = 20
MAX_LEVEL = 9999
PRESTIGE_UNLOCK_LEVEL = 100


def prestige_to_roman(prestige: int) -> str:
    """
    Convert prestige number to Roman numeral display.

    Args:
        prestige: Prestige level (0-20)

    Returns:
        Roman numeral string, or empty string for prestige 0
    """
    if prestige <= 0:
        return ""
    if prestige <= 20:
        return ROMAN_NUMERALS[prestige]
    return str(prestige)


def get_prestige_title(prestige: int) -> str:
    """
    Get the title for a prestige level.

    Args:
        prestige: Prestige level (0-20)

    Returns:
        Title string (e.g., "Investigator", "Commissioner")
    """
    return PRESTIGE_TITLES.get(prestige, "Commissioner")


def format_level_display(level: int, prestige: int) -> str:
    """
    Format level for display like the game does.

    Args:
        level: Player level
        prestige: Prestige level

    Returns:
        Formatted string like "VI-082" or "082"
    """
    roman = prestige_to_roman(prestige)
    if roman:
        return f"{roman}-{level:03d}"
    return f"{level:03d}"


# =============================================================================
# EQUIPMENT DATA
# =============================================================================


@dataclass
class EquipmentInfo:
    """Information about an equipment item."""

    name: str  # Internal field name (e.g., "EMFReader")
    display_name: str  # User-friendly name (e.g., "EMF Reader")
    category: str  # "evidence" or "utility"
    unlock_level: int = 0  # Level required to unlock tier 1
    tier2_level: int = 0  # Level required to unlock tier 2
    tier3_level: int = 0  # Level required to unlock tier 3

    @property
    def tier_field(self) -> str:
        """Field name for current tier (e.g., 'EMFReaderTier')."""
        return f"{self.name}Tier"

    @property
    def tier_unlock_fields(self) -> dict[int, str]:
        """Field names for tier unlock ownership."""
        return {
            1: f"{self.name}TierOneUnlockOwned",
            2: f"{self.name}TierTwoUnlockOwned",
            3: f"{self.name}TierThreeUnlockOwned",
        }

    def loadout_amount_field(self, loadout: int) -> str:
        """Field name for quantity in a loadout (0 or 1)."""
        return f"{self.name}{loadout}Amount"

    def loadout_tier_field(self, loadout: int) -> str:
        """Field name for tier in a loadout (0 or 1)."""
        return f"{self.name}{loadout}Tier"

    @property
    def committed_amount_field(self) -> str:
        """Field name for committed quantity."""
        return f"committed{self.name}Amount"

    @property
    def committed_tier_field(self) -> str:
        """Field name for committed tier (-1 suffix)."""
        return f"{self.name}-1Tier"


# Complete equipment list with actual save file field names
EQUIPMENT: dict[str, EquipmentInfo] = {
    # === EVIDENCE EQUIPMENT ===
    "DOTSProjector": EquipmentInfo(
        name="DOTSProjector",
        display_name="D.O.T.S. Projector",
        category="evidence",
        unlock_level=0,
        tier2_level=29,
        tier3_level=60,
    ),
    "EMFReader": EquipmentInfo(
        name="EMFReader",
        display_name="EMF Reader",
        category="evidence",
        unlock_level=0,
        tier2_level=20,
        tier3_level=52,
    ),
    "GhostWritingBook": EquipmentInfo(
        name="GhostWritingBook",
        display_name="Ghost Writing Book",
        category="evidence",
        unlock_level=0,
        tier2_level=23,
        tier3_level=63,
    ),
    "SpiritBox": EquipmentInfo(
        name="SpiritBox",
        display_name="Spirit Box",
        category="evidence",
        unlock_level=0,
        tier2_level=27,
        tier3_level=54,
    ),
    "Thermometer": EquipmentInfo(
        name="Thermometer",
        display_name="Thermometer",
        category="evidence",
        unlock_level=0,
        tier2_level=36,
        tier3_level=64,
    ),
    "UVLight": EquipmentInfo(
        name="UVLight",
        display_name="UV Light",
        category="evidence",
        unlock_level=0,
        tier2_level=21,
        tier3_level=56,
    ),
    "VideoCamera": EquipmentInfo(
        name="VideoCamera",
        display_name="Video Camera",
        category="evidence",
        unlock_level=0,
        tier2_level=33,
        tier3_level=61,
    ),
    # === UTILITY EQUIPMENT ===
    "Flashlight": EquipmentInfo(
        name="Flashlight",
        display_name="Flashlight",
        category="utility",
        unlock_level=0,
        tier2_level=19,
        tier3_level=35,
    ),
    "Firelight": EquipmentInfo(
        name="Firelight",
        display_name="Candle",
        category="utility",
        unlock_level=0,
        tier2_level=47,
        tier3_level=79,
    ),
    "PhotoCamera": EquipmentInfo(
        name="PhotoCamera",
        display_name="Photo Camera",
        category="utility",
        unlock_level=3,
        tier2_level=25,
        tier3_level=70,
    ),
    "MotionSensor": EquipmentInfo(
        name="MotionSensor",
        display_name="Motion Sensor",
        category="utility",
        unlock_level=5,
        tier2_level=45,
        tier3_level=74,
    ),
    "ParabolicMicrophone": EquipmentInfo(
        name="ParabolicMicrophone",
        display_name="Parabolic Mic",
        category="utility",
        unlock_level=7,
        tier2_level=31,
        tier3_level=72,
    ),
    "Crucifix": EquipmentInfo(
        name="Crucifix",
        display_name="Crucifix",
        category="utility",
        unlock_level=8,
        tier2_level=37,
        tier3_level=90,
    ),
    "Salt": EquipmentInfo(
        name="Salt",
        display_name="Salt",
        category="utility",
        unlock_level=9,
        tier2_level=43,
        tier3_level=68,
    ),
    "Tripod": EquipmentInfo(
        name="Tripod",
        display_name="Tripod",
        category="utility",
        unlock_level=10,
        tier2_level=34,
        tier3_level=62,
    ),
    "SoundSensor": EquipmentInfo(
        name="SoundSensor",
        display_name="Sound Sensor",
        category="utility",
        unlock_level=11,
        tier2_level=32,
        tier3_level=58,
    ),
    "Igniter": EquipmentInfo(
        name="Igniter",
        display_name="Lighter",
        category="utility",
        unlock_level=12,
        tier2_level=41,
        tier3_level=57,
    ),
    "HeadGear": EquipmentInfo(
        name="HeadGear",
        display_name="Head Cam",
        category="utility",
        unlock_level=13,
        tier2_level=49,
        tier3_level=82,
    ),
    "Repellent": EquipmentInfo(
        name="Repellent",
        display_name="Incense",
        category="utility",
        unlock_level=14,
        tier2_level=42,
        tier3_level=85,
    ),
    "SanityMedication": EquipmentInfo(
        name="SanityMedication",
        display_name="Sanity Pills",
        category="utility",
        unlock_level=16,
        tier2_level=39,
        tier3_level=77,
    ),
    "SoundRecorder": EquipmentInfo(
        name="SoundRecorder",
        display_name="Sound Recorder",
        category="utility",
        unlock_level=7,
        tier2_level=31,
        tier3_level=72,
    ),
}


def get_equipment_by_category(category: str) -> list[EquipmentInfo]:
    """Get all equipment in a category."""
    return [eq for eq in EQUIPMENT.values() if eq.category == category]


def get_all_equipment() -> list[EquipmentInfo]:
    """Get all equipment items."""
    return list(EQUIPMENT.values())


# =============================================================================
# LOADOUT DATA
# =============================================================================

NUM_LOADOUTS = 2  # Loadout 0 and Loadout 1


def get_loadout_name_field(loadout: int) -> str:
    """Get the field name for a loadout's name."""
    return f"Loadout{loadout}Name"


# =============================================================================
# STATISTICS DATA
# =============================================================================


@dataclass
class StatInfo:
    """Information about a statistic field."""

    field: str  # Save file field name
    display_name: str  # User-friendly name
    format_type: str  # "int", "money", "time", "distance", "float", "percent"
    category: str  # For grouping in UI
    editable: bool = True  # Whether it can be edited


# Player performance stats
PLAYER_STATS: list[StatInfo] = [
    StatInfo("ghostsIdentifiedAmount", "Ghosts Identified", "int", "performance"),
    StatInfo("ghostsMisidentifiedAmount", "Ghosts Misidentified", "int", "performance"),
    StatInfo("diedAmount", "Times Died", "int", "performance"),
    StatInfo("objectivesCompleted", "Objectives Completed", "int", "performance"),
    StatInfo("amountOfBonesCollected", "Bones Collected", "int", "performance"),
    StatInfo("phrasesRecognized", "Voice Commands Used", "int", "performance"),
    StatInfo("ghostsRepelled", "Ghosts Repelled", "int", "performance"),
    StatInfo("revivedAmount", "Times Revived", "int", "performance"),
]

# Financial stats
FINANCIAL_STATS: list[StatInfo] = [
    StatInfo("moneyEarned", "Money Earned", "money", "financial"),
    StatInfo("moneySpent", "Money Spent", "money", "financial"),
    StatInfo("itemsBought", "Items Bought", "int", "financial"),
    StatInfo("itemsLost", "Items Lost", "int", "financial"),
]

# Time and distance stats
TIME_STATS: list[StatInfo] = [
    StatInfo("timeSpentInvestigating", "Investigation Time", "time", "time"),
    StatInfo("timeSpentInTruck", "Time in Truck", "time", "time"),
    StatInfo("timeSpentInGhostsRoom", "Time in Ghost Room", "time", "time"),
    StatInfo("timeSpentBeingChased", "Time Being Chased", "time", "time"),
    StatInfo("timeSpentInDark", "Time in Dark", "time", "time"),
    StatInfo("timeSpentInLight", "Time in Light", "time", "time"),
    StatInfo("timeInFavouriteRoom", "Time in Favourite Room", "time", "time"),
    StatInfo("distanceTravelled", "Distance Travelled", "distance", "time"),
]

# Sanity stats
SANITY_STATS: list[StatInfo] = [
    StatInfo("sanityLost", "Sanity Lost", "float", "sanity"),
    StatInfo("sanityGained", "Sanity Gained", "float", "sanity"),
]

# Media stats
MEDIA_STATS: list[StatInfo] = [
    StatInfo("photosTaken", "Photos Taken", "int", "media"),
    StatInfo("videosTaken", "Videos Recorded", "int", "media"),
    StatInfo("soundsTaken", "Sounds Recorded", "int", "media"),
]

# Ghost activity stats
GHOST_ACTIVITY_STATS: list[StatInfo] = [
    StatInfo(
        "amountOfGhostInteractions", "Ghost Interactions", "int", "ghost_activity"
    ),
    StatInfo("amountOfGhostEvents", "Ghost Events", "int", "ghost_activity"),
    StatInfo("amountOfGhostHunts", "Ghost Hunts", "int", "ghost_activity"),
    StatInfo("totalHuntTime", "Total Hunt Duration", "time", "ghost_activity"),
    StatInfo("ghostDistanceTravelled", "Ghost Distance", "distance", "ghost_activity"),
    StatInfo("doorsMoved", "Doors Moved", "int", "ghost_activity"),
    StatInfo("objectsUsed", "Objects Used", "int", "ghost_activity"),
    StatInfo("lightsSwitched", "Lights Switched", "int", "ghost_activity"),
    StatInfo("fuseboxToggles", "Fusebox Toggles", "int", "ghost_activity"),
    StatInfo("abilitiesUsed", "Abilities Used", "int", "ghost_activity"),
    StatInfo("roomChanged", "Room Changes", "int", "ghost_activity"),
]

# Cursed possession stats
CURSED_STATS: list[StatInfo] = [
    StatInfo("amountOfCursedPossessionsUsed", "Cursed Items Used", "int", "cursed"),
    StatInfo("amountOfCursedHuntsTriggered", "Cursed Hunts Triggered", "int", "cursed"),
    StatInfo("OuijasFound", "Ouija Boards Found", "int", "cursed"),
    StatInfo("VoodoosFound", "Voodoo Dolls Found", "int", "cursed"),
    StatInfo("MusicBoxesFound", "Music Boxes Found", "int", "cursed"),
    StatInfo("MirrorsFound", "Mirrors Found", "int", "cursed"),
    StatInfo("MonkeyPawFound", "Monkey Paws Found", "int", "cursed"),
]

# All stats grouped
ALL_STATS: dict[str, list[StatInfo]] = {
    "Player Performance": PLAYER_STATS,
    "Financial": FINANCIAL_STATS,
    "Time & Distance": TIME_STATS,
    "Sanity": SANITY_STATS,
    "Media": MEDIA_STATS,
    "Ghost Activity": GHOST_ACTIVITY_STATS,
    "Cursed Possessions": CURSED_STATS,
}

# Dictionary stats (special handling needed)
DICT_STATS = {
    "mostCommonGhosts": "Ghost Encounters",
    "ghostKills": "Deaths by Ghost",
    "playedMaps": "Maps Played",
}

# Ghost types for reference
GHOST_TYPES = [
    "Banshee",
    "Demon",
    "Deogen",
    "Goryo",
    "Hantu",
    "Jinn",
    "Mare",
    "Moroi",
    "Myling",
    "Obake",
    "Oni",
    "Onryo",
    "Phantom",
    "Poltergeist",
    "Raiju",
    "Revenant",
    "Shade",
    "Spirit",
    "Thaye",
    "Mimic",  # Note: save file uses "Mimic" not "TheMimic"
    "TheTwins",
    "Wraith",
    "Yokai",
    "Yurei",
]

# Map IDs (based on save file)
MAP_NAMES = {
    0: "Tanglewood Street House",
    1: "Edgefield Street House",
    2: "Ridgeview Road House",
    3: "Grafton Farmhouse",
    4: "Bleasdale Farmhouse",
    5: "Brownstone High School",
    6: "Maple Lodge Campsite",
    7: "Prison",
    8: "Asylum",
    12: "Sunny Meadows",
    14: "Lighthouse",
    42: "Point Hope",
}


# =============================================================================
# FORMATTING UTILITIES
# =============================================================================


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"


def format_distance(meters: float) -> str:
    """Format meters into human-readable distance."""
    if meters < 1000:
        return f"{meters:.1f}m"
    else:
        return f"{meters / 1000:.2f}km"


def format_money(amount: int) -> str:
    """Format money with $ and commas."""
    return f"${amount:,}"


def format_stat_value(value: float | int, format_type: str) -> str:
    """Format a stat value based on its type."""
    if format_type == "int":
        return f"{int(value):,}"
    elif format_type == "money":
        return format_money(int(value))
    elif format_type == "time":
        return format_time(float(value))
    elif format_type == "distance":
        return format_distance(float(value))
    elif format_type == "float":
        return f"{float(value):,.1f}"
    elif format_type == "percent":
        return f"{float(value):.1f}%"
    else:
        return str(value)


# =============================================================================
# EXPERIENCE REQUIREMENTS
# =============================================================================


def get_experience_for_level(level: int) -> int:
    """
    Calculate cumulative XP needed to reach a level.

    Based on the game's formula.

    Args:
        level: Target level (1-9999)

    Returns:
        Total XP required
    """
    if level <= 1:
        return 0
    if level <= 100:
        # Formula: 100 * (level - 1)^1.73 rounded down
        return int(100 * ((level - 1) ** 1.73))
    if level <= 999:
        # Formula: 283432 + 4971 * (level - 100)
        return 283432 + 4971 * (level - 100)
    # Formula: 4468929 + 100 * (level - 900)^1.73 rounded down
    return int(4468929 + 100 * ((level - 900) ** 1.73))


def get_level_for_experience(xp: int) -> int:
    """
    Calculate level from total XP.

    Args:
        xp: Total experience points

    Returns:
        Player level
    """
    # Binary search for level
    low, high = 1, MAX_LEVEL
    while low < high:
        mid = (low + high + 1) // 2
        if get_experience_for_level(mid) <= xp:
            low = mid
        else:
            high = mid - 1
    return low


# =============================================================================
# DIFFICULTY DATA
# =============================================================================

DIFFICULTIES = {
    "Amateur": {"multiplier": 1.0, "unlock_level": 1},
    "Intermediate": {"multiplier": 2.0, "unlock_level": 10},
    "Professional": {"multiplier": 3.0, "unlock_level": 20},
    "Nightmare": {"multiplier": 4.0, "unlock_level": 30},
    "Insanity": {"multiplier": 6.0, "unlock_level": 40},
    "Custom": {"multiplier": None, "unlock_level": 50},
}
