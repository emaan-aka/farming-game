# Farm & Forage Forever

A 2D farming and foraging simulation game built with Python and Pygame. Players can grow crops, forage for items, manage inventory, and progress through days, with the eventual goal of growing a giant pumpkin!

## Requirements

- **Python**: 3.13 or higher
- **Dependencies**: 
  - `pygame >= 2.0.0`
  - `pygame-emojis`

## How to Run

### Basic Version (JSON Save System)
```bash
python3 main.py
```
Features: JSON-based save/load, single player, basic game mechanics

## Controls

### Movement
- **W** / **↑**: Move up
- **S** / **↓**: Move down
- **A** / **←**: Move left
- **D** / **→**: Move right

### Actions
- **SPACE** / **P**: Plant seed (must have seeds selected)
- **E**: Water plant
- **H**: Harvest mature plant
- **F**: Forage for items
- **B**: Buy seeds (at seed shop)
- **X**: Ship items (at shipping container)
- **TAB**: Cycle through inventory items

### Save/Load
**Basic Version:**
- **Ctrl+Q**: Save game to JSON file
- **Ctrl+L**: Load game from JSON file