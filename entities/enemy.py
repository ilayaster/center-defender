import pygame
import math
import random

ENEMY_HITBOX_BASE_RADIUS = 20

class Enemy:
    def __init__(self, enemy_type, settings, screen_w, screen_h, sprite_manager):
        self.type = enemy_type
        self.sprite_manager = sprite_manager
        enemy_stats = settings.get('enemy_stats', {})
        stats = enemy_stats.get(enemy_type, {'hp': 1, 'speed_multiplier': 1.0})
        
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.base_speed = settings['enemy_speed'] * stats['speed_multiplier'] * (screen_h / 1080)
        self.speed = self.base_speed
        
        self.hitbox_radius = ENEMY_HITBOX_BASE_RADIUS * (screen_h / 1080)
        self.is_dead = False
        self.just_died = False  # <-- НОВОЕ: Флаг для спавна частиц
        self.is_slowed = False
        self.slow_factor = 1.0
        
        self.damage_cooldown = 0.0
        self.damage_flash_timer = 0.0

        angle = random.uniform(0, 2 * math.pi)
        base_distance = math.hypot(screen_w / 2, screen_h / 2)
        random_offset = random.uniform(0, 150)
        distance = base_distance + 50 + random_offset
        
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        
        self.anim_state = 'jump' if enemy_type == 'enemy-2' else 'walk'
        self.frames = self.sprite_manager.get_animation(enemy_type, self.anim_state)
        self.frame_index = 0
        self.frame_timer = 0.0
        self.frame_duration = 0.15
        
        self.is_jumping = (enemy_type == 'enemy-2')
        
        self.jump_state = 'rest'
        self.jump_timer = 0.0
        self.rest_duration = 1.5
        self.jump_duration = 0.5
        
        self.visual_y_offset = 0
        self.shadow_scale = 1.0

        self.rect = self.frames[0].get_rect() if self.frames else pygame.Rect(0, 0, 32, 32)

    def update(self, dt, screen_w, screen_h, core):
        if self.is_dead:
            return False

        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt
            
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= dt

        if self.is_jumping:
            if self.jump_state == 'rest':
                self.jump_timer += dt
                self.visual_y_offset = 0
                self.shadow_scale = 1.0
                self.frame_index = 1 
                
                if self.jump_timer >= self.rest_duration:
                    self.jump_state = 'jump'
                    self.jump_timer = 0.0
                    self.frame_index = 0
            elif self.jump_state == 'jump':
                self.jump_timer += dt
                progress = self.jump_timer / self.jump_duration
                
                if progress >= 1.0:
                    self.jump_state = 'rest'
                    self.jump_timer = 0.0
                    self.visual_y_offset = 0
                    self.shadow_scale = 1.0
                    self.frame_index = 1
                else:
                    current_speed = self.base_speed * self.slow_factor
                    
                    dx = core.x - self.x
                    dy = core.y - self.y
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        self.x += (dx / dist) * current_speed * dt
                        self.y += (dy / dist) * current_speed * dt

                    height_factor = 4 * progress * (1 - progress)
                    self.visual_y_offset = -height_factor * 40
                    self.shadow_scale = 1.0 - (height_factor * 0.4)
                    
                    self.frame_timer += dt
                    if self.frame_timer >= self.frame_duration:
                        self.frame_timer = 0.0
                        self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            current_speed = self.speed * self.slow_factor
            if self.is_slowed:
                current_speed = self.base_speed * self.slow_factor

            dx = core.x - self.x
            dy = core.y - self.y
            dist = math.hypot(dx, dy)
            
            if dist > 0:
                self.x += (dx / dist) * current_speed * dt
                self.y += (dy / dist) * current_speed * dt

            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

        dist_to_core = math.hypot(core.x - self.x, core.y - self.y)
        if dist_to_core <= self.hitbox_radius + core.hitbox_radius:
            return True
            
        return False

    def take_damage(self, amount=1):
        if self.is_dead or self.damage_cooldown > 0:
            return False
        
        self.hp -= amount
        self.damage_cooldown = 0.2
        self.damage_flash_timer = 0.15
        
        if self.hp <= 0:
            self.is_dead = True
            self.just_died = True  # <-- НОВОЕ: Сигнал для спавна частиц
            return True
        return False

    def draw(self, surface, show_hitboxes=False):
        current_frame = self.frames[self.frame_index] if self.frames else None
        if not current_frame:
            return

        draw_x = int(self.x)
        draw_y = int(self.y) + self.visual_y_offset
        
        self.rect.center = (draw_x, draw_y)
        
        if self.damage_flash_timer > 0:
            damaged_frames = self.sprite_manager.get_animation(self.type, "damaged")
            if damaged_frames and len(damaged_frames) > 0:
                surface.blit(damaged_frames[0], self.rect)
            else:
                flash_surf = current_frame.copy()
                flash_surf.fill((255, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(flash_surf, self.rect)
        else:
            surface.blit(current_frame, self.rect)
        
        if self.hp < self.max_hp:
            hp_bar_width = 40
            hp_bar_height = 6
            hp_ratio = self.hp / self.max_hp
            hp_x = int(self.x) - hp_bar_width // 2
            hp_y = int(self.y) - self.hitbox_radius - 15
            
            pygame.draw.rect(surface, (50, 50, 50), (hp_x, hp_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(surface, (255, 0, 0), (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))

        if show_hitboxes:
            color = (100, 100, 255) if self.is_slowed else (255, 0, 0)
            if self.type == 'enemy-2':
                color = (255, 165, 0)
            
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.hitbox_radius), 2)