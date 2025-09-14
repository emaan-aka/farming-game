"""
Database connection and initialization for the farming game.
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from farming_game.database.models import Base

class Database:
    """Database connection manager."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to a 'data' directory in the project root
            project_root = Path(__file__).parent.parent.parent
            data_dir = project_root / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "farming_game.db")
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def initialize(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
        
    def close(self):
        """Close database connection."""
        self.engine.dispose()

# Global database instance
_db_instance = None

def get_database() -> Database:
    """Get the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.initialize()
    return _db_instance

def get_session() -> Session:
    """Get a new database session (convenience function)."""
    return get_database().get_session()