import pygame
import math
import random
from cores.base import BaseCore

class SlowCore(BaseCore):
    name = "SLOW"
    max_hp = 3
    hitbox_radius_multiplier = 60.0
    slow_radius_multiplier = 280.0
    slow_factor = 0.5
    explosion_radius_multiplier = 80.0
    regen_time_per_hp = 80.0
    sprite_name = "slow-core"
    particle_color = (50, 150, 255)

    def _apply_special_effects(self, enemies, dt):
        # Замедление врагов в радиусе
        for enemy in enemies:
            if enemy.is_dead:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < self.slow_radius + enemy.hitbox_radius:
                enemy.is_slowed = True
                enemy.slow_factor = self.slow_factor
            else:
                enemy.is_slowed = False

        # Спавн частиц ауры
        self.particle_spawn_timer += dt
        if self.particle_spawn_timer > 0.25:
            self.particle_spawn_timer = 0.0
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, self.slow_radius)
            px = self.x + math.cos(angle) * dist
            py = self.y + math.sin(angle) * dist
            self.particles.append({
                'x': px, 'y': py,
                'vy': -40 - random.random() * 30,
                'life': 1.0 + random.random() * 0.5,
                'size': 3 + random.random() * 4
            })

    def _draw_special_effects(self, surface):
        # Кольцо замедления
        slow_surf = pygame.Surface((int(self.slow_radius * 2), int(self.slow_radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(slow_surf, (100, 200, 255, 180), (int(self.slow_radius), int(self.slow_radius)), int(self.slow_radius), 2)
        surface.blit(slow_surf, (int(self.x - self.slow_radius), int(self.y - self.slow_radius)))
        
        # Отрисовка частиц
        for p in self.particles:
            alpha = int(255 * (p['life'] / 1.5))
            alpha = max(0, min(255, alpha))
            color = (*self.particle_color[:3], alpha)
            p_surf = pygame.Surface((int(p['size']), int(p['size'])), pygame.SRCALPHA)
            p_surf.fill(color)
            surface.blit(p_surf, (int(p['x'] - p['size']/2), int(p['y'] - p['size']/2)))