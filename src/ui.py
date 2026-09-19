"""Reusable UI widgets for the neon game interface."""

import pygame

from src.animations import approach, ease_out_cubic
from src.constants import (
    COLOR_BUTTON,
    COLOR_BUTTON_ACTIVE,
    COLOR_BUTTON_BORDER,
    COLOR_BUTTON_HOVER,
    COLOR_BUTTON_TEXT,
    COLOR_SHADOW,
    BUTTON_CORNER_RADIUS,
)


class Button:
    """A rounded button with time-based hover and pressed transitions."""

    def __init__(self, rect, label, font, *, active=False, disabled=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.active = active
        self.disabled = disabled
        self.hovered = False
        self.pressed = False
        self.hover_amount = 0.0
        self.press_amount = 0.0

    def update(self, mouse_pos, dt):
        self.hovered = self.rect.collidepoint(mouse_pos)
        target_hover = 1.0 if self.hovered and not self.disabled else 0.0
        target_press = 1.0 if self.pressed else 0.0
        self.hover_amount = approach(self.hover_amount, target_hover, 9.0, dt)
        self.press_amount = approach(self.press_amount, target_press, 14.0, dt)

    def click(self, pos):
        if self.disabled or not self.rect.collidepoint(pos):
            return False
        self.pressed = True
        return True

    def release(self):
        self.pressed = False

    def draw(self, surface):
        scale = 1.0 - 0.04 * ease_out_cubic(self.press_amount)
        draw_rect = self.rect.inflate(-int(self.rect.width * (1 - scale)), -int(self.rect.height * (1 - scale)))
        glow_alpha = int(35 + 65 * self.hover_amount)
        glow = pygame.Surface((draw_rect.width + 20, draw_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (*COLOR_BUTTON_HOVER, glow_alpha),
            glow.get_rect().inflate(-10, -10),
            width=4,
            border_radius=BUTTON_CORNER_RADIUS + 3,
        )
        surface.blit(glow, (draw_rect.x - 10, draw_rect.y - 10), special_flags=pygame.BLEND_ADD)

        fill = COLOR_BUTTON_ACTIVE if self.active else COLOR_BUTTON
        if self.disabled:
            fill = tuple(max(12, value // 2) for value in fill)
        border = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON_BORDER
        pygame.draw.rect(surface, fill, draw_rect, border_radius=BUTTON_CORNER_RADIUS)
        pygame.draw.rect(surface, border, draw_rect, width=1, border_radius=BUTTON_CORNER_RADIUS)

        text_color = COLOR_BUTTON_TEXT if not self.disabled else tuple(value // 2 for value in COLOR_BUTTON_TEXT)
        text = self.font.render(self.label, True, text_color)
        surface.blit(text, text.get_rect(center=draw_rect.center))
