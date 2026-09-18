import random

from src.board import WIN_LINES
from src.constants import EMPTY, PLAYER_O, PLAYER_X

EASY = "easy"
MEDIUM = "medium"
HARD = "hard"


def choose_move(cells, ai_mark=PLAYER_O, difficulty=EASY):
    """Return a legal cell index for the AI. Never returns an occupied cell."""
    moves = _empty_cells(cells)
    if not moves:
        raise ValueError("no legal moves")

    if difficulty == EASY:
        choice = random.choice(moves)
    elif difficulty == MEDIUM:
        choice = _medium_move(cells, ai_mark, moves)
    else:
        choice = _hard_move(cells, ai_mark, moves)

    if choice not in moves:
        return random.choice(moves)
    return choice


def _empty_cells(cells):
    return [i for i, mark in enumerate(cells) if mark == EMPTY]


def _winner(cells):
    for a, b, c in WIN_LINES:
        mark = cells[a]
        if mark != EMPTY and mark == cells[b] == cells[c]:
            return mark
    return None


def _would_win(cells, index, mark):
    trial = list(cells)
    trial[index] = mark
    return _winner(trial) == mark


def _medium_move(cells, ai_mark, moves):
    human = PLAYER_X if ai_mark == PLAYER_O else PLAYER_O
    for index in moves:
        if _would_win(cells, index, ai_mark):
            return index
    for index in moves:
        if _would_win(cells, index, human):
            return index
    if 4 in moves:
        return 4
    corners = [index for index in (0, 2, 6, 8) if index in moves]
    if corners:
        return random.choice(corners)
    return random.choice(moves)


def _hard_move(cells, ai_mark, moves):
    best_score = None
    best_moves = []
    for index in moves:
        trial = list(cells)
        trial[index] = ai_mark
        score = _minimax(trial, maximizing=False, ai_mark=ai_mark, depth=1)
        if best_score is None or score > best_score:
            best_score = score
            best_moves = [index]
        elif score == best_score:
            best_moves.append(index)
    return random.choice(best_moves)


def _minimax(cells, maximizing, ai_mark, depth):
    human = PLAYER_X if ai_mark == PLAYER_O else PLAYER_O
    winner = _winner(cells)
    if winner == ai_mark:
        return 10 - depth
    if winner == human:
        return depth - 10

    moves = _empty_cells(cells)
    if not moves:
        return 0

    if maximizing:
        best = None
        for index in moves:
            trial = list(cells)
            trial[index] = ai_mark
            score = _minimax(trial, False, ai_mark, depth + 1)
            if best is None or score > best:
                best = score
        return best

    best = None
    for index in moves:
        trial = list(cells)
        trial[index] = human
        score = _minimax(trial, True, ai_mark, depth + 1)
        if best is None or score < best:
            best = score
    return best
