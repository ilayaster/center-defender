import math
from enemies.base import BaseEnemy

class Jumper(BaseEnemy):
    enemy_type = "enemy-2"
    display_name = "Jumper"
    max_hp = 2
    speed_multiplier = 1.5
    hitbox_radius_multiplier = 20.0
    anim_state = 'jump'
    frame_duration = 0.15
    hitbox_color = (255, 165, 0)  # Оранжевый
    slowed_hitbox_color = (100, 100, 255)

    def __init__(self, settings, screen_w, screen_h, sprite_manager):
        super().__init__(settings, screen_w, screen_h, sprite_manager)
        self.jump_state = 'rest'
        self.jump_timer = 0.0
        self.rest_duration = 1.5
        self.jump_duration = 0.5

    def apply_movement(self, dt, core):
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