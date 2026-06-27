# CSC200M24PID102

# 🃏 Solitaire

A fully playable **Klondike Solitaire** game built in Python using Pygame. Features a complete game engine with drag-and-drop card movement, real-time rendering, and Klondike rules enforcement — all built from scratch without any game engine framework.

---

## Demo

> *(Add a screenshot or GIF of the game running here — even a single screenshot makes a huge difference)*

---

## Features

- **Full Klondike rules** — alternating colours, descending ranks, Kings-only on empty piles, Ace-to-King foundation building
- **Drag-and-drop interface** — click and drag face-up cards across tableau piles with smooth mouse tracking
- **Auto flip** — face-down cards flip automatically when uncovered
- **7-column tableau** with proper initial deal (1 card in column 1, 2 in column 2, ... 7 in column 7)
- **Foundation pile support** — move cards from tableau to foundation stacks
- **Modular architecture** — game logic cleanly separated from rendering

---

## Project Structure

```
Solitaire/
├── FrontEnd.py        # Pygame event loop, rendering, drag-and-drop input handling
├── Tableau.py         # 7-pile tableau logic: initialization, move validation, rendering
├── card.py            # Card class: suit, rank, colour, face-up/face-down state, image rendering
├── deck.py            # Deck class: 52-card creation, shuffle, deal
├── foundation.py      # Foundation pile logic: Ace-to-King suit stacking
├── stack.py           # Linked-list stack used as the underlying pile data structure
├── stockpile.py       # Stockpile (draw pile) logic
├── constants.py       # Shared constants (screen dimensions, colours, card sizes)
└── Pictures/          # Card image assets
```

---

## How It Works

### Data Structure
Each tableau pile is implemented as a **linked-list stack** (`stack.py`). Cards are pushed/popped from the head, and the renderer traverses the list top-to-bottom to draw cards with a vertical offset.

### Move Validation (`Tableau.CanAddCard`)
A card can be placed on a pile if:
1. The destination pile is empty → only a King is allowed
2. The card's colour is **opposite** to the top card's colour
3. The card's rank is **exactly one less** than the top card's rank

### Drag-and-Drop Flow
1. `MOUSEBUTTONDOWN` → `detect_card_click()` hit-tests all face-up cards using `pygame.Rect.collidepoint`
2. `MOUSEMOTION` → selected card renders at mouse position
3. `MOUSEBUTTONUP` → `move_card()` checks all pile rectangles for a valid drop target and applies the move if valid

---

## Installation

**Requirements:** Python 3.8+, Pygame

```bash
# Clone the repository
git clone https://github.com/Waleed-Sarfraz-7/Solitaire.git
cd Solitaire

# Install Pygame
pip install pygame

# Run the game
python FrontEnd.py
```

---

## Controls

| Action | Input |
|---|---|
| Pick up a card | Left-click on any face-up card |
| Move a card | Drag to target pile, release mouse |
| Move to foundation | Use `MoveCardToFoundation()` (foundation UI coming soon) |

---

## Tech Stack

| | |
|---|---|
| Language | Python 3 |
| Graphics | Pygame |
| Data Structure | Custom linked-list stack |
| Architecture | OOP — separated model, view, controller |

---

## Concepts Demonstrated

- Object-oriented design with single-responsibility classes
- Custom linked-list implementation for pile management
- Event-driven programming with Pygame's event loop
- Collision detection for interactive UI elements
- Game state management without external frameworks

---

## Author

**Waleed Sarfraz** — CS Undergraduate, UET Lahore  
[GitHub](https://github.com/Waleed-Sarfraz-7) · [LinkedIn](https://linkedin.com/in/waleed-sarfraz)
