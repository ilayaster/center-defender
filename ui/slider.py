import pygame

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, font, label=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.font = font
        self.label = label
        self.dragging = False
        
        self._update_knob()

    def _update_knob(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_w = self.rect.h
        self.knob_rect = pygame.Rect(
            self.rect.x + int(ratio * (self.rect.w - knob_w)),
            self.rect.y,
            knob_w,
            self.rect.h
        )

    def handle_event(self, event):
        """Возвращает True, если ползунок был перетащен (чтобы блокировать другие клики)"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value_from_pos(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value_from_pos(event.pos[0])
            return True
        return False

    def _update_value_from_pos(self, x):
        ratio = max(0.0, min(1.0, (x - self.rect.x) / (self.rect.w - self.knob_rect.w)))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
        self._update_knob()

    def draw(self, surface):
        # Дорожка (фон)
        pygame.draw.rect(surface, (60, 60, 60), self.rect, border_radius=self.rect.h // 2)
        # Заполненная часть дорожки
        fill_w = self.knob_rect.centerx - self.rect.x
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_w, self.rect.h)
        pygame.draw.rect(surface, (100, 100, 100), fill_rect, border_radius=self.rect.h // 2)
        # Ползунок (knob)
        pygame.draw.circle(surface, (220, 220, 220), self.knob_rect.center, self.knob_rect.w // 2)
        
        # Текст с названием и значением
        if self.label:
            pct = int((self.value / self.max_val) * 100)
            text = f"{self.label}: {pct}%"
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, (self.rect.x, self.rect.y - 25))