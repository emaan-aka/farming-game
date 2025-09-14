"""
UI system for displaying game state, inventory, and tooltips.
"""
import pygame
import pygame_emojis
from typing import Optional
from farming_game.data.data_classes import Position, CellType
from farming_game.data.constants import *
from farming_game.core.game_manager import GameManager

class UI:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.small_font = pygame.font.Font(None, 20)
        self.large_font = pygame.font.Font(None, 32)
    
    def draw_field(self, game_manager: GameManager, selected_item=None):
        field = game_manager.field
        player_pos = game_manager.player.position
        storage = game_manager.storage_system
        
        for y in range(FIELD_HEIGHT):
            for x in range(FIELD_WIDTH):
                cell = field.get_cell(Position(x, y))
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                
                # Draw cell background
                if storage.is_seed_shop_position(x, y):
                    pygame.draw.rect(self.screen, BROWN, rect)
                    self.draw_emoji("🏪", rect.centerx, rect.centery, size=SHOP_EMOJI_SIZE)
                elif storage.is_shipping_position(x, y):
                    pygame.draw.rect(self.screen, GRAY, rect)
                    self.draw_emoji("📫", rect.centerx, rect.centery, size=SHOP_EMOJI_SIZE)
                elif cell.cell_type == CellType.PLANTED:
                    pygame.draw.rect(self.screen, GREEN, rect)
                    self.draw_plant(cell, rect)
                elif cell.cell_type == CellType.FORAGE:
                    pygame.draw.rect(self.screen, BROWN, rect)  # Hide forage items visually
                else:
                    pygame.draw.rect(self.screen, LIGHT_BROWN, rect)
                
                # Draw grid lines
                pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw player
        player_rect = pygame.Rect(player_pos.x * GRID_SIZE, player_pos.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        self.draw_emoji("👩‍🌾", player_rect.centerx, player_rect.centery, size=PLAYER_EMOJI_SIZE)
        
        # Draw held item indicator next to player
        if selected_item:
            item_emoji = self.get_item_emoji(selected_item)
            if item_emoji:
                self.draw_emoji(item_emoji, player_rect.right - 6, player_rect.centery - 10, size=HELD_ITEM_EMOJI_SIZE)
    
    def draw_plant(self, cell, rect):
        if not cell.plant_type:
            return
        
        plant_data = PLANT_REGISTRY.get(cell.plant_type)
        if not plant_data:
            return
        
        # Show different stages
        if cell.growth_stage == 0:
            self.draw_emoji("🌱", rect.centerx, rect.centery, size=PLANT_EMOJI_SIZE)
        elif cell.growth_stage < plant_data.growth_stages - 1:
            self.draw_emoji("🌿", rect.centerx, rect.centery, size=PLANT_EMOJI_SIZE)
        else:
            self.draw_emoji(plant_data.sprite, rect.centerx, rect.centery, size=PLANT_EMOJI_SIZE)
        
        # Show water indicator
        if cell.growth_stage in plant_data.water_requirements and not cell.watered:
            pygame.draw.circle(self.screen, BLUE, (rect.right - 5, rect.top + 5), 3)
    
    def draw_forage(self, cell, rect, forage_system):
        if not cell.forage_item:
            return
        
        forage_data = FORAGE_REGISTRY.get(cell.forage_item)
        if not forage_data:
            return
        
        # Draw forage item
        self.draw_emoji(forage_data.sprite, rect.centerx, rect.centery, size=PLANT_EMOJI_SIZE)
        
        # Draw rarity indicator
        rarity_color = RARITY_COLORS.get(forage_data.rarity, WHITE)
        pygame.draw.rect(self.screen, rarity_color, rect, 2)
    
    def draw_ui_panel(self, game_manager: GameManager):
        panel_rect = pygame.Rect(FIELD_WIDTH * GRID_SIZE, 0, UI_PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, panel_rect)
        pygame.draw.rect(self.screen, BLACK, panel_rect, 2)
        
        y_offset = 10
        
        # Time and day
        time_text = game_manager.get_current_time_string()
        self.draw_text(time_text, panel_rect.x + 10, y_offset, color=BLACK)
        y_offset += 30
        
        # Money
        money_text = f"Money: ${game_manager.player.money}"
        self.draw_text(money_text, panel_rect.x + 10, y_offset, color=BLACK)
        y_offset += 40
        
        # Skip inventory in side panel - will show at bottom instead
        y_offset += 20
        
        # Seed shop info
        self.draw_text("Seed Prices:", panel_rect.x + 10, y_offset, color=BLACK, font=self.large_font)
        y_offset += 30
        
        # Dynamic seed info based on what's available
        seed_info = [
            "Carrot: $1",
            "Tomato: $2", 
            "Melon: $5"
        ]
        
        # Add gigantic pumpkin if unlocked (day 3+)
        if game_manager.game_state.day >= 3:
            seed_info.append("G.Pumpkin: $500")
        
        for info in seed_info:
            self.draw_text(info, panel_rect.x + 10, y_offset, color=BLACK, font=self.small_font)
            y_offset += 18
        
        # Controls help
        y_offset = WINDOW_HEIGHT - 250
        self.draw_text("Controls:", panel_rect.x + 10, y_offset, color=BLACK, font=self.large_font)
        y_offset += 30
        
        controls = [
            "WASD/Arrows: Move",
            "TAB: Select item",
            "Space/P: Plant seed", 
            "E: Water",
            "H: Harvest",
            "F: Forage",
            "B: Buy seeds",
            "X: Ship items",
            "Ctrl+Q: Save",
            "Ctrl+L: Load"
        ]
        
        for control in controls:
            self.draw_text(control, panel_rect.x + 10, y_offset, color=BLACK, font=self.small_font)
            y_offset += 15
    
    def draw_text(self, text: str, x: int, y: int, color=WHITE, center=False, font=None):
        if font is None:
            font = self.font
        
        text_surface = font.render(str(text), True, color)
        if center:
            text_rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, text_rect)
        else:
            self.screen.blit(text_surface, (x, y))
    
    def draw_emoji(self, emoji: str, x: int, y: int, size: int = 24):
        try:
            emoji_surface = pygame_emojis.load_emoji(emoji, size)
            emoji_rect = emoji_surface.get_rect(center=(x, y))
            self.screen.blit(emoji_surface, emoji_rect)
        except (pygame_emojis.EmojiNotFound, FileNotFoundError):
            # Fallback to text if emoji not found
            self.draw_text(emoji, x, y, center=True, font=self.small_font)
    
    def draw_bottom_inventory(self, game_manager: GameManager, selected_item=None):
        # Draw inventory bar at bottom of screen
        inventory_height = 80
        inventory_rect = pygame.Rect(0, WINDOW_HEIGHT - inventory_height, WINDOW_WIDTH, inventory_height)
        pygame.draw.rect(self.screen, WHITE, inventory_rect)
        pygame.draw.rect(self.screen, BLACK, inventory_rect, 2)
        
        y_pos = WINDOW_HEIGHT - inventory_height + 5
        self.draw_text("Inventory:", 10, y_pos, color=BLACK, font=self.font)
        
        # Draw inventory grid - fixed number of slots
        slot_size = 60
        start_x = 120
        max_slots = 8  # Total number of inventory slots
        
        # Create inventory list with empty hands first, then items, then empty slots
        inventory_items = [None]  # Empty hands
        inventory_items.extend(list(game_manager.player.inventory.keys()))
        
        # Fill remaining slots with unique empty placeholders  
        empty_slot_count = 0
        while len(inventory_items) < max_slots:
            inventory_items.append(f"empty_slot_{empty_slot_count}")
            empty_slot_count += 1
        
        # Draw each slot
        for slot_index in range(max_slots):
            slot_x = start_x + slot_index * (slot_size + 5)
            slot_rect = pygame.Rect(slot_x, y_pos + 15, slot_size, slot_size)
            
            item = inventory_items[slot_index] if slot_index < len(inventory_items) else f"empty_slot_{slot_index}"
            
            if item is None:  # Empty hands slot
                slot_color = GRAY
                # Highlight if empty hands is selected
                if selected_item is None:
                    pygame.draw.rect(self.screen, YELLOW, slot_rect)
                    pygame.draw.rect(self.screen, RED, slot_rect, 3)
                else:
                    pygame.draw.rect(self.screen, slot_color, slot_rect)
                    pygame.draw.rect(self.screen, BLACK, slot_rect, 1)
                # Leave blank - no icon
                
            elif item.startswith("empty_slot"):  # Empty inventory slot
                # Highlight if this empty slot is selected
                if selected_item == item:
                    pygame.draw.rect(self.screen, YELLOW, slot_rect)
                    pygame.draw.rect(self.screen, RED, slot_rect, 3)
                else:
                    pygame.draw.rect(self.screen, GRAY, slot_rect)
                    pygame.draw.rect(self.screen, BLACK, slot_rect, 1)
                # Leave blank
                
            else:  # Actual inventory item
                # Use seed color for seeds, light brown for other items
                if item.endswith("_seeds"):
                    slot_color = SEED_COLORS.get(item, LIGHT_BROWN)
                else:
                    slot_color = LIGHT_BROWN
                
                # Highlight if this item is selected
                if selected_item == item:
                    pygame.draw.rect(self.screen, YELLOW, slot_rect)
                    pygame.draw.rect(self.screen, RED, slot_rect, 3)
                else:
                    pygame.draw.rect(self.screen, slot_color, slot_rect)
                    pygame.draw.rect(self.screen, BLACK, slot_rect, 1)
                
                # Draw item content
                emoji = self.get_item_emoji(item)
                if emoji:
                    self.draw_emoji(emoji, slot_x + slot_size//2, y_pos + 30, size=INVENTORY_EMOJI_SIZE)
                    quantity = game_manager.player.inventory.get(item, 0)
                    self.draw_text(str(quantity), slot_x + slot_size - 20, y_pos + 55, color=BLACK, font=self.small_font)
                else:
                    item_abbrev = item[:4] + str(game_manager.player.inventory.get(item, 0))
                    self.draw_text(item_abbrev, slot_x + 2, y_pos + 20, color=BLACK, font=self.small_font)
    
    def get_item_emoji(self, item: str) -> str:
        """Get emoji representation for inventory items"""
        emoji_map = {
            # Seeds - use seed emoji for all seeds
            "carrot_seeds": "🌱",
            "tomato_seeds": "🌱", 
            "melon_seeds": "🌱",
            "gigantic_pumpkin_seeds": "🌱",
            
            # Harvested plants
            "carrot": "🥕",
            "tomato": "🍅",
            "melon": "🍈", 
            "gigantic_pumpkin": "🎃",
            
            # Forage items
            "wild_berries": "🫐",
            "herbs": "🌿",
            "mushrooms": "🍄",
            "flowers": "🌸",
            "crystals": "💎",
            "ancient_coin": "🪙",
            "golden_artifact": "🏆"
        }
        return emoji_map.get(item, "")
    
    def draw_message(self, message: str, duration: int = 2000):
        # Draw temporary message (could be enhanced with timer)
        text_surface = self.font.render(message, True, WHITE)
        text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)