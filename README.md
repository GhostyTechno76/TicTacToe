# Tic-Tac-Toe

A classic Tic-Tac-Toe game built with Python and [Pygame](https://www.pygame.org/).

## Features

- Classic 3×3 Tic-Tac-Toe gameplay
- Graphical interface powered by Pygame
- Win and draw detection
- P v AI with difficulty (Easy, Medium, Hard)

## Requirements

- Python 3.8 or newer
- Pygame 2.6.1 (installed via `requirements.txt`)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/GhostyTechno76/TicTacToe.git
   cd TicTacToe
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the game from the project root:

```bash
python main.py
```

## How to Play

1. Players take turns placing their mark (X or O) on the 3×3 grid.
2. The first player to get three marks in a row, whether horizontally, vertically, or diagonally, wins.
3. If all nine squares are filled and nobody has three in a row, the game is a draw.



## Project Structure

```
TicTacToe/
├── assets/
│   └── images/      # Images used by the game
├── src/             # Game source code
├── main.py          # Entry point
├── requirements.txt # Python dependencies
└── .gitignore
```

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.


## Author

Made by [SUBHAM KUMAR DAS](https://github.com/GhostyTechno76).