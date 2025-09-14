"""
Player selection and management UI.
"""
import pygame
from typing import Optional, List, Dict, Any
from farming_game.data.constants import *
from farming_game.services.player_service import PlayerService

class PlayerSelectionUI:
    """UI for selecting/creating players and managing saves."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.large_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 20)
        
        self.player_service = PlayerService()
        self.selected_player_id = None
        self.selected_save_id = None
        
        # UI state
        self.mode = "player_select"  # player_select, create_player, save_select
        self.players = []
        self.saves = []
        self.selected_index = 0
        self.input_text = ""
        self.message = ""
        self.message_timer = 0
        
        # Load players
        self.refresh_players()
    
    def refresh_players(self):
        """Refresh the player list."""
        self.players = self.player_service.list_players()
        
    def refresh_saves(self, player_id: int):
        """Refresh saves for selected player."""
        from farming_game.services.save_service import SaveService
        save_service = SaveService()
        self.saves = save_service.get_player_saves(player_id)
        save_service.close()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[Dict[str, Any]]:
        """Handle UI events. Returns selected player/save or None."""
        if event.type == pygame.KEYDOWN:
            if self.mode == "player_select":
                return self.handle_player_select_keys(event.key)
            elif self.mode == "create_player":
                return self.handle_create_player_keys(event.key)
            elif self.mode == "save_select":
                return self.handle_save_select_keys(event.key)
        return None
    
    def handle_player_select_keys(self, key: int) -> Optional[Dict[str, Any]]:
        """Handle keys in player selection mode."""
        if key == pygame.K_UP and self.selected_index > 0:
            self.selected_index -= 1
        elif key == pygame.K_DOWN and self.selected_index < len(self.players):
            self.selected_index += 1
        elif key == pygame.K_RETURN:
            if self.selected_index < len(self.players):
                # Select existing player
                player = self.players[self.selected_index]
                self.selected_player_id = player['id']
                self.refresh_saves(player['id'])
                self.mode = "save_select"
                self.selected_index = 0
            else:
                # Create new player
                self.mode = "create_player"
                self.input_text = ""
                self.message = ""
        elif key == pygame.K_ESCAPE:
            return {"action": "quit"}
        
        return None
    
    def handle_create_player_keys(self, key: int) -> Optional[Dict[str, Any]]:
        """Handle keys in create player mode."""
        if key == pygame.K_RETURN:
            if self.input_text.strip():
                valid, message = self.player_service.validate_username(self.input_text.strip())
                if valid:
                    player = self.player_service.create_player(self.input_text.strip())
                    if player:
                        self.refresh_players()
                        self.mode = "player_select"
                        self.selected_index = 0
                        self.input_text = ""
                        self.show_message(f"Player '{player['username']}' created!")
                    else:
                        self.show_message("Failed to create player!")
                else:
                    self.show_message(message)
        elif key == pygame.K_ESCAPE:
            self.mode = "player_select"
            self.input_text = ""
            self.message = ""
        elif key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]
        else:
            # Add character if printable
            char = pygame.key.name(key)
            if len(char) == 1 and char.isprintable():
                if pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]:
                    char = char.upper()
                self.input_text += char
            elif key == pygame.K_SPACE:
                self.input_text += " "
        
        return None
    
    def handle_save_select_keys(self, key: int) -> Optional[Dict[str, Any]]:
        """Handle keys in save selection mode."""
        if key == pygame.K_UP and self.selected_index > 0:
            self.selected_index -= 1
        elif key == pygame.K_DOWN and self.selected_index <= len(self.saves):
            self.selected_index += 1
        elif key == pygame.K_RETURN:
            if self.selected_index < len(self.saves):
                # Load existing save
                save = self.saves[self.selected_index]
                return {
                    "action": "load_save",
                    "player_id": self.selected_player_id,
                    "save_id": save['id']
                }
            else:
                # Start new game
                return {
                    "action": "new_game",
                    "player_id": self.selected_player_id
                }
        elif key == pygame.K_ESCAPE:
            self.mode = "player_select"
            self.selected_index = 0
        elif key == pygame.K_DELETE and self.selected_index < len(self.saves):
            # Delete save
            save = self.saves[self.selected_index]
            from farming_game.services.save_service import SaveService
            save_service = SaveService()
            if save_service.delete_save(save['id']):\n                self.refresh_saves(self.selected_player_id)\n                self.show_message(f\"Save '{save['name']}' deleted!\")\n                if self.selected_index >= len(self.saves):\n                    self.selected_index = max(0, len(self.saves) - 1)\n            save_service.close()\n        \n        return None\n    \n    def show_message(self, text: str):\n        \"\"\"Show a temporary message.\"\"\"\n        self.message = text\n        self.message_timer = pygame.time.get_ticks() + MESSAGE_DISPLAY_TIME\n    \n    def update(self):\n        \"\"\"Update UI state.\"\"\"\n        # Clear message after timer\n        if self.message_timer > 0 and pygame.time.get_ticks() > self.message_timer:\n            self.message = \"\"\n            self.message_timer = 0\n    \n    def draw(self):\n        \"\"\"Draw the UI.\"\"\"\n        self.screen.fill(BLACK)\n        \n        if self.mode == \"player_select\":\n            self.draw_player_select()\n        elif self.mode == \"create_player\":\n            self.draw_create_player()\n        elif self.mode == \"save_select\":\n            self.draw_save_select()\n        \n        # Draw message if active\n        if self.message:\n            self.draw_message()\n        \n        pygame.display.flip()\n    \n    def draw_player_select(self):\n        \"\"\"Draw player selection screen.\"\"\"\n        title = \"Select Player\"\n        title_surface = self.large_font.render(title, True, WHITE)\n        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))\n        self.screen.blit(title_surface, title_rect)\n        \n        y_start = 120\n        line_height = 40\n        \n        # Draw players\n        for i, player in enumerate(self.players):\n            y = y_start + i * line_height\n            color = YELLOW if i == self.selected_index else WHITE\n            \n            text = f\"{player['username']} (Last played: {player['last_played']})\"\n            text_surface = self.font.render(text, True, color)\n            self.screen.blit(text_surface, (50, y))\n        \n        # Draw \"Create New Player\" option\n        y = y_start + len(self.players) * line_height\n        color = YELLOW if self.selected_index == len(self.players) else WHITE\n        text_surface = self.font.render(\"Create New Player\", True, color)\n        self.screen.blit(text_surface, (50, y))\n        \n        # Instructions\n        instructions = [\n            \"Use UP/DOWN arrows to navigate\",\n            \"Press ENTER to select\",\n            \"Press ESC to quit\"\n        ]\n        \n        y_start = WINDOW_HEIGHT - 120\n        for i, instruction in enumerate(instructions):\n            text_surface = self.small_font.render(instruction, True, WHITE)\n            self.screen.blit(text_surface, (50, y_start + i * 25))\n    \n    def draw_create_player(self):\n        \"\"\"Draw create player screen.\"\"\"\n        title = \"Create New Player\"\n        title_surface = self.large_font.render(title, True, WHITE)\n        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))\n        self.screen.blit(title_surface, title_rect)\n        \n        # Input field\n        prompt = \"Enter username:\"\n        prompt_surface = self.font.render(prompt, True, WHITE)\n        self.screen.blit(prompt_surface, (50, 150))\n        \n        # Text input box\n        input_rect = pygame.Rect(50, 180, 400, 30)\n        pygame.draw.rect(self.screen, WHITE, input_rect, 2)\n        \n        input_surface = self.font.render(self.input_text, True, WHITE)\n        self.screen.blit(input_surface, (55, 185))\n        \n        # Cursor\n        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor\n            cursor_x = 55 + input_surface.get_width()\n            pygame.draw.line(self.screen, WHITE, (cursor_x, 185), (cursor_x, 205))\n        \n        # Instructions\n        instructions = [\n            \"Press ENTER to create player\",\n            \"Press ESC to go back\",\n            \"Username: 3-50 characters, letters/numbers/spaces/_/-\"\n        ]\n        \n        y_start = WINDOW_HEIGHT - 120\n        for i, instruction in enumerate(instructions):\n            text_surface = self.small_font.render(instruction, True, WHITE)\n            self.screen.blit(text_surface, (50, y_start + i * 25))\n    \n    def draw_save_select(self):\n        \"\"\"Draw save selection screen.\"\"\"\n        title = \"Select Save File\"\n        title_surface = self.large_font.render(title, True, WHITE)\n        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))\n        self.screen.blit(title_surface, title_rect)\n        \n        y_start = 120\n        line_height = 50\n        \n        # Draw saves\n        for i, save in enumerate(self.saves):\n            y = y_start + i * line_height\n            color = YELLOW if i == self.selected_index else WHITE\n            \n            name_text = f\"{save['name']}\"\n            details_text = f\"Day {save['day']}, ${save['money']}, {save['last_played']}\"\n            \n            name_surface = self.font.render(name_text, True, color)\n            details_surface = self.small_font.render(details_text, True, GRAY)\n            \n            self.screen.blit(name_surface, (50, y))\n            self.screen.blit(details_surface, (50, y + 20))\n        \n        # Draw \"New Game\" option\n        y = y_start + len(self.saves) * line_height\n        color = YELLOW if self.selected_index == len(self.saves) else WHITE\n        text_surface = self.font.render(\"Start New Game\", True, color)\n        self.screen.blit(text_surface, (50, y))\n        \n        # Instructions\n        instructions = [\n            \"Use UP/DOWN arrows to navigate\",\n            \"Press ENTER to select\",\n            \"Press DELETE to delete save\",\n            \"Press ESC to go back\"\n        ]\n        \n        y_start = WINDOW_HEIGHT - 140\n        for i, instruction in enumerate(instructions):\n            text_surface = self.small_font.render(instruction, True, WHITE)\n            self.screen.blit(text_surface, (50, y_start + i * 25))\n    \n    def draw_message(self):\n        \"\"\"Draw message overlay.\"\"\"\n        message_surface = self.font.render(self.message, True, WHITE)\n        message_rect = message_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))\n        \n        # Draw background\n        bg_rect = message_rect.inflate(20, 10)\n        pygame.draw.rect(self.screen, BLACK, bg_rect)\n        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)\n        \n        self.screen.blit(message_surface, message_rect)\n    \n    def close(self):\n        \"\"\"Clean up resources.\"\"\"\n        self.player_service.close()