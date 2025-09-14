"""
Player character implementation with movement and inventory management.
"""
from typing import Dict
from farming_game.data.data_classes import Position, InteractionResult
from farming_game.data.constants import FIELD_WIDTH, FIELD_HEIGHT

class Player:
    def __init__(self, start_pos: Position):
        self.position = start_pos
        self.inventory: Dict[str, int] = {"carrot_seeds": 3, "tomato_seeds": 2}
        self.money = 20
    
    def move(self, direction: Position) -> bool:
        new_pos = self.position + direction
        if 0 <= new_pos.x < FIELD_WIDTH and 0 <= new_pos.y < FIELD_HEIGHT:
            self.position = new_pos
            return True
        return False
    
    def add_item(self, item: str, quantity: int = 1) -> bool:
        if item in self.inventory:
            self.inventory[item] += quantity
        else:
            self.inventory[item] = quantity
        return True
    
    def remove_item(self, item: str, quantity: int = 1) -> bool:
        if item in self.inventory and self.inventory[item] >= quantity:
            self.inventory[item] -= quantity
            if self.inventory[item] == 0:
                del self.inventory[item]
            return True
        return False
    
    def has_item(self, item: str, quantity: int = 1) -> bool:
        return item in self.inventory and self.inventory[item] >= quantity
    
    def add_money(self, amount: int):
        self.money += amount
    
    def spend_money(self, amount: int) -> bool:
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def get_seed_for_plant(self, plant_type: str) -> str:
        return f"{plant_type}_seeds"