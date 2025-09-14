"""
Plant system with growth mechanics and interactions.
"""
from typing import Optional, List
from ..data.data_classes import Position, CellState, CellType, InteractionResult
from ..data.constants import PLANT_REGISTRY
from ..core.player import Player
from ..core.field import Field

class PlantSystem:
    def __init__(self, field: Field):
        self.field = field
    
    def plant_seed(self, player: Player, pos: Position, plant_type: str) -> InteractionResult:
        if not self.field.can_plant_at(pos):
            return InteractionResult.ALREADY_PLANTED
        
        seed_name = player.get_seed_for_plant(plant_type)
        if not player.has_item(seed_name):
            return InteractionResult.NO_SEEDS
        
        plant_data = PLANT_REGISTRY.get(plant_type)
        if not plant_data:
            return InteractionResult.FAILED
        
        if not player.spend_money(plant_data.seed_cost):
            return InteractionResult.NO_MONEY
        
        player.remove_item(seed_name)
        
        cell = self.field.get_cell(pos)
        cell.cell_type = CellType.PLANTED
        cell.plant_type = plant_type
        cell.growth_stage = 0
        cell.plant_timer = 0
        cell.watered = False
        
        return InteractionResult.SUCCESS
    
    def water_plant(self, pos: Position) -> InteractionResult:
        cell = self.field.get_cell(pos)
        if not cell or cell.cell_type != CellType.PLANTED:
            return InteractionResult.NOT_POSSIBLE
        
        if cell.watered:
            return InteractionResult.NOT_POSSIBLE
        
        cell.watered = True
        return InteractionResult.SUCCESS
    
    def harvest_plant(self, player: Player, pos: Position) -> InteractionResult:
        if not self.field.can_harvest_at(pos):
            return InteractionResult.NOTHING_TO_HARVEST
        
        cell = self.field.get_cell(pos)
        plant_data = PLANT_REGISTRY.get(cell.plant_type)
        
        if not plant_data:
            return InteractionResult.FAILED
        
        # Check if plant is fully grown
        if cell.growth_stage < plant_data.growth_stages - 1:
            return InteractionResult.NOT_READY
        
        # Harvest the plant
        harvested_item = cell.plant_type
        player.add_item(harvested_item)
        
        # Reset cell
        cell.cell_type = CellType.EMPTY
        cell.plant_type = None
        cell.growth_stage = 0
        cell.plant_timer = 0
        cell.watered = False
        
        return InteractionResult.SUCCESS
    
    def update_plant_growth(self, current_time_minutes: int):
        for y in range(len(self.field.cells)):
            for x in range(len(self.field.cells[0])):
                cell = self.field.cells[y][x]
                
                if cell.cell_type == CellType.PLANTED and cell.plant_type:
                    plant_data = PLANT_REGISTRY.get(cell.plant_type)
                    if not plant_data:
                        continue
                    
                    # Check if plant needs water at this stage
                    needs_water = cell.growth_stage in plant_data.water_requirements
                    
                    # Only grow if watered when needed, or if no water needed
                    can_grow = not needs_water or cell.watered
                    
                    if can_grow:
                        cell.plant_timer += 1  # Increment each update (roughly once per second)
                        
                        # Check if ready to advance to next stage
                        if cell.plant_timer >= plant_data.growth_time_per_stage:
                            if cell.growth_stage < plant_data.growth_stages - 1:
                                cell.growth_stage += 1
                                cell.plant_timer = 0
                                cell.watered = False  # Reset watered status for next stage
    
    def get_plant_growth_progress(self, pos: Position) -> Optional[float]:
        cell = self.field.get_cell(pos)
        if not cell or cell.cell_type != CellType.PLANTED or not cell.plant_type:
            return None
        
        plant_data = PLANT_REGISTRY.get(cell.plant_type)
        if not plant_data:
            return None
        
        stage_progress = cell.plant_timer / plant_data.growth_time_per_stage
        total_progress = (cell.growth_stage + stage_progress) / plant_data.growth_stages
        return min(total_progress, 1.0)