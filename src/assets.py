"""Image loading with transparent placeholders when optional art is unavailable."""

from pathlib import Path

import pygame

from src.constants import (
    BOARD_SIZE,
    CELL_SIZE,
    COLOR_BUTTON_ACTIVE,
    COLOR_ACCENT,
    COLOR_MAGENTA,
    MARK_PADDING,
    PLAYER_O,
    PLAYER_X,
    RESTART_RECT,
)


class AssetStore:
    """Load, scale, and retain all image assets used by the app."""

    def __init__(self, screen):
        self.screen = screen
        self.image_dir = Path(__file__).resolve().parent.parent / "assets" / "images"
        self.board = self._load("TicTacToeBoard.png", (BOARD_SIZE, BOARD_SIZE), self._board_fallback())
        mark_size = CELL_SIZE - MARK_PADDING * 2
        self.marks = {
            PLAYER_X: self._load("TicTacToe_X.png", (mark_size, mark_size), self._mark_fallback(COLOR_ACCENT, "X")),
            PLAYER_O: self._load("TicTacToe_O.png", (mark_size, mark_size), self._mark_fallback(COLOR_MAGENTA, "O")),
        }
        self.restart = self._load("Restart.png", RESTART_RECT[2:], self._restart_fallback())
        self.win_banners = {
            PLAYER_X: self._load("X_WINS.png", None, self._text_fallback(COLOR_ACCENT, "X WINS!")),
            PLAYER_O: self._load("O_WIns.png", None, self._text_fallback(COLOR_MAGENTA, "O WINS!")),
        }

    def _load(self, name, size, fallback):
        try:
            image = pygame.image.load(self.image_dir / name).convert_alpha()
        except (pygame.error, OSError):
            image = fallback
        if size is not None and image.get_size() != tuple(size):
            image = pygame.transform.smoothscale(image, size)
        return image

    def _board_fallback(self):
        image = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
        step = BOARD_SIZE // 3
        for offset in (step, step * 2):
            pygame.draw.line(image, COLOR_ACCENT, (offset, 0), (offset, BOARD_SIZE), 3)
            pygame.draw.line(image, COLOR_ACCENT, (0, offset), (BOARD_SIZE, offset), 3)
        return image

    def _mark_fallback(self, color, label):
        image = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        font = pygame.font.Font(None, CELL_SIZE - 20)
        text = font.render(label, True, color)
        image.blit(text, text.get_rect(center=image.get_rect().center))
        return image

    def _restart_fallback(self):
        image = pygame.Surface(RESTART_RECT[2:], pygame.SRCALPHA)
        pygame.draw.rect(image, COLOR_BUTTON_ACTIVE, image.get_rect(), 2, border_radius=8)
        font = pygame.font.Font(None, 18)
        text = font.render("RESTART", True, COLOR_ACCENT)
        image.blit(text, text.get_rect(center=image.get_rect().center))
        return image

    def _text_fallback(self, color, label):
        font = pygame.font.Font(None, 28)
        return font.render(label, True, color)
