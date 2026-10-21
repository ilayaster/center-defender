import pygame
import random
import math

class EffectsManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mode = 'OFF'  # OFF, RETRO, RETROIER
        
        self.scanlines = None
        self.vignette = None
        self.crt_mask = None
        
        self._generate_textures()

    def resize(self, width, height):
        """Пересоздает текстуры при смене разрешения"""
        self.width = width
        self.height = height
        self._generate_textures()

    def _generate_textures(self):
        # 1. Scanlines (горизонтальные полосы)
        self.scanlines = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(self.scanlines, (0, 0, 0, 80), (0, y), (self.width, y), 1)
            
        # 2. Vignette (затемнение углов)
        size = 128
        vig_small = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2
        max_dist = math.hypot(cx, cy)
        
        for x in range(size):
            for y in range(size):
                dist = math.hypot(x - cx, y - cy)
                norm_dist = max(0, (dist / max_dist) - 0.2) / 0.8
                alpha = int(220 * (norm_dist ** 1.5))
                if alpha > 0:
                    vig_small.set_at((x, y), (0, 0, 0, min(alpha, 220)))
                    
        self.vignette = pygame.transform.smoothscale(vig_small, (self.width, self.height))

        # 3. CRT Mask (имитация выпуклого стекла)
        self.crt_mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        border_thickness = 15
        pygame.draw.rect(self.crt_mask, (0, 0, 0, 255), 
                         (0, 0, self.width, self.height), border_thickness, border_radius=40)
        for i in range(20):
            alpha = int(100 * (1 - i / 20))
            pygame.draw.rect(self.crt_mask, (0, 0, 0, alpha), 
                             (border_thickness + i, border_thickness + i, 
                              self.width - 2*(border_thickness + i), 
                              self.height - 2*(border_thickness + i)), 
                             1, border_radius=max(0, 40 - i))

    def apply(self, surface):
        """Применяет эффекты к переданному Surface"""
        if self.mode == 'OFF':
            return

        # 1. Scanlines (для обоих режимов)
        surface.blit(self.scanlines, (0, 0))

        # 2. Vignette (для обоих режимов)
        surface.blit(self.vignette, (0, 0))

        # 3. RETROIER специфичные эффекты
        if self.mode == 'RETROIER':
            # Хроматическая аберрация (RGB Split)
            w, h = surface.get_size()
            
            red_shift = pygame.Surface((w, h), pygame.SRCALPHA)
            blue_shift = pygame.Surface((w, h), pygame.SRCALPHA)
            
            temp = surface.copy()
            
            red_shift.blit(temp, (-2, 0))
            red_shift.fill((0, 255, 255, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
            blue_shift.blit(temp, (2, 0))
            blue_shift.fill((255, 255, 0, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
            surface.fill((255, 0, 255, 0), special_flags=pygame.BLEND_RGBA_SUB)
            
            surface.blit(red_shift, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(blue_shift, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            # CRT Mask
            surface.blit(self.crt_mask, (0, 0))