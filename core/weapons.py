import pygame
import math
from settings import WEAPONS, DEFAULT_WEAPON

class WeaponManager:
    def __init__(self):
        self.current_weapon_key = DEFAULT_WEAPON
        self.stats = WEAPONS[self.current_weapon_key]
        self.reload_font = pygame.font.Font(None, 18)
        self.reset_timers()

    def set_weapon(self, weapon_key):
        if weapon_key in WEAPONS:
            self.current_weapon_key = weapon_key
            self.stats = WEAPONS[self.current_weapon_key]
            self.reset_timers()

    def reset_timers(self):
        self.cooldown_timer = 0.0
        self.windup_timer = 0.0
        self.is_swinging = False
        self.swing_timer = 0.0
        self.attack_requested = False

        self.max_ammo = self.stats.get('magazine_size', 0)
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.reload_timer = 0.0

    def request_attack(self):
        if self.is_reloading or self.cooldown_timer > 0 or self.is_swinging or self.windup_timer > 0:
            return False

        if self.max_ammo > 0:
            if self.current_ammo <= 0:
                self.is_reloading = True
                self.reload_timer = self.stats['reload_duration']
                return False
            self.current_ammo -= 1

        self.windup_timer = self.stats['windup_duration']
        self.attack_requested = True
        return True

    def request_reload(self):
        """Ручная перезарядка (например, по клавише R)"""
        if self.max_ammo > 0 and self.current_ammo < self.max_ammo and not self.is_reloading:
            self.is_reloading = True
            self.reload_timer = self.stats['reload_duration']

    def _perform_attack(self, mouse_pos, enemies):
        hits = 0
        weapon_range = self.stats['range']
        for enemy in enemies:
            if not enemy.is_dead:
                dist = math.hypot(mouse_pos[0] - enemy.x, mouse_pos[1] - enemy.y)
                if dist <= (weapon_range + enemy.hitbox_radius):
                    enemy.is_dead = True
                    hits += 1
        
        self.is_swinging = True
        self.swing_timer = self.stats['swing_duration']
        self.cooldown_timer = self.stats['cooldown']
        self.attack_requested = False

        if self.max_ammo > 0 and self.current_ammo == 0:
            self.is_reloading = True
            self.reload_timer = self.stats['reload_duration']

        return hits

    def update(self, dt, mouse_pos, enemies):
        hits = 0
        
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.max_ammo
                
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        if self.attack_requested:
            if self.windup_timer > 0:
                self.windup_timer -= dt
                if self.windup_timer <= 0:
                    self.windup_timer = 0
                    hits = self._perform_attack(mouse_pos, enemies)
            else:
                hits = self._perform_attack(mouse_pos, enemies)
            
        if self.is_swinging:
            self.swing_timer -= dt
            if self.swing_timer <= 0:
                self.is_swinging = False
                
        return hits

    def draw(self, surface, mouse_pos):
        mx, my = int(mouse_pos[0]), int(mouse_pos[1])
        stats = self.stats
        base_radius = max(12, int(stats['range'] * 0.25))

        if self.is_reloading:
            pct = 1.0 - (self.reload_timer / self.stats['reload_duration'])
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (0, 255, 255), (mx, my), current_r, 3)

        elif self.cooldown_timer > 0:
            pct = self.cooldown_timer / stats['cooldown']
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (255, 200, 0), (mx, my), current_r, 3)

        if self.windup_timer > 0:
            pct = 1.0 - (self.windup_timer / stats['windup_duration'])
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                r, g, b = stats['swing_color']
                pygame.draw.circle(surface, (r, g, b), (mx, my), current_r, 3)

        if self.max_ammo > 0:
            dot_r = 3
            spacing = 10
            total_w = (self.max_ammo - 1) * spacing
            start_x = mx - total_w // 2
            y_pos = my - 25
            
            if self.is_reloading:
                reload_text = self.reload_font.render("RELOADING", True, (0, 255, 255))
                text_rect = reload_text.get_rect(center=(mx, y_pos - 15))
                surface.blit(reload_text, text_rect)

            reload_pct = 0.0
            if self.is_reloading:
                reload_pct = 1.0 - (self.reload_timer / self.stats['reload_duration'])
                
            loaded_bullets = int(reload_pct * self.max_ammo)
            fractional = (reload_pct * self.max_ammo) - loaded_bullets

            for i in range(self.max_ammo):
                x_pos = start_x + i * spacing
                if i < self.current_ammo:
                    pygame.draw.circle(surface, (255, 255, 255), (x_pos, y_pos), dot_r)
                elif self.is_reloading:
                    idx_in_reload = i - self.current_ammo
                    if idx_in_reload < loaded_bullets:
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), dot_r)
                    elif idx_in_reload == loaded_bullets:
                        current_r = max(1, int(dot_r * fractional))
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), current_r)
                    else:
                        pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)
                else:
                    pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)

        if self.is_swinging:
            progress = 1.0 - (self.swing_timer / stats['swing_duration'])
            current_range = int(stats['range'] * (0.4 + 0.6 * progress))
            alpha_factor = 1.0 - progress
            
            r = min(255, int(stats['swing_color'][0] * alpha_factor) + 50)
            g = min(255, int(stats['swing_color'][1] * alpha_factor) + 50)
            b = min(255, int(stats['swing_color'][2] * alpha_factor) + 50)
            
            pygame.draw.circle(surface, (r, g, b), (mx, my), current_range, 5)
        else:
            color = stats['cursor_color']
            pygame.draw.line(surface, color, (mx-10, my), (mx+10, my), 2)
            pygame.draw.line(surface, color, (mx, my-10), (mx, my+10), 2)
            pygame.draw.circle(surface, (255, 50, 50), (mx, my), 3)