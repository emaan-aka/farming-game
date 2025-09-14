"""
Forage system with random spawning and rarity mechanics.
"""
from typing import Optional
from ..data.data_classes import Position, CellState, CellType, InteractionResult
from ..data.constants import FORAGE_REGISTRY
from ..core.player import Player
from ..core.field import Field

class ForageSystem:
    def __init__(self, field: Field):
        self.field = field
    
    def forage_item(self, player: Player, pos: Position) -> InteractionResult:
        if not self.field.can_forage_at(pos):
            return InteractionResult.NOTHING_TO_HARVEST
        
        cell = self.field.get_cell(pos)
        forage_data = FORAGE_REGISTRY.get(cell.forage_item)
        
        if not forage_data:
            return InteractionResult.FAILED
        
        # Collect the forage item
        player.add_item(cell.forage_item)
        
        # Clear the cell
        cell.cell_type = CellType.EMPTY
        cell.forage_item = None
        cell.forage_spawn_time = 0
        
        return InteractionResult.SUCCESS
    
    def get_forage_rarity(self, pos: Position) -> Optional[str]:
        cell = self.field.get_cell(pos)
        if not cell or cell.cell_type != CellType.FORAGE or not cell.forage_item:
            return None
        
        forage_data = FORAGE_REGISTRY.get(cell.forage_item)
        return forage_data.rarity if forage_data else None