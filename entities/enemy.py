import pygame
import math
import random

ENEMY_HITBOX_BASE_RADIUS = 45

class Enemy:
    def __init__(self, enemy_type, settings, screen_w, screen_h, sprite_manager):
        self.type = enemy_type
        enemy_stats = settings.get('enemy_stats', {})
        stats = enemy_stats.get(enemy_type, {'hp': 1, 'speed_multiplier': 1.0})
        
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.base_speed = settings['enemy_speed'] * stats['speed_multiplier'] * (screen_h / 1080)
        self.speed = self.base_speed
        
        self.hitbox_radius = ENEMY_HITBOX_BASE_RADIUS * (screen_h / 1080)
        self.is_dead = False
        self.is_slowed = False
        self.slow_factor = 1.0
        
        # <-- НОВОЕ: Кулдаун на получение урона, чтобы один взмах не бил много раз
        self.damage_cooldown = 0.0

        angle = random.uniform(0, 2 * math.pi)
        base_distance = math.hypot(screen_w / 2, screen_h / 2)
        random_offset = random.uniform(0, 150)
        distance = base_distance + 50 + random_offset
        
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        
        self.anim_state = 'jump' if enemy_type == 'enemy-2' else 'walk'
        self.frames = sprite_manager.get_animation(enemy_type, self.anim_state)
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

        # <-- Обновляем кулдаун урона каждый кадр
        if self.damage_cooldown > 0:
            self.damage_cooldown -= dt

        center_x, center_y = screen_w // 2, screen_h // 2
        dx, dy = center_x - self.x, center_y - self.y
        dist = math.hypot(dx, dy)
        
        current_speed = self.speed
        if self.is_slowed:
            current_speed *= self.slow_factor
        
        if self.is_jumping:
            if self.jump_state == 'rest':
                self.jump_timer += dt
                self.visual_y_offset = 0
                self.shadow_scale = 1.0
                
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
                    self.frame_index = 0
                else:
                    if dist > 0:
                        self.x += (dx / dist) * current_speed * dt
                        self.y += (dy / dist) * current_speed * dt
                    
                    height_factor = 4 * progress * (1 - progress)
                    self.visual_y_offset = -height_factor * 40
                    self.shadow_scale = 1.0 - (height_factor * 0.4)
        else:
            self.visual_y_offset = 0
            self.shadow_scale = 1.0
            if dist > 0:
                self.x += (dx / dist) * current_speed * dt
                self.y += (dy / dist) * current_speed * dt

        should_animate = True
        if self.is_jumping and self.jump_state == 'rest':
            should_animate = False
        
        if should_animate:
            self.frame_timer += dt
            if self.frame_timer >= self.frame_duration:
                self.frame_timer = 0.0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

        if dist < core.hitbox_radius + self.hitbox_radius:
            return True 
        return False

    def take_damage(self, amount=1):
        # Если враг уже мертв или находится в кулдауне после удара, урон не проходит
        if self.is_dead or self.damage_cooldown > 0:
            return False
        
        self.hp -= amount
        self.damage_cooldown = 0.2  # 0.2 секунды неуязвимости после получения урона
        
        if self.hp <= 0:
            self.is_dead = True
            return True
        return False

    def draw(self, surface, show_hitboxes=False):
        current_frame = self.frames[self.frame_index] if self.frames else None
        if not current_frame:
            return

        draw_x = int(self.x)
        draw_y = int(self.y) + self.visual_y_offset
        
        self.rect.center = (draw_x, draw_y)
        
        if self.is_jumping:
            shadow_size = int(self.hitbox_radius * 1.2 * self.shadow_scale)
            shadow_surf = pygame.Surface((shadow_size * 2, shadow_size * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_size * 2, shadow_size * 2))
            surface.blit(shadow_surf, (int(self.x) - shadow_size, int(self.y) - shadow_size // 2))

        surface.blit(current_frame, self.rect)
        
        if show_hitboxes:
            hp_bar_width = 40
            hp_bar_height = 6
            hp_ratio = self.hp / self.max_hp
            hp_x = int(self.x) - hp_bar_width // 2
            hp_y = int(self.y) - self.hitbox_radius - 20
            
            pygame.draw.rect(surface, (50, 50, 50), (hp_x, hp_y, hp_bar_width, hp_bar_height))
            fill_color = (0, 255, 0) if hp_ratio > 0.5 else (255, 165, 0) if hp_ratio > 0.25 else (255, 0, 0)
            pygame.draw.rect(surface, fill_color, (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))
            
            color = (100, 100, 255) if self.is_slowed else (255, 0, 0)
            if self.type == 'enemy-2':
                color = (255, 165, 0)
            
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.hitbox_radius), 2)