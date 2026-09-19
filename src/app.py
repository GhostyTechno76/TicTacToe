import math
import random

import pygame

from src.ai import EASY, HARD, MEDIUM, choose_move
from src.animations import clamp, ease_in_out, ease_out_back, ease_out_cubic, lerp
from src.assets import AssetStore
from src.board import WIN_LINES, Board
from src.constants import (
    BOARD_MARGIN_TOP,
    BOARD_MARGIN_X,
    BOARD_SIZE,
    BOARD_GLOW_WIDTH,
    CELL_SIZE,
    COLOR_BG,
    COLOR_ACCENT,
    COLOR_ACCENT_DIM,
    COLOR_BG_TOP,
    COLOR_MAGENTA,
    COLOR_PANEL,
    COLOR_SHADOW,
    COLOR_TEXT_MUTED,
    COLOR_LINE,
    COLOR_TEXT,
    CONTROL_GAP,
    EASY_RECT,
    EMPTY,
    FPS,
    FONT_NAME,
    HARD_RECT,
    HOVER_ALPHA,
    MARK_ANIMATION_DURATION,
    MARK_PADDING,
    MEDIUM_RECT,
    AI_DELAY_MAX,
    AI_DELAY_MIN,
    BANNER_ANIMATION_DURATION,
    BOARD_INTRO_DURATION,
    PARTICLE_COUNT,
    PARTICLE_DURATION,
    PARTICLE_SPEED,
    PLAYER_O,
    PLAYER_X,
    PVAI_RECT,
    PVP_RECT,
    RESTART_RECT,
    RESTART_ANIMATION_DURATION,
    SCORE_POP_DURATION,
    SCORE_Y,
    STATUS_TRANSITION_DURATION,
    STATUS_Y,
    WIN_GLOW_WIDTH,
    WIN_LINE_DURATION,
    WIN_LINE_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from src.ui import Button


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, 30, bold=True)
        self.small_font = pygame.font.SysFont(FONT_NAME, 17, bold=True)
        self.score_font = pygame.font.SysFont(FONT_NAME, 14, bold=True)
        self.board = Board()
        self.assets = AssetStore(self.screen)
        self.running = True
        self.vs_ai = False
        self.difficulty = EASY
        self.muted = False
        self.score = {PLAYER_X: 0, PLAYER_O: 0, "draws": 0}
        self.score_pop = {PLAYER_X: 0.0, PLAYER_O: 0.0, "draws": 0.0}
        self.mark_animations = {}
        self.board_intro = 0.0
        self.restart_animation = 1.0
        self.ai_thinking = False
        self.ai_timer = 0.0
        self.ai_delay = 0.0
        self.winning_line = None
        self.win_line_progress = 0.0
        self.banner_progress = 0.0
        self.outcome_recorded = False
        self.status_key = None
        self.status_transition = STATUS_TRANSITION_DURATION
        self.particles = []
        self.buttons = {
            "pvp": Button(PVP_RECT, "PVP", self.small_font, active=True),
            "pvai": Button(PVAI_RECT, "PVAi", self.small_font),
            "easy": Button(EASY_RECT, "EASY", self.small_font, active=True),
            "medium": Button(MEDIUM_RECT, "MEDIUM", self.small_font),
            "hard": Button(HARD_RECT, "HARD", self.small_font),
        }
        self.background = self._build_background()
        self.board_glow = self._build_board_glow()
        self.particle_seed = random.Random(7)
        self._spawn_particles()

    def run(self):
        while self.running:
            self._handle_events()
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self._restart_game()
                elif event.key == pygame.K_m:
                    self.muted = not self.muted
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    self._try_move(event.key - pygame.K_1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for button in self.buttons.values():
                    button.release()

    def _handle_click(self, pos):
        for button in self.buttons.values():
            if button.click(pos):
                break
        if pygame.Rect(*RESTART_RECT).collidepoint(pos):
            self._restart_game()
            return
        if pygame.Rect(*PVP_RECT).collidepoint(pos):
            self.vs_ai = False
            self.ai_thinking = False
            return
        if pygame.Rect(*PVAI_RECT).collidepoint(pos):
            self.vs_ai = True
            self._maybe_start_ai_move()
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

        index = cell_index_from_pos(pos)
        self._try_move(index)

    def _try_move(self, index):
        if index is None or self.ai_thinking or self.board.game_over:
            return
        if self.vs_ai and self.board.current_player != PLAYER_X:
            return
        if self.board.place(index):
            self.mark_animations[index] = {"mark": self.board.cells[index], "progress": 0.0, "removing": False}
            self._after_move()

    def _after_move(self):
        if self.board.game_over:
            self.ai_thinking = False
            self._finish_outcome()
        else:
            self._maybe_start_ai_move()

    def _maybe_start_ai_move(self):
        if not self.vs_ai or self.board.game_over or self.board.current_player != PLAYER_O:
            return
        self.ai_thinking = True
        self.ai_timer = 0.0
        self.ai_delay = random.uniform(AI_DELAY_MIN, AI_DELAY_MAX)

    def _place_ai_move(self):
        legal = self.board.empty_cells()
        if not legal:
            return
        move = choose_move(self.board.cells, PLAYER_O, self.difficulty)
        if move in legal and self.board.place(move):
            self.mark_animations[move] = {"mark": PLAYER_O, "progress": 0.0, "removing": False}
        self.ai_thinking = False
        self._after_move()

    def _restart_game(self):
        for animation in self.mark_animations.values():
            animation["removing"] = True
            animation["progress"] = 0.0
        self.board.reset()
        self.board_intro = 0.0
        self.restart_animation = 0.0
        self.ai_thinking = False
        self.winning_line = None
        self.win_line_progress = 0.0
        self.banner_progress = 0.0
        self.outcome_recorded = False
        self.particles.clear()

    def _update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for name, button in self.buttons.items():
            button.active = (name == "pvp" and not self.vs_ai) or (name == "pvai" and self.vs_ai)
            button.disabled = name in {"easy", "medium", "hard"} and not self.vs_ai
            if name in {"easy", "medium", "hard"}:
                button.active = self.difficulty == {"easy": EASY, "medium": MEDIUM, "hard": HARD}[name]
            button.update(mouse_pos, dt)

        self._update_cursor(mouse_pos)
        self.board_intro = min(1.0, self.board_intro + dt / BOARD_INTRO_DURATION)
        self.restart_animation = min(1.0, self.restart_animation + dt / RESTART_ANIMATION_DURATION)
        self.status_transition = min(STATUS_TRANSITION_DURATION, self.status_transition + dt)
        self.banner_progress = min(1.0, self.banner_progress + dt / BANNER_ANIMATION_DURATION) if self.board.winner else 0.0
        if self.board.winner:
            self.win_line_progress = min(1.0, self.win_line_progress + dt / WIN_LINE_DURATION)
        if self.ai_thinking:
            self.ai_timer += dt
            if self.ai_timer >= self.ai_delay:
                self._place_ai_move()

        for index in list(self.mark_animations):
            animation = self.mark_animations[index]
            animation["progress"] += dt / MARK_ANIMATION_DURATION
            if animation["removing"] and animation["progress"] >= 1.0:
                del self.mark_animations[index]
        for mark in self.score_pop:
            self.score_pop[mark] = min(1.0, self.score_pop[mark] + dt / SCORE_POP_DURATION)
        self._update_particles(dt)

    def _finish_outcome(self):
        if self.outcome_recorded:
            return
        self.outcome_recorded = True
        if self.board.winner:
            self.score[self.board.winner] += 1
            self.score_pop[self.board.winner] = 0.0
            self.winning_line = self._find_winning_line()
            self.win_line_progress = 0.0
            self.banner_progress = 0.0
            self._spawn_particles(self.winning_line)
        else:
            self.score["draws"] += 1
            self.score_pop["draws"] = 0.0

    def _find_winning_line(self):
        for line in WIN_LINES:
            if self.board.cells[line[0]] and self.board.cells[line[0]] == self.board.cells[line[1]] == self.board.cells[line[2]]:
                return line
        return None

    def _update_cursor(self, mouse_pos):
        over_button = any(button.hovered for button in self.buttons.values()) or pygame.Rect(*RESTART_RECT).collidepoint(mouse_pos)
        over_cell = cell_index_from_pos(mouse_pos) is not None
        try:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if over_button or over_cell else pygame.SYSTEM_CURSOR_ARROW)
        except pygame.error:
            pass

    def _build_background(self):
        background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            amount = y / max(1, WINDOW_HEIGHT - 1)
            color = tuple(int(lerp(COLOR_BG_TOP[i], COLOR_BG[i], amount)) for i in range(3))
            pygame.draw.line(background, color, (0, y), (WINDOW_WIDTH, y))
        grid = pygame.Surface(background.get_size(), pygame.SRCALPHA)
        for x in range(0, WINDOW_WIDTH, 34):
            pygame.draw.line(grid, (*COLOR_ACCENT, 12), (x, 0), (x, WINDOW_HEIGHT), 1)
        for y in range(0, WINDOW_HEIGHT, 34):
            pygame.draw.line(grid, (*COLOR_ACCENT, 12), (0, y), (WINDOW_WIDTH, y), 1)
        background.blit(grid, (0, 0))
        return background

    def _build_board_glow(self):
        glow = pygame.Surface((BOARD_SIZE + BOARD_GLOW_WIDTH * 2, BOARD_SIZE + BOARD_GLOW_WIDTH * 2), pygame.SRCALPHA)
        board = self.assets.board.copy()
        board.set_alpha(80)
        glow.blit(board, (BOARD_GLOW_WIDTH, BOARD_GLOW_WIDTH), special_flags=pygame.BLEND_ADD)
        return glow

    def _spawn_particles(self, line=None):
        if line is None:
            return
        start = self._cell_center(line[0])
        end = self._cell_center(line[2])
        for _ in range(PARTICLE_COUNT):
            origin = (random.uniform(start[0], end[0]), random.uniform(start[1], end[1]))
            angle = random.uniform(0, math.tau)
            self.particles.append({"x": origin[0], "y": origin[1], "vx": math.cos(angle) * PARTICLE_SPEED, "vy": math.sin(angle) * PARTICLE_SPEED, "life": PARTICLE_DURATION})

    def _update_particles(self, dt):
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.particles = [particle for particle in self.particles if particle["life"] > 0]

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        self._draw_particles()
        self._draw_status()
        self._draw_board()
        self._draw_marks()
        self._draw_hover_preview()
        self._draw_win_effects()
        self._draw_controls()

    def _draw_status(self):
        if self.ai_thinking:
            text = "AI THINKING . . ."
        elif self.board.is_draw:
            text = "Draw"
        elif self.vs_ai and self.board.current_player == PLAYER_O:
            text = "TURN: O (AI)"
        else:
            text = f"TURN: {self.board.current_player}"
        key = (text, self.board.current_player)
        if key != self.status_key:
            self.status_key = key
            self.status_transition = 0.0
        surface = self.font.render(text, True, COLOR_TEXT)
        surface.set_alpha(int(255 * ease_out_cubic(self.status_transition / STATUS_TRANSITION_DURATION)))
        rect = surface.get_rect(center=(WINDOW_WIDTH // 2, STATUS_Y))
        self.screen.blit(surface, rect)
        self._draw_scoreboard()

    def _draw_scoreboard(self):
        text = f"X {self.score[PLAYER_X]}     O {self.score[PLAYER_O]}     DRAWS {self.score['draws']}"
        surface = self.score_font.render(text, True, COLOR_TEXT_MUTED)
        self.screen.blit(surface, surface.get_rect(center=(WINDOW_WIDTH // 2, SCORE_Y)))

    def _draw_board(self):
        board_rect = pygame.Rect(BOARD_MARGIN_X, BOARD_MARGIN_TOP, BOARD_SIZE, BOARD_SIZE)
        self.screen.blit(self.board_glow, (board_rect.x - BOARD_GLOW_WIDTH, board_rect.y - BOARD_GLOW_WIDTH), special_flags=pygame.BLEND_ADD)
        intro_scale = 0.94 + 0.06 * ease_out_cubic(self.board_intro)
        board_image = self.assets.board
        if intro_scale != 1.0:
            board_image = pygame.transform.smoothscale(board_image, (int(BOARD_SIZE * intro_scale), int(BOARD_SIZE * intro_scale)))
        board_image.set_alpha(int(255 * ease_out_cubic(self.board_intro)))
        self.screen.blit(board_image, board_image.get_rect(center=board_rect.center))

    def _draw_marks(self):
        winning = set(self.winning_line or ())
        for index, animation in self.mark_animations.items():
            progress = clamp(animation["progress"])
            if animation["removing"]:
                alpha = int(255 * (1 - ease_out_cubic(progress)))
                scale = 1.0 - 0.12 * ease_out_cubic(progress)
            else:
                alpha = int(255 * ease_out_cubic(progress))
                scale = max(0.05, ease_out_back(progress))
            if self.winning_line and index not in winning:
                alpha = int(alpha * 0.38)
            if index in winning and self.board.winner:
                alpha = int(alpha * (0.8 + 0.2 * (0.5 + 0.5 * math.sin(self.win_line_progress * math.tau))))
            image = self.assets.marks[animation["mark"]]
            size = max(1, int(image.get_width() * scale))
            rendered = pygame.transform.smoothscale(image, (size, size))
            rendered.set_alpha(max(0, min(255, alpha)))
            self.screen.blit(rendered, rendered.get_rect(center=self._cell_center(index)))

    def _draw_hover_preview(self):
        index = cell_index_from_pos(pygame.mouse.get_pos())
        if not self._can_play(index):
            return
        cell = pygame.Rect(BOARD_MARGIN_X + index % 3 * CELL_SIZE, BOARD_MARGIN_TOP + index // 3 * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (*COLOR_ACCENT, HOVER_ALPHA), highlight.get_rect(), 2, border_radius=8)
        self.screen.blit(highlight, cell)
        ghost = self.assets.marks[self.board.current_player].copy()
        ghost.set_alpha(72)
        self.screen.blit(ghost, ghost.get_rect(center=cell.center))

    def _draw_win_effects(self):
        if self.winning_line:
            start = self._cell_center(self.winning_line[0])
            end = self._cell_center(self.winning_line[2])
            target = (lerp(start[0], end[0], ease_in_out(self.win_line_progress)), lerp(start[1], end[1], ease_in_out(self.win_line_progress)))
            glow = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(glow, (*COLOR_ACCENT, 100), start, target, WIN_GLOW_WIDTH)
            self.screen.blit(glow, (0, 0), special_flags=pygame.BLEND_ADD)
            pygame.draw.line(self.screen, COLOR_TEXT, start, target, WIN_LINE_WIDTH)
            overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
            overlay.fill((*COLOR_SHADOW, int(115 * ease_out_cubic(self.banner_progress))))
            self.screen.blit(overlay, (BOARD_MARGIN_X, BOARD_MARGIN_TOP))
            banner = self.assets.win_banners[self.board.winner]
            scale = 0.8 + 0.2 * ease_out_back(self.banner_progress)
            bob = math.sin(self.banner_progress * math.pi * 3) * 3
            size = (max(1, int(banner.get_width() * scale)), max(1, int(banner.get_height() * scale)))
            banner = pygame.transform.smoothscale(banner, size)
            banner.set_alpha(int(255 * ease_out_cubic(self.banner_progress)))
            self.screen.blit(banner, banner.get_rect(center=(WINDOW_WIDTH // 2, BOARD_MARGIN_TOP + BOARD_SIZE // 2 + bob)))

    def _draw_particles(self):
        layer = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for particle in self.particles:
            alpha = int(180 * clamp(particle["life"] / PARTICLE_DURATION))
            pygame.draw.circle(layer, (*COLOR_ACCENT, alpha), (int(particle["x"]), int(particle["y"])), 2)
        self.screen.blit(layer, (0, 0), special_flags=pygame.BLEND_ADD)

    def _draw_controls(self):
        self.buttons["pvp"].draw(self.screen)
        self.buttons["pvai"].draw(self.screen)
        restart_rect = pygame.Rect(*RESTART_RECT)
        if restart_rect.collidepoint(pygame.mouse.get_pos()):
            glow = pygame.Surface((restart_rect.width + 18, restart_rect.height + 18), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*COLOR_ACCENT, 85), glow.get_rect().inflate(-9, -9), 3, border_radius=10)
            self.screen.blit(glow, (restart_rect.x - 9, restart_rect.y - 9), special_flags=pygame.BLEND_ADD)
        restart = self.assets.restart
        if self.restart_animation < 1.0:
            scale = 0.85 + 0.15 * ease_out_back(self.restart_animation)
            restart = pygame.transform.rotozoom(restart, 8 * (1 - self.restart_animation), scale)
        self.screen.blit(restart, restart.get_rect(center=restart_rect.center))
        self.buttons["easy"].draw(self.screen)
        self.buttons["medium"].draw(self.screen)
        self.buttons["hard"].draw(self.screen)
        muted = "MUTED" if self.muted else "SOUND ON"
        sound = self.score_font.render(f"{muted}  [M]", True, COLOR_TEXT_MUTED)
        self.screen.blit(sound, sound.get_rect(bottomright=(WINDOW_WIDTH - CONTROL_GAP, WINDOW_HEIGHT - CONTROL_GAP)))

    def _cell_center(self, index):
        return (BOARD_MARGIN_X + index % 3 * CELL_SIZE + CELL_SIZE // 2, BOARD_MARGIN_TOP + index // 3 * CELL_SIZE + CELL_SIZE // 2)

    def _can_play(self, index):
        return index is not None and not self.board.game_over and not self.ai_thinking and (not self.vs_ai or self.board.current_player == PLAYER_X) and self.board.cells[index] == EMPTY


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
