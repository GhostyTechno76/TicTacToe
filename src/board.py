from src.constants import EMPTY, PLAYER_O, PLAYER_X

WIN_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


class Board:
    """3x3 Tic-Tac-Toe rules. No drawing."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.cells = [EMPTY] * 9
        self.current_player = PLAYER_X
        self.winner = None
        self.is_draw = False

    def place(self, index):
        """Place the current player's mark. Returns True if the move was legal."""
        if self.game_over:
            return False
        if index < 0 or index > 8:
            return False
        if self.cells[index] != EMPTY:
            return False

        self.cells[index] = self.current_player
        self._update_outcome()
        if not self.game_over:
            self.current_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X
        return True

    def empty_cells(self):
        return [i for i, mark in enumerate(self.cells) if mark == EMPTY]

    @property
    def game_over(self):
        return self.winner is not None or self.is_draw

    def _update_outcome(self):
        for a, b, c in WIN_LINES:
            mark = self.cells[a]
            if mark != EMPTY and mark == self.cells[b] == self.cells[c]:
                self.winner = mark
                return
        if EMPTY not in self.cells:
            self.is_draw = True
