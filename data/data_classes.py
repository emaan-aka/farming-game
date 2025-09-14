"""
Core data classes for the farming game.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum

@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class CellType(Enum):
    EMPTY = "empty"
    PLANTED = "planted"
    FORAGE = "forage"

@dataclass
class CellState:
    cell_type: CellType = CellType.EMPTY
    plant_type: Optional[str] = None
    growth_stage: int = 0
    watered: bool = False
    last_watered_day: int = -1
    forage_item: Optional[str] = None
    forage_spawn_time: int = 0
    plant_timer: int = 0  # tracks growth progress

@dataclass
class GameState:
    day: int = 1
    time_minutes: int = 0  # current time in game minutes
    player_pos: Position = field(default_factory=lambda: Position(9, 7))
    player_money: int = 100
    inventory: Dict[str, int] = field(default_factory=dict)
    field_state: List[List[CellState]] = field(default_factory=list)
    chest_contents: Dict[str, int] = field(default_factory=dict)
    
    def get_time_string(self) -> str:
        hours = int(self.time_minutes // 60) % 24
        minutes = int(self.time_minutes % 60)
        return f"Day {self.day} - {hours:02d}:{minutes:02d}"

class InteractionResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    NOT_POSSIBLE = "not_possible"
    NO_SEEDS = "no_seeds"
    NO_MONEY = "no_money"
    ALREADY_PLANTED = "already_planted"
    NOT_READY = "not_ready"
    NOTHING_TO_HARVEST = "nothing_to_harvest"