"""
Field grid system and cell management.
"""
from typing import List, Optional
import random
from ..data.data_classes import Position, CellState, CellType, InteractionResult
from ..data.constants import FIELD_WIDTH, FIELD_HEIGHT, FORAGE_REGISTRY

class Field:
    def __init__(self):
        self.cells: List[List[CellState]] = []
        self.initialize_field()
    
    def initialize_field(self):
        self.cells = [[CellState() for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]
    
    def get_cell(self, pos: Position) -> Optional[CellState]:
        if 0 <= pos.x < FIELD_WIDTH and 0 <= pos.y < FIELD_HEIGHT:
            return self.cells[pos.y][pos.x]
        return None
    
    def set_cell(self, pos: Position, cell: CellState) -> bool:
        if 0 <= pos.x < FIELD_WIDTH and 0 <= pos.y < FIELD_HEIGHT:
            self.cells[pos.y][pos.x] = cell
            return True
        return False
    
    def is_valid_position(self, pos: Position) -> bool:
        return 0 <= pos.x < FIELD_WIDTH and 0 <= pos.y < FIELD_HEIGHT
    
    def can_plant_at(self, pos: Position) -> bool:
        cell = self.get_cell(pos)
        return cell is not None and cell.cell_type == CellType.EMPTY
    
    def can_harvest_at(self, pos: Position) -> bool:
        cell = self.get_cell(pos)
        if cell is None or cell.cell_type != CellType.PLANTED:
            return False
        return cell.plant_type is not None
    
    def can_forage_at(self, pos: Position) -> bool:
        cell = self.get_cell(pos)
        return cell is not None and cell.cell_type == CellType.FORAGE and cell.forage_item is not None
    
    def update_forage_spawns(self, current_time: int):
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                cell = self.cells[y][x]
                
                # Only spawn on empty cells
                if cell.cell_type == CellType.EMPTY:
                    # Attempt to spawn forage items
                    for forage_id, forage_data in FORAGE_REGISTRY.items():
                        if random.random() < forage_data.spawn_probability / 1000:  # Reduced probability per frame
                            cell.cell_type = CellType.FORAGE
                            cell.forage_item = forage_id
                            cell.forage_spawn_time = current_time
                            break
                
                # Remove expired forage items
                elif cell.cell_type == CellType.FORAGE and cell.forage_item:
                    forage_data = FORAGE_REGISTRY.get(cell.forage_item)
                    if forage_data and current_time - cell.forage_spawn_time >= forage_data.respawn_time:
                        cell.cell_type = CellType.EMPTY
                        cell.forage_item = None
                        cell.forage_spawn_time = 0
    
    def get_all_cells(self) -> List[List[CellState]]:
        return self.cells