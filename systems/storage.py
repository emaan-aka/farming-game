"""
Storage system with chest and shipping container mechanics.
"""
from typing import Dict
from ..data.data_classes import InteractionResult
from ..data.constants import PLANT_REGISTRY, FORAGE_REGISTRY
from ..core.player import Player

class StorageSystem:
    def __init__(self):
        self.seed_shop_position = (16, 2)  # Fixed position for seed shop
        self.shipping_position = (16, 4)  # Fixed position for shipping container
    
    def buy_seeds(self, player: Player, plant_type: str, quantity: int = 1) -> InteractionResult:
        if plant_type not in PLANT_REGISTRY:
            return InteractionResult.NOT_POSSIBLE
        
        plant_data = PLANT_REGISTRY[plant_type]
        total_cost = plant_data.seed_cost * quantity
        
        if not player.spend_money(total_cost):
            return InteractionResult.NO_MONEY
        
        seed_name = f"{plant_type}_seeds"
        player.add_item(seed_name, quantity)
        return InteractionResult.SUCCESS
    
    def ship_items(self, player: Player) -> int:
        """Ship all non-seed items from player inventory"""
        total_value = 0
        items_to_remove = []
        
        for item, quantity in player.inventory.items():
            if not item.endswith("_seeds"):  # Don't ship seeds
                item_value = self.get_item_value(item)
                if item_value > 0:
                    total_value += item_value * quantity
                    items_to_remove.append(item)
        
        # Remove shipped items
        for item in items_to_remove:
            del player.inventory[item]
        
        player.add_money(total_value)
        return total_value
    
    def get_item_value(self, item: str) -> int:
        # Check if it's a plant product
        if item in PLANT_REGISTRY:
            return PLANT_REGISTRY[item].sell_price
        
        # Check if it's a forage item
        if item in FORAGE_REGISTRY:
            return FORAGE_REGISTRY[item].sell_price
        
        return 0
    
    def is_seed_shop_position(self, x: int, y: int) -> bool:
        return (x, y) == self.seed_shop_position
    
    def is_shipping_position(self, x: int, y: int) -> bool:
        return (x, y) == self.shipping_position