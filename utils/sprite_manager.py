import pygame
import os

# Ищем папку sprites относительно корня проекта (на уровень выше utils)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")

class SpriteManager:
    def __init__(self):
        self.sprites = {}

    def load(self, name, filename, target_size=None):
        filepath = os.path.join(SPRITES_DIR, filename)
        try:
            img = pygame.image.load(filepath).convert_alpha()
            if target_size:
                # Обычный scale для четкого Nearest Neighbor
                img = pygame.transform.scale(img, target_size)
            self.sprites[name] = img
        except pygame.error as e:
            print(f"Warning: Could not load sprite '{filepath}'. Error: {e}")
            size = target_size if target_size else (64, 64)
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((255, 0, 255)) # Розовый квадрат-заглушка
            self.sprites[name] = fallback

    def get(self, name):
        return self.sprites.get(name)