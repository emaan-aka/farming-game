"""
Repository pattern for database operations.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from farming_game.database.models import Player, GameSave, FieldCell, InventoryItem
from farming_game.database.database import get_session

class PlayerRepository:
    """Repository for player operations."""
    
    def __init__(self, session: Session = None):
        self.session = session or get_session()
        
    def create_player(self, username: str) -> Player:
        """Create a new player."""
        player = Player(username=username)
        self.session.add(player)
        self.session.commit()
        return player
        
    def get_player_by_username(self, username: str) -> Optional[Player]:
        """Get player by username."""
        return self.session.query(Player).filter(Player.username == username).first()
        
    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Get player by ID."""
        return self.session.query(Player).filter(Player.id == player_id).first()
        
    def get_all_players(self) -> List[Player]:
        """Get all players."""
        return self.session.query(Player).order_by(Player.username).all()
        
    def update_last_played(self, player_id: int):
        """Update player's last played timestamp."""
        from datetime import datetime
        player = self.get_player_by_id(player_id)
        if player:
            player.last_played = datetime.utcnow()
            self.session.commit()

class SaveRepository:
    """Repository for game save operations."""
    
    def __init__(self, session: Session = None):
        self.session = session or get_session()
        
    def create_save(self, player_id: int, save_name: str, game_state_data: Dict[str, Any]) -> GameSave:
        """Create a new game save."""
        save = GameSave(
            player_id=player_id,
            save_name=save_name,
            day=game_state_data.get('day', 1),
            time_minutes=game_state_data.get('time_minutes', 0),
            player_pos_x=game_state_data.get('player_pos_x', 9),
            player_pos_y=game_state_data.get('player_pos_y', 7),
            player_money=game_state_data.get('player_money', 100)
        )
        self.session.add(save)
        self.session.commit()
        return save
        
    def get_saves_by_player(self, player_id: int) -> List[GameSave]:
        """Get all saves for a player."""
        return (self.session.query(GameSave)
                .filter(GameSave.player_id == player_id)
                .order_by(desc(GameSave.updated_at))
                .all())
                
    def get_save_by_id(self, save_id: int) -> Optional[GameSave]:
        """Get save by ID."""
        return self.session.query(GameSave).filter(GameSave.id == save_id).first()
        
    def update_save(self, save_id: int, game_state_data: Dict[str, Any]):
        """Update an existing save."""
        from datetime import datetime
        save = self.get_save_by_id(save_id)
        if save:
            save.day = game_state_data.get('day', save.day)
            save.time_minutes = game_state_data.get('time_minutes', save.time_minutes)
            save.player_pos_x = game_state_data.get('player_pos_x', save.player_pos_x)
            save.player_pos_y = game_state_data.get('player_pos_y', save.player_pos_y)
            save.player_money = game_state_data.get('player_money', save.player_money)
            save.updated_at = datetime.utcnow()
            self.session.commit()
            return save
        return None
        
    def delete_save(self, save_id: int) -> bool:
        """Delete a save (cascades to field cells and inventory)."""
        save = self.get_save_by_id(save_id)
        if save:
            self.session.delete(save)
            self.session.commit()
            return True
        return False

class FieldRepository:
    """Repository for field cell operations."""
    
    def __init__(self, session: Session = None):
        self.session = session or get_session()
        
    def save_field_state(self, save_id: int, field_cells: List[List[Any]]):
        """Save complete field state, replacing existing data."""
        # Clear existing field data for this save
        self.session.query(FieldCell).filter(FieldCell.save_id == save_id).delete()
        
        # Save only non-empty cells for efficiency
        for y, row in enumerate(field_cells):
            for x, cell in enumerate(row):
                if cell.cell_type.value != 'empty':  # Only save non-empty cells
                    field_cell = FieldCell(
                        save_id=save_id,
                        x=x,
                        y=y,
                        cell_type=cell.cell_type.value,
                        plant_type=cell.plant_type,
                        growth_stage=cell.growth_stage,
                        watered=cell.watered,
                        forage_item=cell.forage_item,
                        forage_spawn_time=cell.forage_spawn_time,
                        plant_timer=cell.plant_timer
                    )
                    self.session.add(field_cell)
        
        self.session.commit()
        
    def load_field_state(self, save_id: int) -> List[FieldCell]:
        """Load field state for a save."""
        return (self.session.query(FieldCell)
                .filter(FieldCell.save_id == save_id)
                .all())

class InventoryRepository:
    """Repository for inventory operations."""
    
    def __init__(self, session: Session = None):
        self.session = session or get_session()
        
    def save_inventory(self, save_id: int, inventory: Dict[str, int]):
        """Save player inventory, replacing existing data."""
        # Clear existing inventory for this save
        self.session.query(InventoryItem).filter(InventoryItem.save_id == save_id).delete()
        
        # Save inventory items
        for item_name, quantity in inventory.items():
            if quantity > 0:  # Only save items with positive quantities
                inventory_item = InventoryItem(
                    save_id=save_id,
                    item_name=item_name,
                    quantity=quantity
                )
                self.session.add(inventory_item)
        
        self.session.commit()
        
    def load_inventory(self, save_id: int) -> Dict[str, int]:
        """Load inventory for a save."""
        items = (self.session.query(InventoryItem)
                .filter(InventoryItem.save_id == save_id)
                .all())
        
        return {item.item_name: item.quantity for item in items}