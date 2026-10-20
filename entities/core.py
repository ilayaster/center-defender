import pygame
from settings import CORE_RADIUS

class Core:
    def __init__(self, screen_w, screen_h, sprite_manager):
        self.x = screen_w // 2
        self.y = screen_h // 2
        self.hitbox_radius = CORE_RADIUS * (screen_h / 1080.0)
        
        self.sprite = sprite_manager.get('core')
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    def update_size(self, screen_w, screen_h, sprite_manager):
        """Пересчитывает размер при смене разрешения"""
        self.x = screen_w // 2
        self.y = screen_h // 2
        self.hitbox_radius = CORE_RADIUS * (screen_h / 1080.0)
        
        self.sprite = sprite_manager.get('core')
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

    def draw(self, surface, show_hitboxes=False):
        surface.blit(self.sprite, self.rect)
        
        if show_hitboxes:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), int(self.hitbox_radius), 2)