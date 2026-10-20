import pygame
from settings import BTN_COLOR, BTN_HOVER, BTN_TEXT

class DropdownButton:
    def __init__(self, x, y, width, height, text, options, font, screen_width, enabled=True, max_visible=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.options = options
        self.font = font
        self.color = BTN_COLOR
        self.hover_color = BTN_HOVER
        self.disabled_color = (40, 40, 40)
        self.disabled_text_color = (100, 100, 100)
        self.enabled = enabled
        self.is_open = False
        
        self.max_visible = min(max_visible, len(options))
        self.scroll_offset = 0
        self.direction = 'right' if x + width * 2 <= screen_width else 'left'
        
        self.option_height = height
        self.total_options_height = self.max_visible * self.option_height
        self.y_offset = (self.rect.height - self.total_options_height) / 2
        
    def get_visible_rects(self):
        rects = []
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible, len(self.options))
        for i in range(start_idx, end_idx):
            opt_y = int(self.rect.y + self.y_offset + (i - start_idx) * self.option_height)
            opt_x = self.rect.x + self.rect.width if self.direction == 'right' else self.rect.x - self.rect.width
            rects.append((self.options[i], pygame.Rect(opt_x, opt_y, self.rect.width, self.option_height), i))
        return rects

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.disabled_color if not self.enabled else (self.hover_color if self.rect.collidepoint(mouse_pos) else self.color)
        text_color = self.disabled_text_color if not self.enabled else BTN_TEXT
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        text_rect.x -= 10
        surface.blit(text_surf, text_rect)
        
        # Стрелочка
        arrow_points = []
        offset = -15 if self.direction == 'right' else 15
        base_x = self.rect.right + offset if self.direction == 'right' else self.rect.left + offset
        
        if self.is_open:
            arrow_points = [(base_x, self.rect.centery - 5), (base_x, self.rect.centery + 5), (base_x - (10 if self.direction == 'right' else -10), self.rect.centery)]
        else:
            arrow_points = [(base_x, self.rect.centery - 5), (base_x, self.rect.centery + 5), (base_x + (10 if self.direction == 'right' else -10), self.rect.centery)]
        pygame.draw.polygon(surface, text_color, arrow_points)

        if self.is_open and self.enabled:
            visible_rects = self.get_visible_rects()
            if visible_rects:
                min_y = visible_rects[0][1].y
                max_y = visible_rects[-1][1].bottom
                bg_x = self.rect.x + self.rect.width if self.direction == 'right' else self.rect.x - self.rect.width
                bg_rect = pygame.Rect(bg_x, min_y, self.rect.width, max_y - min_y)
                
                pygame.draw.rect(surface, (40, 40, 45), bg_rect, border_radius=8)
                pygame.draw.rect(surface, (120, 120, 120), bg_rect, 2, border_radius=8)
                
                # Скроллбар
                if len(self.options) > self.max_visible:
                    sb_x, sb_w, sb_h, sb_y = bg_rect.right - 10, 4, bg_rect.height - 10, bg_rect.y + 5
                    pygame.draw.rect(surface, (60, 60, 60), (sb_x, sb_y, sb_w, sb_h), border_radius=2)
                    max_offset = len(self.options) - self.max_visible
                    if max_offset > 0:
                        thumb_h = max(20, sb_h * (self.max_visible / len(self.options)))
                        thumb_y = sb_y + (sb_h - thumb_h) * (self.scroll_offset / max_offset)
                        pygame.draw.rect(surface, (150, 150, 150), (sb_x, thumb_y, sb_w, thumb_h), border_radius=2)

                for opt_text, opt_rect, _ in visible_rects:
                    opt_color = self.hover_color if opt_rect.collidepoint(mouse_pos) else (50, 50, 55)
                    pygame.draw.rect(surface, opt_color, opt_rect, border_radius=4)
                    opt_surf = self.font.render(opt_text, True, BTN_TEXT)
                    opt_rect_text = opt_surf.get_rect(center=opt_rect.center)
                    if len(self.options) > self.max_visible: opt_rect_text.x -= 5
                    surface.blit(opt_surf, opt_rect_text)

    def handle_event(self, event):
        if not self.enabled: return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return None
            elif self.is_open:
                for opt_text, opt_rect, _ in self.get_visible_rects():
                    if opt_rect.collidepoint(event.pos):
                        self.is_open = False
                        self.scroll_offset = 0
                        return opt_text
                self.is_open = False
                self.scroll_offset = 0
                return None
        elif event.type == pygame.MOUSEWHEEL and self.is_open:
            visible_rects = self.get_visible_rects()
            if visible_rects:
                min_y, max_y = visible_rects[0][1].y, visible_rects[-1][1].bottom
                bg_x = self.rect.x + self.rect.width if self.direction == 'right' else self.rect.x - self.rect.width
                if pygame.Rect(bg_x, min_y, self.rect.width, max_y - min_y).collidepoint(pygame.mouse.get_pos()):
                    max_offset = len(self.options) - self.max_visible
                    self.scroll_offset = max(0, min(self.scroll_offset - event.y, max_offset))
        return None