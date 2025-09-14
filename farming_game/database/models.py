"""
SQLAlchemy ORM models for the farming game database.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Player(Base):
    """Player profile and authentication."""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_played = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    saves = relationship("GameSave", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player(id={self.id}, username='{self.username}')>"

class GameSave(Base):
    """Game save data - one record per save file."""
    __tablename__ = 'game_saves'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    save_name = Column(String(100), nullable=False)  # e.g., "My Farm", "Save Slot 1"
    
    # Game state data
    day = Column(Integer, default=1)
    time_minutes = Column(Integer, default=0)
    player_pos_x = Column(Integer, default=9)
    player_pos_y = Column(Integer, default=7)
    player_money = Column(Integer, default=100)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="saves")
    field_cells = relationship("FieldCell", back_populates="save", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="save", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GameSave(id={self.id}, player_id={self.player_id}, save_name='{self.save_name}', day={self.day})>"

class FieldCell(Base):
    """Field cell state - only stores non-empty cells for efficiency."""
    __tablename__ = 'field_cells'
    
    id = Column(Integer, primary_key=True)
    save_id = Column(Integer, ForeignKey('game_saves.id'), nullable=False)
    
    # Position
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    
    # Cell state
    cell_type = Column(String(20), nullable=False)  # empty, planted, forage
    plant_type = Column(String(50), nullable=True)
    growth_stage = Column(Integer, default=0)
    watered = Column(Boolean, default=False)
    forage_item = Column(String(50), nullable=True)
    forage_spawn_time = Column(Integer, default=0)
    plant_timer = Column(Integer, default=0)
    
    # Relationships
    save = relationship("GameSave", back_populates="field_cells")
    
    def __repr__(self):
        return f"<FieldCell(save_id={self.save_id}, x={self.x}, y={self.y}, type='{self.cell_type}')>"

class InventoryItem(Base):
    """Player inventory items - normalized storage."""
    __tablename__ = 'inventory_items'
    
    id = Column(Integer, primary_key=True)
    save_id = Column(Integer, ForeignKey('game_saves.id'), nullable=False)
    item_name = Column(String(50), nullable=False)
    quantity = Column(Integer, default=0)
    
    # Relationships
    save = relationship("GameSave", back_populates="inventory_items")
    
    def __repr__(self):
        return f"<InventoryItem(save_id={self.save_id}, item='{self.item_name}', qty={self.quantity})>"