import pygame

from src.board import Board
from src.constants import (
    BOARD_MARGIN_TOP,
    BOARD_MARGIN_X,
    BOARD_SIZE,
    CELL_SIZE,
    COLOR_BG,
    COLOR_BUTTON,
    COLOR_BUTTON_BORDER,
    COLOR_LINE,
    COLOR_O,
    COLOR_TEXT,
    COLOR_X,
    EMPTY,
    FPS,
    LINE_WIDTH,
    MARK_PADDING,
    MARK_WIDTH,
    PLAYER_O,
    PLAYER_X,
    RESTART_RECT,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.board = Board()
        self.running = True

    def run(self):
        while self.running:
            self._handle_events()
            self._draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.board.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

    def _handle_click(self, pos):
        restart = pygame.Rect(*RESTART_RECT)
        if restart.collidepoint(pos):
            self.board.reset()
            return

        index = cell_index_from_pos(pos)
        if index is not None:
            self.board.place(index)

    def _draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_status()
        self._draw_board()
        self._draw_marks()
        self._draw_restart()

    def _draw_status(self):
        if self.board.winner:
            text = f"{self.board.winner} wins"
        elif self.board.is_draw:
            text = "Draw"
        else:
            text = f"Turn: {self.board.current_player}"
        surface = self.font.render(text, True, COLOR_TEXT)
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(surface, rect)

    def _draw_board(self):
        x0 = BOARD_MARGIN_X
        y0 = BOARD_MARGIN_TOP
        x1 = x0 + BOARD_SIZE
        y1 = y0 + BOARD_SIZE
        pygame.draw.rect(self.screen, COLOR_LINE, (x0, y0, BOARD_SIZE, BOARD_SIZE), LINE_WIDTH)
        for i in (1, 2):
            x = x0 + i * CELL_SIZE
            y = y0 + i * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_LINE, (x, y0), (x, y1), LINE_WIDTH)
            pygame.draw.line(self.screen, COLOR_LINE, (x0, y), (x1, y), LINE_WIDTH)

    def _draw_marks(self):
        for index, mark in enumerate(self.board.cells):
            if mark == EMPTY:
                continue
            col = index % 3
            row = index // 3
            cell = pygame.Rect(
                BOARD_MARGIN_X + col * CELL_SIZE,
                BOARD_MARGIN_TOP + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            inner = cell.inflate(-MARK_PADDING * 2, -MARK_PADDING * 2)
            if mark == PLAYER_X:
                pygame.draw.line(
                    self.screen, COLOR_X, inner.topleft, inner.bottomright, MARK_WIDTH
                )
                pygame.draw.line(
                    self.screen, COLOR_X, inner.topright, inner.bottomleft, MARK_WIDTH
                )
            elif mark == PLAYER_O:
                pygame.draw.ellipse(self.screen, COLOR_O, inner, MARK_WIDTH)

    def _draw_restart(self):
        rect = pygame.Rect(*RESTART_RECT)
        pygame.draw.rect(self.screen, COLOR_BUTTON, rect)
        pygame.draw.rect(self.screen, COLOR_BUTTON_BORDER, rect, 2)
        label = self.small_font.render("Restart", True, COLOR_TEXT)
        self.screen.blit(label, label.get_rect(center=rect.center))


def cell_index_from_pos(pos):
    x, y = pos
    if not (
        BOARD_MARGIN_X <= x < BOARD_MARGIN_X + BOARD_SIZE
        and BOARD_MARGIN_TOP <= y < BOARD_MARGIN_TOP + BOARD_SIZE
    ):
        return None
    col = (x - BOARD_MARGIN_X) // CELL_SIZE
    row = (y - BOARD_MARGIN_TOP) // CELL_SIZE
    return int(row * 3 + col)
