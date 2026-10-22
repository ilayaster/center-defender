import pygame
import math
import random

ENEMY_HITBOX_BASE_RADIUS = 20

class Enemy:
    def __init__(self, settings, screen_w, screen_h, sprite_manager):
        self.hitbox_radius = ENEMY_HITBOX_BASE_RADIUS * (screen_h / 1080)
        self.base_speed = settings['enemy_speed'] * (screen_h / 1080)
        self.speed = self.base_speed
        
        angle = random.uniform(0, 2 * math.pi)
        distance = math.hypot(screen_w / 2, screen_h / 2) + 50
        
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        self.is_dead = False
        
        self.is_slowed = False
        self.slow_factor = 1.0
        
        self.sprite = sprite_manager.get('enemy')
        self.rect = self.sprite.get_rect()

    def update(self, dt, screen_w, screen_h, core):
        if self.is_dead:
            return False

        center_x, center_y = screen_w // 2, screen_h // 2
        dx, dy = center_x - self.x, center_y - self.y
        dist = math.hypot(dx, dy)
        
        current_speed = self.speed
        if self.is_slowed:
            current_speed *= self.slow_factor
            
        if dist > 0:
            self.x += (dx / dist) * current_speed * dt
            self.y += (dy / dist) * current_speed * dt

        if dist < core.hitbox_radius + self.hitbox_radius:
            return True 
        return False

    def draw(self, surface, show_hitboxes=False):
        self.rect.center = (int(self.x), int(self.y))
        # <-- УДАЛЕНО затемнение спрайта. Рисуем как есть.
        surface.blit(self.sprite, self.rect)
        
        if show_hitboxes:
            color = (100, 100, 255) if self.is_slowed else (255, 0, 0)
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.hitbox_radius), 2)