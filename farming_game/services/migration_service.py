"""
Migration service for converting JSON saves to SQLite database.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from farming_game.services.player_service import PlayerService
from farming_game.services.save_service import SaveService
from farming_game.data.data_classes import CellState, CellType

class MigrationService:
    """Service for migrating JSON saves to SQLite database."""
    
    def __init__(self):
        self.player_service = PlayerService()
        self.save_service = SaveService()
    
    def find_json_saves(self, directory: str = ".") -> List[str]:
        """Find all JSON save files in directory."""
        json_files = []
        for file_path in Path(directory).glob("*.json"):
            if self.is_valid_save_file(str(file_path)):
                json_files.append(str(file_path))
        return json_files
    
    def is_valid_save_file(self, file_path: str) -> bool:
        """Check if file is a valid game save."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check for required structure
            return (
                "game_state" in data and 
                "field_state" in data and
                "day" in data.get("game_state", {})
            )
        except (json.JSONDecodeError, FileNotFoundError):
            return False
    
    def migrate_json_save(self, json_file_path: str, player_username: str, save_name: str = None) -> bool:
        """Migrate a single JSON save to database."""
        try:
            # Load JSON data
            with open(json_file_path, 'r') as f:
                save_data = json.load(f)
            
            # Get or create player
            player = self.player_service.get_player(player_username)
            if not player:
                player = self.player_service.create_player(player_username)
                if not player:
                    print(f"Failed to create player: {player_username}")
                    return False
            
            player_id = player['id']
            
            # Extract game state data
            game_state_data = self.extract_game_state(save_data)
            
            # Create save name if not provided
            if not save_name:
                save_name = f"Migrated Save - Day {game_state_data.get('day', 1)}"
            
            # Convert field state to CellState objects
            field_cells = self.convert_field_state(save_data.get("field_state", []))\n            \n            # Extract inventory\n            inventory = save_data.get("game_state", {}).get("inventory", {})\n            \n            # Create game state object for service\n            from farming_game.data.data_classes import GameState, Position\n            game_state = GameState(\n                day=game_state_data['day'],\n                time_minutes=game_state_data['time_minutes'],\n                player_pos=Position(game_state_data['player_pos_x'], game_state_data['player_pos_y']),\n                player_money=game_state_data['player_money'],\n                inventory=inventory\n            )\n            \n            # Save to database\n            success = self.save_service.save_game_state(\n                player_id=player_id,\n                save_name=save_name,\n                game_state=game_state,\n                player_money=game_state_data['player_money'],\n                inventory=inventory,\n                field_cells=field_cells\n            )\n            \n            if success:\n                print(f"Successfully migrated {json_file_path} for player {player_username}")\n                return True\n            else:\n                print(f"Failed to save migrated data for {json_file_path}")\n                return False\n                \n        except Exception as e:\n            print(f"Migration failed for {json_file_path}: {e}")\n            return False\n    \n    def extract_game_state(self, save_data: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Extract and normalize game state data from JSON.\"\"\"\n        game_state = save_data.get("game_state", {})\n        \n        # Extract player position\n        player_pos = game_state.get("player_pos", {"x": 9, "y": 7})\n        \n        return {\n            'day': game_state.get("day", 1),\n            'time_minutes': int(game_state.get("time_minutes", 0)),\n            'player_pos_x': player_pos.get("x", 9),\n            'player_pos_y': player_pos.get("y", 7),\n            'player_money': game_state.get("player_money", 100)\n        }\n    \n    def convert_field_state(self, field_data: List[List[Dict]]) -> List[List[CellState]]:\n        \"\"\"Convert JSON field data to CellState objects.\"\"\"\n        if not field_data:\n            # Initialize empty field\n            from farming_game.data.constants import FIELD_WIDTH, FIELD_HEIGHT\n            return [[CellState() for _ in range(FIELD_WIDTH)] for _ in range(FIELD_HEIGHT)]\n        \n        field_cells = []\n        for row_data in field_data:\n            row_cells = []\n            for cell_data in row_data:\n                cell = CellState(\n                    cell_type=CellType(cell_data.get("cell_type", "empty")),\n                    plant_type=cell_data.get("plant_type"),\n                    growth_stage=cell_data.get("growth_stage", 0),\n                    watered=cell_data.get("watered", False),\n                    forage_item=cell_data.get("forage_item"),\n                    forage_spawn_time=cell_data.get("forage_spawn_time", 0),\n                    plant_timer=cell_data.get("plant_timer", 0)\n                )\n                row_cells.append(cell)\n            field_cells.append(row_cells)\n        \n        return field_cells\n    \n    def migrate_all_json_saves(self, directory: str = ".", default_username: str = "Player1") -> Dict[str, Any]:\n        \"\"\"Migrate all JSON saves in directory.\"\"\"\n        json_files = self.find_json_saves(directory)\n        results = {\n            'total_files': len(json_files),\n            'successful': 0,\n            'failed': 0,\n            'files': []\n        }\n        \n        for i, json_file in enumerate(json_files):\n            print(f"Migrating {json_file} ({i+1}/{len(json_files)})...")\n            \n            # Generate save name from filename\n            filename = Path(json_file).stem\n            save_name = f"Migrated - {filename}"\n            \n            success = self.migrate_json_save(json_file, default_username, save_name)\n            \n            results['files'].append({\n                'file': json_file,\n                'success': success,\n                'save_name': save_name\n            })\n            \n            if success:\n                results['successful'] += 1\n            else:\n                results['failed'] += 1\n        \n        return results\n    \n    def backup_json_file(self, json_file_path: str) -> str:\n        \"\"\"Create backup of JSON file before migration.\"\"\"\n        backup_path = f"{json_file_path}.backup"\n        \n        try:\n            import shutil\n            shutil.copy2(json_file_path, backup_path)\n            return backup_path\n        except Exception as e:\n            print(f"Failed to backup {json_file_path}: {e}")\n            return None\n    \n    def close(self):\n        \"\"\"Clean up resources.\"\"\"\n        self.player_service.close()\n        self.save_service.close()\n\ndef run_migration_tool():\n    \"\"\"Interactive migration tool.\"\"\"\n    print("=== JSON to SQLite Migration Tool ===\")\n    print()\n    \n    migration_service = MigrationService()\n    \n    try:\n        # Find JSON files\n        json_files = migration_service.find_json_saves(".")\n        \n        if not json_files:\n            print("No JSON save files found in current directory.")\n            return\n        \n        print(f"Found {len(json_files)} JSON save files:\")\n        for i, file_path in enumerate(json_files):\n            print(f\"  {i+1}. {file_path}\")\n        print()\n        \n        # Get player username\n        username = input("Enter username for migrated saves (default: Player1): \").strip()\n        if not username:\n            username = "Player1"\n        \n        # Confirm migration\n        print(f\"This will migrate all {len(json_files)} saves to player '{username}'\")\n        confirm = input("Continue? (y/N): \").strip().lower()\n        \n        if confirm != 'y':\n            print("Migration cancelled.")\n            return\n        \n        # Run migration\n        print(\"\\nStarting migration...\")\n        results = migration_service.migrate_all_json_saves(\".\", username)\n        \n        # Report results\n        print(f\"\\nMigration complete!\")\n        print(f\"Total files: {results['total_files']}\")\n        print(f\"Successful: {results['successful']}\")\n        print(f\"Failed: {results['failed']}\")\n        \n        if results['failed'] > 0:\n            print(\"\\nFailed files:\")\n            for file_info in results['files']:\n                if not file_info['success']:\n                    print(f\"  - {file_info['file']}\")\n        \n        print(f\"\\nMigrated saves are now available for player '{username}' in the database.\")\n        \n    finally:\n        migration_service.close()\n\nif __name__ == \"__main__\":\n    run_migration_tool()