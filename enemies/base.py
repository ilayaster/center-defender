import pygame
import math
import random

class BaseEnemy:
    # --- Базовые параметры (переопределяются в дочерних классах) ---
    enemy_type = "unknown"
    display_name = "Unknown"
    max_hp = 1
    speed_multiplier = 1.0
    hitbox_radius_multiplier = 20.0
    
    anim_state = 'walk'
    frame_duration = 0.15
    
    hitbox_color = (255, 0, 0)
    slowed_hitbox_color = (100, 100, 255)

    def __init__(self, settings, screen_w, screen_h, sprite_manager):
        self.sprite_manager = sprite_manager
        
        self.hp = self.max_hp
        self.base_speed = settings['enemy_speed'] * self.speed_multiplier * (screen_h / 1080.0)
        self.speed = self.base_speed
        
        self.hitbox_radius = self.hitbox_radius_multiplier * (screen_h / 1080.0)
        self.is_dead = False
        self.just_died = False
        self.is_slowed = False
        self.slow_factor = 1.0
        
        self.damage_cooldown = 0.0
        self.damage_flash_timer = 0.0

        # Спавн за пределами экрана
        angle = random.uniform(0, 2 * math.pi)
        base_distance = math.hypot(screen_w / 2, screen_h / 2)
        random_offset = random.uniform(0, 150)
        distance = base_distance + 50 + random_offset
        
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        
        self.frames = self.sprite_manager.get_animation(self.enemy_type, self.anim_state)
        self.frame_index = 0
        self.frame_timer = 0.0
        
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

        # Делегируем специфичное движение подклассам
        self.apply_movement(dt, core)

        dist_to_core = math.hypot(core.x - self.x, core.y - self.y)
        if dist_to_core <= self.hitbox_radius + core.hitbox_radius:
            return True
            
        return False

    def apply_movement(self, dt, core):
        """Стандартное движение к ядру. Переопределяется для Jumper."""
        current_speed = self.speed * self.slow_factor
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

    def take_damage(self, amount=1):
        if self.is_dead or self.damage_cooldown > 0:
            return False
        
        self.hp -= amount
        self.damage_cooldown = 0.2
        self.damage_flash_timer = 0.15
        
        if self.hp <= 0:
            self.is_dead = True
            self.just_died = True
            return True
        return False

    def draw(self, surface, show_hitboxes=False):
        current_frame = self.frames[self.frame_index] if self.frames else None
        if not current_frame:
            return

        draw_x = int(self.x)
        draw_y = int(self.y) + self.visual_y_offset
        self.rect.center = (draw_x, draw_y)
        
        # Эффект получения урона
        if self.damage_flash_timer > 0:
            damaged_frames = self.sprite_manager.get_animation(self.enemy_type, "damaged")
            if damaged_frames and len(damaged_frames) > 0:
                surface.blit(damaged_frames[0], self.rect)
            else:
                flash_surf = current_frame.copy()
                flash_surf.fill((255, 80, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(flash_surf, self.rect)
        else:
            surface.blit(current_frame, self.rect)
        
        # Полоска здоровья
        if self.hp < self.max_hp:
            hp_bar_width = 40
            hp_bar_height = 6
            hp_ratio = self.hp / self.max_hp
            hp_x = int(self.x) - hp_bar_width // 2
            hp_y = int(self.y) - self.hitbox_radius - 15
            
            pygame.draw.rect(surface, (50, 50, 50), (hp_x, hp_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(surface, (255, 0, 0), (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))

        # Хитбоксы (цвета берутся из атрибутов класса)
        if show_hitboxes:
            color = self.slowed_hitbox_color if self.is_slowed else self.hitbox_color
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.hitbox_radius), 2)