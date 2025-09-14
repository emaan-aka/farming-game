"""
Player character implementation with movement and inventory management.
"""
from typing import Dict
from farming_game.data.data_classes import Position
from farming_game.data.constants import FIELD_WIDTH, FIELD_HEIGHT, DEFAULT_STARTING_MONEY, DEFAULT_STARTING_SEEDS

class Player:
    def __init__(self, start_pos: Position):
        self.position = start_pos
        self.inventory: Dict[str, int] = DEFAULT_STARTING_SEEDS.copy()
        self.money = DEFAULT_STARTING_MONEY
    
    def move(self, direction: Position) -> bool:
        """Move player in given direction if within field bounds."""
        new_pos = self.position + direction
        if 0 <= new_pos.x < FIELD_WIDTH and 0 <= new_pos.y < FIELD_HEIGHT:
            self.position = new_pos
            return True
        return False
    
    def add_item(self, item: str, quantity: int = 1) -> bool:
        """Add item to inventory."""
        if quantity <= 0:
            return False
        self.inventory[item] = self.inventory.get(item, 0) + quantity
        return True
    
    def remove_item(self, item: str, quantity: int = 1) -> bool:
        """Remove item from inventory if available."""
        if quantity <= 0 or not self.has_item(item, quantity):
            return False
        self.inventory[item] -= quantity
        if self.inventory[item] == 0:
            del self.inventory[item]
        return True
    
    def has_item(self, item: str, quantity: int = 1) -> bool:
        """Check if player has enough of an item."""
        return self.inventory.get(item, 0) >= quantity
    
    def add_money(self, amount: int) -> None:
        """Add money to player's funds."""
        if amount > 0:
            self.money += amount
    
    def spend_money(self, amount: int) -> bool:
        """Spend money if player has enough."""
        if amount <= 0 or self.money < amount:
            return False
        self.money -= amount
        return True
    
    def get_seed_for_plant(self, plant_type: str) -> str:
        """Get seed name for a given plant type."""
        return f"{plant_type}_seeds"