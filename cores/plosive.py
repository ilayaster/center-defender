import pygame
from cores.base import BaseCore

class PlosiveCore(BaseCore):
    name = "PLOSIVE"
    max_hp = 5
    hitbox_radius_multiplier = 40.0
    explosion_radius_multiplier = 300.0
    regen_time_per_hp = 60.0
    sprite_name = "core-plosive"

    def _draw_special_effects(self, surface):
        # Рисуем постоянное кольцо радиуса взрыва
        explosion_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surf, (255, 150, 100, 180), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius), 2)
        surface.blit(explosion_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))