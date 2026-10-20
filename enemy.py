import pygame
import math
import random
from settings import ENEMY_COLOR, CORE_RADIUS

class Enemy:
    def __init__(self, settings, screen_w, screen_h):
        self.radius = 15
        self.speed = settings['enemy_speed']
        
        angle = random.uniform(0, 2 * math.pi)
        distance = max(screen_w, screen_h)
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        self.is_dead = False

    def update(self, dt, screen_w, screen_h):
        center_x, center_y = screen_w // 2, screen_h // 2
        dx = center_x - self.x
        dy = center_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        if dist < CORE_RADIUS + self.radius:
            return True 
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, ENEMY_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)