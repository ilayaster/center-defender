import pygame
from settings import BTN_COLOR, BTN_HOVER, BTN_TEXT

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = BTN_COLOR
        self.hover_color = BTN_HOVER

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, BTN_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

class DropdownButton:
    def __init__(self, x, y, width, height, text, options, font, screen_width, enabled=True):
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
        
        # Smart direction: open right if fits, otherwise left
        self.direction = 'right' if x + width * 2 <= screen_width else 'left'
        
        # --- NEW: Calculate vertical offset to center the dropdown relative to the button ---
        self.option_height = height
        self.total_options_height = len(options) * self.option_height
        self.y_offset = (self.rect.height - self.total_options_height) / 2
        
        self.option_rects = []
        for i, opt in enumerate(options):
            opt_y = int(self.rect.y + self.y_offset + i * self.option_height)
            if self.direction == 'right':
                opt_x = self.rect.x + self.rect.width
            else:
                opt_x = self.rect.x - self.rect.width
            rect = pygame.Rect(opt_x, opt_y, self.rect.width, self.option_height)
            self.option_rects.append((opt, rect))

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        if not self.enabled:
            current_color = self.disabled_color
            text_color = self.disabled_text_color
        else:
            current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
            text_color = BTN_TEXT
            
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        text_rect.x -= 10 
        surface.blit(text_surf, text_rect)
        
        # Arrow indicator
        arrow_points = []
        if self.is_open:
            if self.direction == 'right':
                arrow_points = [(self.rect.right - 15, self.rect.centery - 5), 
                                (self.rect.right - 15, self.rect.centery + 5), 
                                (self.rect.right - 25, self.rect.centery)]
            else:
                arrow_points = [(self.rect.left + 15, self.rect.centery - 5), 
                                (self.rect.left + 15, self.rect.centery + 5), 
                                (self.rect.left + 25, self.rect.centery)]
        else:
            if self.direction == 'right':
                arrow_points = [(self.rect.right - 25, self.rect.centery - 5), 
                                (self.rect.right - 25, self.rect.centery + 5), 
                                (self.rect.right - 15, self.rect.centery)]
            else:
                arrow_points = [(self.rect.left + 25, self.rect.centery - 5), 
                                (self.rect.left + 25, self.rect.centery + 5), 
                                (self.rect.left + 15, self.rect.centery)]
        pygame.draw.polygon(surface, text_color, arrow_points)

        if self.is_open and self.enabled:
            if self.option_rects:
                min_y = self.option_rects[0][1].y
                max_y = self.option_rects[-1][1].bottom
                if self.direction == 'right':
                    bg_x = self.rect.x + self.rect.width
                else:
                    bg_x = self.rect.x - self.rect.width
                bg_rect = pygame.Rect(bg_x, min_y, self.rect.width, max_y - min_y)
                pygame.draw.rect(surface, (40, 40, 45), bg_rect, border_radius=8)
                pygame.draw.rect(surface, (120, 120, 120), bg_rect, 2, border_radius=8)
            
            for opt_text, opt_rect in self.option_rects:
                opt_color = self.hover_color if opt_rect.collidepoint(mouse_pos) else (50, 50, 55)
                pygame.draw.rect(surface, opt_color, opt_rect, border_radius=4)
                opt_surf = self.font.render(opt_text, True, BTN_TEXT)
                opt_rect_text = opt_surf.get_rect(center=opt_rect.center)
                surface.blit(opt_surf, opt_rect_text)

    def handle_event(self, event):
        if not self.enabled:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return None
            elif self.is_open:
                for opt_text, opt_rect in self.option_rects:
                    if opt_rect.collidepoint(mouse_pos):
                        self.is_open = False
                        return opt_text 
                self.is_open = False 
                return None
        return None