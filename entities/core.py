import pygame
import math
import os
import random

CORE_HITBOX_BASE_RADIUS_PLOSIVE = 40
CORE_HITBOX_BASE_RADIUS_SLOW = 60

class Core:
    def __init__(self, screen_w, screen_h, sprite_manager, core_type='plosive'):
        self.core_type = core_type
        self.x = screen_w // 2
        self.y = screen_h // 2
        
        scale = screen_h / 1080.0
        
        if self.core_type == 'plosive':
            self.max_hp = 5
            self.hitbox_radius = CORE_HITBOX_BASE_RADIUS_PLOSIVE * scale
            self.explosion_radius = 300 * scale
            self.regen_time_per_hp = 60.0
            sprite_name = 'core-plosive'
        else:
            self.max_hp = 3
            self.hitbox_radius = CORE_HITBOX_BASE_RADIUS_SLOW * scale
            self.slow_radius = 280 * scale
            self.slow_factor = 0.5
            self.regen_time_per_hp = 80.0
            self.explosion_radius = 80 * scale
            sprite_name = 'slow-core'
            
        self.current_hp = self.max_hp
        self.regen_timer = 0.0
        self.damage_cooldown = 0.0
        
        self.sprite = sprite_manager.get(sprite_name)
        if self.sprite is None:
            sprite_path = f"sprites/{sprite_name}.png"
            if os.path.exists(sprite_path):
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
        
        if self.sprite:
            original_width = self.sprite.get_width()
            original_height = self.sprite.get_height()
            self.sprite = pygame.transform.scale(
                self.sprite, 
                (original_width * 3, original_height * 3)
            )
            
        self.rect = self.sprite.get_rect(center=(self.x, self.y))
        
        self.explosion_active = False
        self.explosion_timer = 0.0
        self.explosion_duration = 0.3

        self.particles = []
        self.particle_spawn_timer = 0.0

    def apply_effects(self, enemies, dt):
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            
        if self.current_hp < self.max_hp:
            self.regen_timer += dt
            if self.regen_timer >= self.regen_time_per_hp:
                self.current_hp += 1
                self.regen_timer = 0.0
                
        if self.core_type == 'slow':
            for enemy in enemies:
                if enemy.is_dead:
                    continue
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < self.slow_radius + enemy.hitbox_radius:
                    enemy.is_slowed = True
                    enemy.slow_factor = self.slow_factor
                else:
                    enemy.is_slowed = False

            # <-- ИЗМЕНЕНО: Уменьшено количество частиц (было 0.05, стало 0.25)
            self.particle_spawn_timer += dt
            if self.particle_spawn_timer > 0.25:
                self.particle_spawn_timer = 0.0
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(0, self.slow_radius)
                px = self.x + math.cos(angle) * dist
                py = self.y + math.sin(angle) * dist
                self.particles.append({
                    'x': px,
                    'y': py,
                    'vy': -40 - random.random() * 30,
                    'life': 1.0 + random.random() * 0.5,
                    'size': 3 + random.random() * 4
                })

        for p in self.particles:
            p['y'] += p['vy'] * dt
            p['life'] -= dt
        self.particles = [p for p in self.particles if p['life'] > 0]

        if self.explosion_active:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.explosion_active = False

    def on_hit(self, enemies):
        if self.damage_cooldown > 0:
            return 0
            
        self.current_hp -= 1
        self.regen_timer = 0.0
        self.damage_cooldown = 0.75
        
        kills = 0
        if self.core_type == 'plosive':
            self.explosion_active = True
            self.explosion_timer = self.explosion_duration
            for enemy in enemies:
                if enemy.is_dead:
                    continue
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < self.explosion_radius + enemy.hitbox_radius:
                    enemy.is_dead = True
                    kills += 1
        else:
            self.explosion_active = True
            self.explosion_timer = self.explosion_duration
            for enemy in enemies:
                if enemy.is_dead:
                    continue
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < self.explosion_radius + enemy.hitbox_radius:
                    enemy.is_dead = True
                    kills += 1
                    
        return kills

    def draw(self, surface, show_hitboxes=False):
        if self.core_type == 'plosive':
            explosion_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surf, (255, 150, 100, 180), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius), 2)
            surface.blit(explosion_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))
        elif self.core_type == 'slow':
            slow_surf = pygame.Surface((int(self.slow_radius * 2), int(self.slow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(slow_surf, (100, 200, 255, 180), (int(self.slow_radius), int(self.slow_radius)), int(self.slow_radius), 2)
            surface.blit(slow_surf, (int(self.x - self.slow_radius), int(self.y - self.slow_radius)))

        surface.blit(self.sprite, self.rect)
        
        if show_hitboxes:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), int(self.hitbox_radius), 2)
                
        if self.explosion_active:
            alpha = int(255 * (self.explosion_timer / self.explosion_duration))
            flash_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 50, alpha), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius))
            surface.blit(flash_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))

        if self.core_type == 'slow':
            for p in self.particles:
                alpha = int(255 * (p['life'] / 1.5))
                alpha = max(0, min(255, alpha))
                color = (50, 150, 255, alpha)
                p_surf = pygame.Surface((int(p['size']), int(p['size'])), pygame.SRCALPHA)
                p_surf.fill(color)
                surface.blit(p_surf, (int(p['x'] - p['size']/2), int(p['y'] - p['size']/2)))