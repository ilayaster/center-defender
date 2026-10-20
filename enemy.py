import pygame
import math
import random
from settings import CORE_RADIUS

class Enemy:
    def __init__(self, settings, screen_w, screen_h, sprite_manager):
        self.radius = 15 * (screen_h / 1080)
        self.speed = settings['enemy_speed'] * (screen_h / 1080)
        
        angle = random.uniform(0, 2 * math.pi)
        distance = max(screen_w, screen_h)
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        self.is_dead = False
        
        # Получаем статичную картинку врага
        self.sprite = sprite_manager.get('enemy')
        self.rect = self.sprite.get_rect()

    def update(self, dt, screen_w, screen_h):
        center_x, center_y = screen_w // 2, screen_h // 2
        dx = center_x - self.x
        dy = center_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        core_radius = CORE_RADIUS * (screen_h / 1080)
        if dist < core_radius + self.radius:
            return True 
        return False

    def draw(self, surface):
        # Просто обновляем центр прямоугольника и рисуем
        self.rect.center = (int(self.x), int(self.y))
        surface.blit(self.sprite, self.rect)