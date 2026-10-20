import pygame
import os
from settings import CORE_COLOR

class AssetManager:
    """Управляет загрузкой спрайтов и шрифтов"""
    
    def __init__(self, sprite_manager, screen):
        self.sprite_manager = sprite_manager
        self.screen = screen
        self.font_small = None
        self.font_medium = None
        self.font_large = None
    
    def load_sprites(self):
        """Загружает спрайты с масштабированием под экран"""
        scale_factor = self.screen.get_height() / 1080.0
        core_size = int(128 * scale_factor)
        enemy_size = int(48 * scale_factor)
        
        self.sprite_manager.load('core', 'core.png', (core_size, core_size))
        self.sprite_manager.load('enemy', 'enemy.png', (enemy_size, enemy_size))
    
    def load_fonts(self):
        """Загружает шрифты (пиксельный или запасной)"""
        sh = self.screen.get_height()
        size_small = max(12, min(16, sh // 60))
        size_medium = max(14, min(20, sh // 45))
        size_large = max(24, min(36, sh // 25))
        
        try:
            font_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                "fonts", "pixel.ttf"
            )
            self.font_small = pygame.font.Font(font_path, size_small)
            self.font_medium = pygame.font.Font(font_path, size_medium)
            self.font_large = pygame.font.Font(font_path, size_large)
        except FileNotFoundError:
            self.font_small = pygame.font.SysFont("courier", size_small, bold=True)
            self.font_medium = pygame.font.SysFont("courier", size_medium, bold=True)
            self.font_large = pygame.font.SysFont("courier", size_large, bold=True)
    
    def load_all(self):
        """Загружает все ресурсы"""
        self.load_sprites()
        self.load_fonts()