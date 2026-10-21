import pygame
import math
import random

# --- НАСТРОЙКИ ХИТБОКСА ENEMY ---
ENEMY_HITBOX_BASE_RADIUS = 20  # Базовый радиус хитбокса врага (масштабируется относительно 1080p)

class Enemy:
    def __init__(self, settings, screen_w, screen_h, sprite_manager):
        self.hitbox_radius = ENEMY_HITBOX_BASE_RADIUS * (screen_h / 1080)
        self.speed = settings['enemy_speed'] * (screen_h / 1080)
        
        angle = random.uniform(0, 2 * math.pi)
        
        # ИСПРАВЛЕНИЕ: расстояние от центра до угла экрана + 50 пикселей запаса
        # Это гарантирует, что враг появится ровно за видимой границей, а не где-то в километре от неё
        distance = math.hypot(screen_w / 2, screen_h / 2) + 50
        
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        self.is_dead = False
        
        self.sprite = sprite_manager.get('enemy')
        self.rect = self.sprite.get_rect()

    def update(self, dt, screen_w, screen_h, core):
        """Обновляет позицию врага и проверяет коллизию с ядром"""
        center_x, center_y = screen_w // 2, screen_h // 2
        dx, dy = center_x - self.x, center_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        # Проверка столкновения с ядром
        if dist < core.hitbox_radius + self.hitbox_radius:
            return True 
        return False

    def draw(self, surface, show_hitboxes=False):
        self.rect.center = (int(self.x), int(self.y))
        surface.blit(self.sprite, self.rect)
        
        if show_hitboxes:
            # Красный цвет для хитбокса врага, чтобы отличать от зеленого хитбокса ядра
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), int(self.hitbox_radius), 2)