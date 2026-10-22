import pygame
import math

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
            self.explosion_radius = 300 * scale  # <-- УВЕЛИЧЕН В 2 РАЗА (было 150)
            self.regen_time_per_hp = 60.0
        else:  # slow
            self.max_hp = 3
            self.hitbox_radius = CORE_HITBOX_BASE_RADIUS_SLOW * scale
            self.slow_radius = 280 * scale
            self.slow_factor = 0.5
            self.regen_time_per_hp = 80.0
            
        self.current_hp = self.max_hp
        self.regen_timer = 0.0
        self.damage_cooldown = 0.0
        
        self.sprite = sprite_manager.get('core')
        self.rect = self.sprite.get_rect(center=(self.x, self.y))
        
        self.explosion_active = False
        self.explosion_timer = 0.0
        self.explosion_duration = 0.3  # Чуть дольше вспышка для большого радиуса

    def update_size(self, screen_w, screen_h, sprite_manager):
        self.x = screen_w // 2
        self.y = screen_h // 2
        scale = screen_h / 1080.0
        
        if self.core_type == 'plosive':
            self.hitbox_radius = CORE_HITBOX_BASE_RADIUS_PLOSIVE * scale
            self.explosion_radius = 300 * scale
        else:
            self.hitbox_radius = CORE_HITBOX_BASE_RADIUS_SLOW * scale
            self.slow_radius = 280 * scale
            
        self.sprite = sprite_manager.get('core')
        self.rect = self.sprite.get_rect(center=(self.x, self.y))

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
            for enemy in enemies:
                if enemy.is_dead:
                    continue
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < self.hitbox_radius + enemy.hitbox_radius:
                    enemy.is_dead = True
                    kills += 1
                    
        return kills

    def draw(self, surface, show_hitboxes=False):
        if self.core_type == 'plosive':
            explosion_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(explosion_surf, (255, 100, 50, 30), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius))
            pygame.draw.circle(explosion_surf, (255, 150, 100, 120), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius), 2)
            surface.blit(explosion_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))
        elif self.core_type == 'slow':
            slow_surf = pygame.Surface((int(self.slow_radius * 2), int(self.slow_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(slow_surf, (50, 150, 255, 30), (int(self.slow_radius), int(self.slow_radius)), int(self.slow_radius))
            pygame.draw.circle(slow_surf, (100, 200, 255, 120), (int(self.slow_radius), int(self.slow_radius)), int(self.slow_radius), 2)
            surface.blit(slow_surf, (int(self.x - self.slow_radius), int(self.y - self.slow_radius)))

        surface.blit(self.sprite, self.rect)
        
        if show_hitboxes:
            pygame.draw.circle(surface, (0, 255, 0), (int(self.x), int(self.y)), int(self.hitbox_radius), 2)
                
        if self.explosion_active:
            alpha = int(255 * (self.explosion_timer / self.explosion_duration))
            flash_surf = pygame.Surface((int(self.explosion_radius * 2), int(self.explosion_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 200, 50, alpha), (int(self.explosion_radius), int(self.explosion_radius)), int(self.explosion_radius))
            surface.blit(flash_surf, (int(self.x - self.explosion_radius), int(self.y - self.explosion_radius)))