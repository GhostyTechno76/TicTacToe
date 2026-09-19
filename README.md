# Neon Tic-Tac-Toe

A modern arcade-styled Tic-Tac-Toe built with Python and Pygame, featuring a polished neon interface, animated board interactions, and a competitive AI opponent.

This project turns a classic game into a stylized retro-inspired experience with hover previews, glowing win lines, score tracking, particle bursts, and multiple game modes.

## Overview

The game is designed as a clean, interactive desktop app with:

- A grid-based board with custom marker rendering
- Player-vs-player and player-vs-AI gameplay
- Adjustable AI difficulty levels
- Animated win celebrations and scoreboard feedback
- Pixel-inspired neon UI elements and layered visual effects
- Keyboard and mouse controls for smooth play

## Features

### Core gameplay

- Classic 3x3 Tic-Tac-Toe rules
- Turn-based validation and legal move checking
- Automatic win and draw detection
- Scoreboard that tracks X wins, O wins, and draws
- Restart button and quick keyboard restart with R

### Game modes

- PVP mode: two human players on the same device
- PVAI mode: human vs computer with selectable difficulty
- Difficulty switching: Easy, Medium, and Hard

### AI system

- Easy: random legal move selection
- Medium: strategic center/corner preference plus immediate win/block detection
- Hard: minimax-based decision engine that evaluates future outcomes

### Visual effects

- Neon gradient background with subtle grid overlay
- Hover cell preview for mouse interaction
- Animated X and O markers with scale and alpha transitions
- Winning line glow and banner celebration
- Particle burst effect for victories
- Smooth transitions for status text and board intro
- Custom rounded UI buttons with hover and press animations

### Interface and controls

- Mouse-based interaction for board cells and menu buttons
- Hand cursor when hovering interactive elements
- Keyboard shortcuts:
  - R: restart match
  - M: toggle muted indicator state
  - Escape: quit game
  - 1-9: quick cell selection shortcut
- Restart control button in the corner of the interface

### Art and rendering

- Uses asset loading with fallback drawing when image files are missing
- Board and marker artwork can be replaced by custom image assets
- Pixel-inspired, neon UI aesthetic with layered glow and alpha blending

## Tech Stack

- Python 3
- Pygame 2.6.1
- Object-oriented game architecture
- Custom animation helpers and easing functions
- Surface-based rendering and alpha blending
- Asset management system with graceful fallback graphics

## Algorithms and Logic

### 1. Board state management

The board model tracks:

- cell occupancy
- current player
- win state
- draw state
- legal move availability

This is handled in the board logic, where each move validates index bounds, checks cell emptiness, updates the winner, and flips turns when the game continues.

### 2. Win detection

The game checks all valid winning combinations in a fixed tuple of line indexes:

- rows
- columns
- diagonals

If three matching marks align in any line, the winner is declared.

### 3. AI difficulty logic

#### Easy

The AI chooses a random legal move from the available empty cells.

#### Medium

The medium strategy uses a small tactical heuristic:

- prefers immediate winning moves
- blocks the opponent’s winning move
- prefers the center cell when available
- falls back to corners before random remaining spaces

This creates a stronger, more human-like opponent without full-depth search.

#### Hard

The hard AI uses minimax, a recursive decision tree algorithm that simulates future game states and chooses the move with the best outcome for the AI.

The evaluation logic is designed to:

- maximize AI advantage when a winning line is reachable
- minimize losses against the human player
- evaluate game states by depth, so quicker wins and slower losses are preferred

### 4. Animation smoothing

The project uses custom easing and interpolation functions such as:

- ease_out_cubic
- ease_out_back
- ease_in_out
- lerp
- approach

These create smooth motion for:

- marker pop-in scale animation
- board intro transition
- hover button effects
- win banner motion
- particle motion

### 5. Tweening and UI behavior

Buttons animate through hover and press states using time-based interpolation so they respond naturally to mouse movement and clicks.

## Pixel-Inspired UI Design

The interface is intentionally styled as a modern pixel/retro arcade experience:

- compact neon palette with cyan and magenta accents
- grid background with subtle glow lines
- rounded control panels and UI buttons
- textured display surfaces resembling classic game HUDs
- layered transparency and light bloom effects
- polished board glow for emphasis during active and winning states

The design is not a full sprite-heavy game engine, but it uses a deliberately pixel-art-inspired presentation through surface rendering, scaling, glow overlays, and custom UI widgets.

## Project Structure

```text
TicTacToe/
├── assets/
│   └── images/
│       ├── TicTacToeBoard.png
│       ├── TicTacToe_X.png
│       ├── TicTacToe_O.png
│       ├── Restart.png
│       ├── X_WINS.png
│       └── O_WIns.png
├── src/
│   ├── ai.py
│   ├── animations.py
│   ├── app.py
│   ├── assets.py
│   ├── board.py
│   ├── constants.py
│   ├── ui.py
│   └── screens/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Requirements

- Python 3.8 or newer
- Pygame 2.6.1

## Installation

1. Clone the repository:

```bash
git clone https://github.com/GhostyTechno76/TicTacToe.git
cd TicTacToe
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

From the project root:

```bash
python main.py
```

## Controls

- Mouse click: place mark on the board
- Restart button: start a new round
- R: restart the current game
- M: toggle sound state indicator
- Escape: exit the game
- 1-9: quick cell placement keys

## Gameplay Flow

1. Choose PVP or PVAI mode.
2. Select a difficulty if playing against AI.
3. Place marks in the 3x3 board.
4. First player to complete a row, column, or diagonal wins.
5. If the board fills without a winner, the match is a draw.
6. Scores accumulate until you restart or the app is closed.

## Example Use Cases

- Quick local multiplayer game
- Solo practice against a computer opponent
- UI/graphics demo of a polished Pygame app
- Educational project for AI and game-state logic

## Notes

This project is intentionally built as a compact, self-contained desktop game. It demonstrates a strong combination of game logic, UI design, and algorithmic decision making within a small Python codebase.

## Author

Made by [SUBHAM KUMAR DAS](https://github.com/GhostyTechno76).

## License

This project is available for educational and personal use. If you plan to use or distribute it in a public project, please credit the author and repository source appropriately.