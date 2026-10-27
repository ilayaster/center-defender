import pygame
import math
import os

class BaseCore:
    name = "UNKNOWN"
    max_hp = 5
    hitbox_radius_multiplier = 40.0  # Будет умножено на (screen_h / 1080.0)
    
    # Специальные способности (переопределяются в дочерних классах)
    slow_radius_multiplier = 0.0
    slow_factor = 0.5
    explosion_radius_multiplier = 0.0
    regen_time_per_hp = 60.0
    
    sprite_name = "core"
    particle_color = (255, 255, 255)

    def __init__(self, screen_w, screen_h, sprite_manager):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = screen_w // 2
        self.y = screen_h // 2
        
        self._calculate_radii()
        self.current_hp = self.max_hp
        self.regen_timer = 0.0
        self.damage_cooldown = 0.0
        
        self._load_sprite(sprite_manager)
        
        self.explosion_active = False
        self.explosion_timer = 0.0
        self.explosion_duration = 0.3
        self.particles = []
        self.particle_spawn_timer = 0.0

    def _calculate_radii(self):
        scale = self.screen_h / 1080.0
        self.hitbox_radius = self.hitbox_radius_multiplier * scale
        self.slow_radius = self.slow_radius_multiplier * scale
        self.explosion_radius = self.explosion_radius_multiplier * scale

    def _load_sprite(self, sprite_manager):
        self.sprite = sprite_manager.get(self.sprite_name)
        if self.sprite is None:
            sprite_path = f"sprites/{self.sprite_name}.png"
            if os.path.exists(sprite_path):
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                if self.sprite:
                    w, h = self.sprite.get_width(), self.sprite.get_height()
                    self.sprite = pygame.transform.scale(self.sprite, (w * 3, h * 3))
        
        self.rect = self.sprite.get_rect(center=(self.x, self.y)) if self.sprite else pygame.Rect(0, 0, 0, 0)

    def update_size(self, screen_w, screen_h, sprite_manager):
        """Вызывается при изменении размера окна"""
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.x = screen_w // 2
        self.y = screen_h // 2
        self._calculate_radii()
        self._load_sprite(sprite_manager)

    def apply_effects(self, enemies, dt):
        # Регенерация
        if self.current_hp < self.max_hp:
            self.regen_timer += dt
            if self.regen_timer >= self.regen_time_per_hp:
                self.current_hp += 1
                self.regen_timer = 0.0
        
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            
        self._apply_special_effects(enemies, dt)
        
        # Обновление частиц
        for p in self.particles:
            p['y'] += p.get('vy', 0) * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        if self.explosion_active:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.explosion_active = False

    def _apply_special_effects(self, enemies, dt):
        """Переопределяется в дочерних классах (замедление, спавн частиц и т.д.)"""
        pass

    def on_hit(self, enemies):
        if self.damage_cooldown > 0:
            return 0
            
        self.current_hp -= 1
        self.regen_timer = 0.0
        self.damage_cooldown = 0.75
        
        kills = 0
        self.explosion_active = True
        self.explosion_timer = self.explosion_duration
        
        # Базовая логика убийства врагов в радиусе вспышки (одинакова для всех ядер)
        for enemy in enemies:
            if enemy.is_dead:
                continue
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist < self.explosion_radius + enemy.hitbox_radius:
                enemy.is_dead = True
                kills += 1
                
        self._on_hit_special(enemies)
        return kills

    def _on_hit_special(self, enemies):
        """Дополнительная логика при получении урона"""
        pass

    def draw(self, surface, show_hitboxes=False):
        self._draw_special_effects(surface)
        
        if self.sprite:
            surface.blit(self.sprite, self.rect)
            
        if show_hitboxes:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), int(self.hitbox_radius), 2)
            
        if self.explosion_active:
            alpha = int(255 * (self.explosion_timer / self.explosion_duration))
            flash_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 50, alpha), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius))
            surface.blit(flash_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))

    def _draw_special_effects(self, surface):
        """Переопределяется для отрисовки ауры, частиц и т.д."""
        pass