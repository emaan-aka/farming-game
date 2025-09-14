"""
Game constants, settings, and data registries for the farming game.
"""
from dataclasses import dataclass
from typing import List

# Game settings
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 750
FPS = 60
GRID_SIZE = 40
FIELD_WIDTH = 18
FIELD_HEIGHT = 16

# Time settings (1 game minute = 1 real second)
GAME_DAY_LENGTH = 900  # 900 game minutes = 15 real minutes
MINUTES_PER_SECOND = 1  # 1 game minute per real second

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
LIGHT_BROWN = (153, 117, 98)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Rarity colors
RARITY_COLORS = {
    "common": (200, 200, 200),      # Light gray
    "uncommon": (0, 255, 0),        # Green  
    "rare": (0, 100, 255),          # Blue
    "legendary": (255, 215, 0)      # Gold
}

# Seed colors (for seed backgrounds)
SEED_COLORS = {
    "carrot_seeds": (255, 140, 0),      # Orange
    "tomato_seeds": (220, 20, 60),      # Crimson red
    "melon_seeds": (144, 238, 144),     # Light green
    "gigantic_pumpkin_seeds": (255, 165, 0)  # Orange
}

@dataclass
class PlantData:
    name: str
    growth_stages: int
    growth_time_per_stage: int  # game minutes
    water_requirements: List[int]  # which stages need water (0-indexed)
    sell_price: int
    sprite: str
    seed_cost: int = 0

@dataclass 
class ForageData:
    name: str
    rarity: str
    spawn_probability: float
    sell_price: int
    respawn_time: int  # game minutes
    sprite: str

# Plant registry
PLANT_REGISTRY = {
    "carrot": PlantData("Carrot", 3, 40, [0], 25, "🥕", 1),
    "tomato": PlantData("Tomato", 4, 75, [0, 2], 50, "🍅", 2),
    "melon": PlantData("Melon", 5, 120, [0, 2, 3], 100, "🍈", 5),
    "gigantic_pumpkin": PlantData("Gigantic Pumpkin", 7, 128, [0, 2, 3, 4, 5], 1000, "🎃", 500)
}

# Forage registry  
FORAGE_REGISTRY = {
    "wild_berries": ForageData("Wild Berries", "common", 0.08, 15, 60, "🫐"),
    "herbs": ForageData("Wild Herbs", "common", 0.07, 12, 80, "🌿"),
    "mushrooms": ForageData("Mushrooms", "uncommon", 0.04, 30, 120, "🍄"),
    "flowers": ForageData("Wild Flowers", "uncommon", 0.03, 25, 100, "🌸"),
    "crystals": ForageData("Crystals", "rare", 0.015, 120, 300, "💎"),
    "ancient_coin": ForageData("Ancient Coin", "rare", 0.008, 180, 350, "🪙"),
    "golden_artifact": ForageData("Golden Artifact", "legendary", 0.003, 600, 600, "🏆")
}

# UI settings
UI_PANEL_WIDTH = 300
FONT_SIZE = 24

# Game defaults
DEFAULT_STARTING_MONEY = 20
DEFAULT_STARTING_SEEDS = {"carrot_seeds": 3, "tomato_seeds": 2}
MESSAGE_DISPLAY_TIME = 2000  # milliseconds
MOVEMENT_DELAY = 150  # milliseconds
MAX_INVENTORY_SLOTS = 8

# Player position defaults
DEFAULT_PLAYER_X = 9
DEFAULT_PLAYER_Y = 7

# Emoji sizes
PLANT_EMOJI_SIZE = 30
PLAYER_EMOJI_SIZE = 30
HELD_ITEM_EMOJI_SIZE = 18
INVENTORY_EMOJI_SIZE = 32
SHOP_EMOJI_SIZE = 30