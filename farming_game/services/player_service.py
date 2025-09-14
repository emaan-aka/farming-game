"""
Player service for managing player accounts and authentication.
"""
from typing import List, Optional
from farming_game.database.repository import PlayerRepository
from farming_game.database.database import get_session

class PlayerService:
    """Service for managing player accounts."""
    
    def __init__(self):
        self.session = get_session()
        self.player_repo = PlayerRepository(self.session)
    
    def create_player(self, username: str) -> Optional[dict]:
        """Create a new player account."""
        # Check if username already exists
        existing_player = self.player_repo.get_player_by_username(username)
        if existing_player:
            return None  # Username already taken
        
        try:
            player = self.player_repo.create_player(username)
            return {
                'id': player.id,
                'username': player.username,
                'created_at': player.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Failed to create player: {e}")
            return None
    
    def get_player(self, username: str) -> Optional[dict]:
        """Get player by username."""
        player = self.player_repo.get_player_by_username(username)
        if player:
            return {
                'id': player.id,
                'username': player.username,
                'created_at': player.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_played': player.last_played.strftime('%Y-%m-%d %H:%M:%S') if player.last_played else None
            }
        return None
    
    def get_player_by_id(self, player_id: int) -> Optional[dict]:
        """Get player by ID."""
        player = self.player_repo.get_player_by_id(player_id)
        if player:
            return {
                'id': player.id,
                'username': player.username,
                'created_at': player.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'last_played': player.last_played.strftime('%Y-%m-%d %H:%M:%S') if player.last_played else None
            }
        return None
    
    def list_players(self) -> List[dict]:
        """List all players."""
        players = self.player_repo.get_all_players()
        return [{
            'id': player.id,
            'username': player.username,
            'last_played': player.last_played.strftime('%Y-%m-%d %H:%M:%S') if player.last_played else 'Never'
        } for player in players]
    
    def validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and availability."""
        if not username or len(username.strip()) == 0:
            return False, "Username cannot be empty"
        
        username = username.strip()
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        
        # Check for invalid characters (allow alphanumeric, spaces, underscores, hyphens)
        if not all(c.isalnum() or c in ' _-' for c in username):
            return False, "Username can only contain letters, numbers, spaces, underscores, and hyphens"
        
        # Check availability
        if self.player_repo.get_player_by_username(username):
            return False, "Username already taken"
        
        return True, "Username is valid"
    
    def close(self):
        """Close database session."""
        self.session.close()