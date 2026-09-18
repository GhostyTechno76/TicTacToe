import pygame

from src.ai import EASY, HARD, MEDIUM, choose_move
from src.board import Board
from src.constants import (
    BOARD_MARGIN_TOP,
    BOARD_MARGIN_X,
    BOARD_SIZE,
    CELL_SIZE,
    COLOR_BG,
    COLOR_BUTTON,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_BORDER,
    COLOR_LINE,
    COLOR_O,
    COLOR_TEXT,
    COLOR_X,
    EASY_RECT,
    EMPTY,
    FPS,
    HARD_RECT,
    LINE_WIDTH,
    MARK_PADDING,
    MARK_WIDTH,
    MEDIUM_RECT,
    PLAYER_O,
    PLAYER_X,
    PVAI_RECT,
    PVP_RECT,
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
        self.vs_ai = False
        self.difficulty = EASY

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
        if pygame.Rect(*RESTART_RECT).collidepoint(pos):
            self.board.reset()
            return
        if pygame.Rect(*PVP_RECT).collidepoint(pos):
            self.vs_ai = False
            return
        if pygame.Rect(*PVAI_RECT).collidepoint(pos):
            self.vs_ai = True
            self._maybe_ai_move()
            return
        if pygame.Rect(*EASY_RECT).collidepoint(pos):
            self.difficulty = EASY
            return
        if pygame.Rect(*MEDIUM_RECT).collidepoint(pos):
            self.difficulty = MEDIUM
            return
        if pygame.Rect(*HARD_RECT).collidepoint(pos):
            self.difficulty = HARD
            return

        if self.vs_ai and self.board.current_player != PLAYER_X:
            return

        index = cell_index_from_pos(pos)
        if index is None:
            return
        if self.board.place(index):
            self._maybe_ai_move()

    def _maybe_ai_move(self):
        if not self.vs_ai or self.board.game_over:
            return
        if self.board.current_player != PLAYER_O:
            return
        legal = self.board.empty_cells()
        move = choose_move(self.board.cells, PLAYER_O, self.difficulty)
        if move not in legal:
            return
        self.board.place(move)

    def _draw(self):
        self.screen.fill(COLOR_BG)
        self._draw_status()
        self._draw_board()
        self._draw_marks()
        self._draw_controls()

    def _draw_status(self):
        if self.board.winner:
            text = f"{self.board.winner} wins"
        elif self.board.is_draw:
            text = "Draw"
        elif self.vs_ai and self.board.current_player == PLAYER_O:
            text = "Turn: O (AI)"
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

    def _draw_controls(self):
        self._draw_button(PVP_RECT, "PvP", not self.vs_ai)
        self._draw_button(PVAI_RECT, "PvAI", self.vs_ai)
        self._draw_button(RESTART_RECT, "Restart", False)
        self._draw_button(EASY_RECT, "Easy", self.difficulty == EASY)
        self._draw_button(MEDIUM_RECT, "Medium", self.difficulty == MEDIUM)
        self._draw_button(HARD_RECT, "Hard", self.difficulty == HARD)

    def _draw_button(self, rect_tuple, label, active):
        rect = pygame.Rect(*rect_tuple)
        fill = COLOR_BUTTON_ACTIVE if active else COLOR_BUTTON
        pygame.draw.rect(self.screen, fill, rect)
        pygame.draw.rect(self.screen, COLOR_BUTTON_BORDER, rect, 2)
        text = self.small_font.render(label, True, COLOR_TEXT)
        self.screen.blit(text, text.get_rect(center=rect.center))


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
