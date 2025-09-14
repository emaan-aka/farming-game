"""
Game manager for day/night cycles, time management, and game state coordination.
"""
import json
from typing import Dict, Any
from farming_game.data.data_classes import GameState, Position, CellState
from farming_game.data.constants import GAME_DAY_LENGTH, MINUTES_PER_SECOND, FIELD_WIDTH, FIELD_HEIGHT
from farming_game.core.player import Player
from farming_game.core.field import Field
from farming_game.systems.plants import PlantSystem
from farming_game.systems.forage import ForageSystem
from farming_game.systems.storage import StorageSystem

class GameManager:
    def __init__(self):
        self.game_state = GameState()
        self.player = Player(self.game_state.player_pos)
        self.field = Field()
        self.plant_system = PlantSystem(self.field)
        self.forage_system = ForageSystem(self.field)
        self.storage_system = StorageSystem()
        self.last_update_time = 0
        
        # Initialize field state in game_state
        self.sync_game_state()
    
    def sync_game_state(self):
        self.game_state.player_pos = self.player.position
        self.game_state.player_money = self.player.money
        self.game_state.inventory = self.player.inventory.copy()
        self.game_state.field_state = self.field.get_all_cells()
        # No chest contents to sync anymore
    
    def update(self, delta_time: float):
        # Update game time (delta_time is in seconds, convert to game minutes)
        time_increment = delta_time * MINUTES_PER_SECOND
        self.game_state.time_minutes += time_increment
        
        # Check for new day
        if self.game_state.time_minutes >= GAME_DAY_LENGTH:
            self.advance_day()
        
        # Update plant growth (once per second approximately)
        current_second = int(self.game_state.time_minutes)
        if current_second != self.last_update_time:
            self.plant_system.update_plant_growth(current_second)
            self.field.update_forage_spawns(current_second)
            self.last_update_time = current_second
        
        # Sync game state
        self.sync_game_state()
    
    def advance_day(self):
        # Ship all items from player inventory at end of day
        earnings = self.storage_system.ship_items(self.player)
        
        # Reset day
        self.game_state.day += 1
        self.game_state.time_minutes = 0
        
        print(f"Day {self.game_state.day - 1} complete! Earned ${earnings} from shipping.")
        
        # Check win condition
        if self.check_win_condition():
            print("Congratulations! You've grown a gigantic pumpkin and won the game!")
    
    def check_win_condition(self) -> bool:
        for row in self.field.cells:
            for cell in row:
                if (cell.plant_type == "gigantic_pumpkin" and 
                    cell.growth_stage >= 6):  # Fully grown gigantic pumpkin
                    return True
        return False
    
    def get_current_time_string(self) -> str:
        return self.game_state.get_time_string()
    
    def save_game(self, filename: str = "savegame.json"):
        save_data = {
            "game_state": {
                "day": self.game_state.day,
                "time_minutes": self.game_state.time_minutes,
                "player_pos": {"x": self.player.position.x, "y": self.player.position.y},
                "player_money": self.player.money,
                "inventory": self.player.inventory,
                # No chest contents to save
            },
            "field_state": []
        }
        
        # Save field state
        for y in range(FIELD_HEIGHT):
            row = []
            for x in range(FIELD_WIDTH):
                cell = self.field.cells[y][x]
                row.append({
                    "cell_type": cell.cell_type.value,
                    "plant_type": cell.plant_type,
                    "growth_stage": cell.growth_stage,
                    "watered": cell.watered,
                    "forage_item": cell.forage_item,
                    "forage_spawn_time": cell.forage_spawn_time,
                    "plant_timer": cell.plant_timer
                })
            save_data["field_state"].append(row)
        
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
            print(f"Game saved to {filename}")
            return True
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False
    
    def load_game(self, filename: str = "savegame.json") -> bool:
        try:
            with open(filename, 'r') as f:
                save_data = json.load(f)
            
            # Load game state
            gs = save_data["game_state"]
            self.game_state.day = gs["day"]
            self.game_state.time_minutes = gs["time_minutes"]
            self.player.position = Position(gs["player_pos"]["x"], gs["player_pos"]["y"])
            self.player.money = gs["player_money"]
            self.player.inventory = gs["inventory"]
            # No chest contents to load
            
            # Load field state
            from farming_game.data.data_classes import CellType
            for y in range(FIELD_HEIGHT):
                for x in range(FIELD_WIDTH):
                    if y < len(save_data["field_state"]) and x < len(save_data["field_state"][y]):
                        cell_data = save_data["field_state"][y][x]
                        cell = self.field.cells[y][x]
                        cell.cell_type = CellType(cell_data["cell_type"])
                        cell.plant_type = cell_data["plant_type"]
                        cell.growth_stage = cell_data["growth_stage"]
                        cell.watered = cell_data["watered"]
                        cell.forage_item = cell_data["forage_item"]
                        cell.forage_spawn_time = cell_data["forage_spawn_time"]
                        cell.plant_timer = cell_data["plant_timer"]
            
            print(f"Game loaded from {filename}")
            return True
        except Exception as e:
            print(f"Failed to load game: {e}")
            return False