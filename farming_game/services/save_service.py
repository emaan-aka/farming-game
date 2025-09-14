"""
Save service for handling game state persistence.
"""
from typing import Optional, List, Dict, Any
from farming_game.database.repository import SaveRepository, FieldRepository, InventoryRepository, PlayerRepository
from farming_game.database.database import get_session
from farming_game.data.data_classes import GameState, Position, CellState, CellType

class SaveService:
    """Service for managing game saves."""
    
    def __init__(self):
        self.session = get_session()
        self.save_repo = SaveRepository(self.session)
        self.field_repo = FieldRepository(self.session)
        self.inventory_repo = InventoryRepository(self.session)
        self.player_repo = PlayerRepository(self.session)
    
    def save_game_state(self, player_id: int, save_name: str, game_state: GameState, 
                       player_money: int, inventory: Dict[str, int], 
                       field_cells: List[List[CellState]]) -> bool:
        """Save complete game state to database."""
        try:
            # Prepare game state data
            game_state_data = {
                'day': game_state.day,
                'time_minutes': int(game_state.time_minutes),
                'player_pos_x': game_state.player_pos.x,
                'player_pos_y': game_state.player_pos.y,
                'player_money': player_money
            }
            
            # Check if save already exists
            existing_saves = self.save_repo.get_saves_by_player(player_id)
            existing_save = next((s for s in existing_saves if s.save_name == save_name), None)
            
            if existing_save:
                # Update existing save
                save = self.save_repo.update_save(existing_save.id, game_state_data)
            else:
                # Create new save
                save = self.save_repo.create_save(player_id, save_name, game_state_data)
            
            if save:
                # Save field state and inventory
                self.field_repo.save_field_state(save.id, field_cells)
                self.inventory_repo.save_inventory(save.id, inventory)
                
                # Update player's last played time
                self.player_repo.update_last_played(player_id)
                
                return True
                
        except Exception as e:
            print(f"Failed to save game: {e}")
            self.session.rollback()
            
        return False
    
    def load_game_state(self, save_id: int) -> Optional[Dict[str, Any]]:
        """Load complete game state from database."""
        try:
            save = self.save_repo.get_save_by_id(save_id)
            if not save:
                return None
            
            # Load field state
            field_cells_data = self.field_repo.load_field_state(save_id)
            
            # Load inventory
            inventory = self.inventory_repo.load_inventory(save_id)
            
            return {
                'save': save,
                'field_cells_data': field_cells_data,
                'inventory': inventory
            }
            
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None
    
    def get_player_saves(self, player_id: int) -> List[Dict[str, Any]]:
        """Get all saves for a player with summary info."""
        saves = self.save_repo.get_saves_by_player(player_id)
        return [{
            'id': save.id,
            'name': save.save_name,
            'day': save.day,
            'money': save.player_money,
            'last_played': save.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'created': save.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for save in saves]
    
    def delete_save(self, save_id: int) -> bool:
        """Delete a save file."""
        return self.save_repo.delete_save(save_id)
    
    def create_field_from_data(self, field_cells_data: List, field_width: int, field_height: int) -> List[List[CellState]]:
        """Reconstruct field state from database data."""
        # Initialize empty field
        field_cells = [[CellState() for _ in range(field_width)] for _ in range(field_height)]
        
        # Populate with saved data
        for cell_data in field_cells_data:
            if 0 <= cell_data.x < field_width and 0 <= cell_data.y < field_height:
                cell = field_cells[cell_data.y][cell_data.x]
                cell.cell_type = CellType(cell_data.cell_type)
                cell.plant_type = cell_data.plant_type
                cell.growth_stage = cell_data.growth_stage
                cell.watered = cell_data.watered
                cell.forage_item = cell_data.forage_item
                cell.forage_spawn_time = cell_data.forage_spawn_time
                cell.plant_timer = cell_data.plant_timer
        
        return field_cells
    
    def close(self):
        """Close database session."""
        self.session.close()