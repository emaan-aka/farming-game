"""
Main game loop and entry point for the farming game - refactored with modules.
"""
import pygame
import sys
from farming_game.data.data_classes import Position, InteractionResult
from farming_game.data.constants import *
from farming_game.core.game_manager import GameManager
from farming_game.ui.renderer import UI

class FarmingGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Farming & Foraging Game")
        self.clock = pygame.time.Clock()
        
        self.game_manager = GameManager()
        self.ui = UI(self.screen)
        self.running = True
        self.message = ""
        self.message_timer = 0
        
        # Available plant types for planting (gigantic_pumpkin unlocked on day 3)
        self.plant_types = ["carrot", "tomato", "melon"]
        self.current_plant_index = 0
        
        # Inventory selection
        self.selected_inventory_item = None
        self.selected_inventory_index = 0
        
        # Movement timing
        self.last_move_time = 0
        self.move_delay = 150  # milliseconds between moves
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keypress(event.key)
        
        # Handle continuous movement with held keys
        self.handle_held_keys()
    
    def handle_held_keys(self):
        """Handle continuous movement when keys are held down"""
        current_time = pygame.time.get_ticks()
        
        # Only move if enough time has passed since last move
        if current_time - self.last_move_time < self.move_delay:
            return
        
        keys = pygame.key.get_pressed()
        player = self.game_manager.player
        moved = False
        
        # Movement with held keys
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            moved = player.move(Position(0, -1))
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            moved = player.move(Position(0, 1))
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            moved = player.move(Position(-1, 0))
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            moved = player.move(Position(1, 0))
        
        # Update last move time if we actually moved
        if moved:
            self.last_move_time = current_time
    
    def handle_keypress(self, key):
        player = self.game_manager.player
        plant_system = self.game_manager.plant_system
        forage_system = self.game_manager.forage_system
        storage = self.game_manager.storage_system
        
        # Inventory selection with TAB
        if key == pygame.K_TAB:
            self.cycle_inventory_selection()
        
        # Actions
        elif key == pygame.K_SPACE or key == pygame.K_p:
            self.plant_seed()
        
        elif key == pygame.K_e:
            self.water_plant()
        
        elif key == pygame.K_h:
            self.harvest_plant()
        
        elif key == pygame.K_f:
            self.forage_item()
        
        elif key == pygame.K_b:
            self.buy_seeds()
        
        elif key == pygame.K_x:
            self.ship_items()
        
        # Save/Load
        elif key == pygame.K_q and pygame.key.get_pressed()[pygame.K_LCTRL]:
            if self.game_manager.save_game():
                self.show_message("Game saved!")
            else:
                self.show_message("Save failed!")
        
        elif key == pygame.K_l and pygame.key.get_pressed()[pygame.K_LCTRL]:
            if self.game_manager.load_game():
                self.show_message("Game loaded!")
            else:
                self.show_message("Load failed!")
    
    def cycle_inventory_selection(self):
        # Create full inventory list with empty hands + items + empty slots
        max_slots = 8
        inventory_slots = [None]  # Empty hands
        inventory_slots.extend(list(self.game_manager.player.inventory.keys()))
        
        # Fill remaining slots with unique empty slot identifiers
        empty_slot_count = 0
        while len(inventory_slots) < max_slots:
            inventory_slots.append(f"empty_slot_{empty_slot_count}")
            empty_slot_count += 1
        
        self.selected_inventory_index = (self.selected_inventory_index + 1) % len(inventory_slots)
        self.selected_inventory_item = inventory_slots[self.selected_inventory_index]
        
        if self.selected_inventory_item is None:
            self.show_message("Empty hands selected")
        elif self.selected_inventory_item.startswith("empty_slot"):
            slot_num = self.selected_inventory_index
            self.show_message(f"Empty slot {slot_num} selected")
        else:
            self.show_message(f"Selected: {self.selected_inventory_item}")
    
    def plant_seed(self):
        # Only plant if holding seeds
        if not self.selected_inventory_item or not self.selected_inventory_item.endswith("_seeds"):
            self.show_message("Select seeds first!")
            return
        
        plant_type = self.selected_inventory_item.replace("_seeds", "")
        result = self.game_manager.plant_system.plant_seed(
            self.game_manager.player, 
            self.game_manager.player.position, 
            plant_type
        )
        
        if result == InteractionResult.SUCCESS:
            self.show_message(f"Planted {plant_type}!")
        elif result == InteractionResult.NO_SEEDS:
            self.show_message(f"No {self.selected_inventory_item}!")
        elif result == InteractionResult.NO_MONEY:
            self.show_message("Not enough money!")
        elif result == InteractionResult.ALREADY_PLANTED:
            self.show_message("Already planted here!")
    
    def water_plant(self):
        result = self.game_manager.plant_system.water_plant(self.game_manager.player.position)
        
        if result == InteractionResult.SUCCESS:
            self.show_message("Plant watered!")
        else:
            self.show_message("Nothing to water here!")
    
    def harvest_plant(self):
        result = self.game_manager.plant_system.harvest_plant(
            self.game_manager.player, 
            self.game_manager.player.position
        )
        
        if result == InteractionResult.SUCCESS:
            self.show_message("Harvested!")
        elif result == InteractionResult.NOT_READY:
            self.show_message("Plant not ready!")
        else:
            self.show_message("Nothing to harvest!")
    
    def forage_item(self):
        result = self.game_manager.forage_system.forage_item(
            self.game_manager.player, 
            self.game_manager.player.position
        )
        
        if result == InteractionResult.SUCCESS:
            self.show_message("Foraged item!")
        else:
            self.show_message("Nothing to forage!")
    
    def buy_seeds(self):
        pos = self.game_manager.player.position
        if not self.game_manager.storage_system.is_seed_shop_position(pos.x, pos.y):
            self.show_message("No seed shop here!")
            return
        
        # Buy based on selected inventory item or show menu
        if self.selected_inventory_item and self.selected_inventory_item.endswith("_seeds"):
            plant_type = self.selected_inventory_item.replace("_seeds", "")
            result = self.game_manager.storage_system.buy_seeds(
                self.game_manager.player, plant_type, 1
            )
            
            if result == InteractionResult.SUCCESS:
                self.show_message(f"Bought {plant_type} seeds!")
            elif result == InteractionResult.NO_MONEY:
                plant_data = PLANT_REGISTRY.get(plant_type)
                cost = plant_data.seed_cost if plant_data else 0
                self.show_message(f"Need ${cost} for {plant_type} seeds!")
            else:
                self.show_message("Can't buy seeds!")
        else:
            # Show available seeds to buy
            available_plants = self.plant_types.copy()
            if len(available_plants) > 0:
                # Buy first available plant type as default
                plant_type = available_plants[0]
                result = self.game_manager.storage_system.buy_seeds(
                    self.game_manager.player, plant_type, 1
                )
                
                if result == InteractionResult.SUCCESS:
                    self.show_message(f"Bought {plant_type} seeds!")
                elif result == InteractionResult.NO_MONEY:
                    plant_data = PLANT_REGISTRY.get(plant_type)
                    cost = plant_data.seed_cost if plant_data else 0
                    self.show_message(f"Need ${cost} for {plant_type} seeds!")
                else:
                    self.show_message("Can't buy seeds!")
    
    def ship_items(self):
        pos = self.game_manager.player.position
        if not self.game_manager.storage_system.is_shipping_position(pos.x, pos.y):
            self.show_message("No shipping container here!")
            return
        
        earnings = self.game_manager.storage_system.ship_items(self.game_manager.player)
        if earnings > 0:
            self.show_message(f"Shipped items for ${earnings}!")
        else:
            self.show_message("Nothing to ship!")
    
    def show_message(self, text: str):
        self.message = text
        self.message_timer = pygame.time.get_ticks() + 2000  # Show for 2 seconds
    
    def update(self, delta_time):
        self.game_manager.update(delta_time)
        
        # Update message timer
        if self.message_timer > 0 and pygame.time.get_ticks() > self.message_timer:
            self.message = ""
            self.message_timer = 0
        
        # Unlock gigantic pumpkin on day 3
        if (self.game_manager.game_state.day >= 3 and 
            "gigantic_pumpkin" not in self.plant_types):
            self.plant_types.append("gigantic_pumpkin")
            self.show_message("Gigantic Pumpkin seeds unlocked!")
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game elements
        self.ui.draw_field(self.game_manager, self.selected_inventory_item)
        self.ui.draw_ui_panel(self.game_manager)
        self.ui.draw_bottom_inventory(self.game_manager, self.selected_inventory_item)
        
        # Draw message if active
        if self.message:
            self.ui.draw_message(self.message)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            delta_time = self.clock.tick(FPS) / 1000.0  # Convert to seconds
            
            self.handle_events()
            self.update(delta_time)
            self.draw()
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = FarmingGame()
    game.run()