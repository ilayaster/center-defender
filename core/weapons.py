import pygame
import math
from settings import WEAPONS, DEFAULT_WEAPON

class WeaponManager:
    def __init__(self):
        self.current_weapon_key = DEFAULT_WEAPON
        self.stats = WEAPONS[self.current_weapon_key]
        self.volume = 0.5
        self.sounds = {}
        self._load_sounds()
        self._load_font()
        self.reset_timers()

    def _load_font(self):
        """Загружает пиксельный шрифт для UI оружия"""
        try:
            self.reload_font = pygame.font.Font('fonts/pixel.ttf', 8)
        except:
            self.reload_font = pygame.font.Font(None, 14)

    def _load_sounds(self):
        """Загружает звуковые эффекты из папки sfx"""
        try:
            self.sounds['sword_swing'] = pygame.mixer.Sound('sfx/sword_swing.wav')
            self.sounds['hammer_hit'] = pygame.mixer.Sound('sfx/hammer_hit.wav')
            self.sounds['empty_gun'] = pygame.mixer.Sound('sfx/empty_gun.wav')
            self.sounds['reloaded'] = pygame.mixer.Sound('sfx/reloaded.wav')
            self.sounds['gun_shot'] = pygame.mixer.Sound('sfx/gun_shot.wav')
            self.set_volume(self.volume)
        except pygame.error:
            print("Warning: Could not load some sound files. Check 'sfx' folder.")

    def set_volume(self, vol):
        """Устанавливает громкость для всех звуков"""
        self.volume = max(0.0, min(1.0, vol))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def _play_sound(self, sound_name):
        """Безопасное воспроизведение звука"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

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
        self.attack_pos = (0, 0)

        self.max_ammo = self.stats.get('magazine_size', 0)
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.reload_timer = 0.0

    def request_attack(self, mouse_pos):
        """Запрашивает атаку. attack_pos будет обновляться во время windup."""
        if self.is_reloading:
            self._play_sound('empty_gun')
            return False
            
        if self.cooldown_timer > 0 or self.is_swinging or self.windup_timer > 0:
            return False

        if self.max_ammo > 0:
            if self.current_ammo <= 0:
                self.is_reloading = True
                self.reload_timer = self.stats['reload_duration']
                self._play_sound('empty_gun')
                return False
            self.current_ammo -= 1

        self.windup_timer = self.stats['windup_duration']
        self.attack_requested = True
        return True

    def request_reload(self):
        """Ручная перезарядка (клавиша R)"""
        if self.max_ammo > 0 and self.current_ammo < self.max_ammo and not self.is_reloading:
            self.is_reloading = True
            bullets_to_reload = self.max_ammo - self.current_ammo
            self.reload_timer = self.stats['reload_duration'] * (bullets_to_reload / self.max_ammo)

    def _perform_attack(self, enemies):
        """Наносит урон по площади, используя self.attack_pos"""
        hits = 0
        weapon_range = self.stats['range']
        mx, my = self.attack_pos
        
        for enemy in enemies:
            if not enemy.is_dead:
                dist = math.hypot(mx - enemy.x, my - enemy.y)
                if dist <= (weapon_range + enemy.hitbox_radius):
                    # Наносим урон через take_damage
                    if enemy.take_damage(1):
                        hits += 1
        
        self.is_swinging = True
        self.swing_timer = self.stats['swing_duration']
        self.cooldown_timer = self.stats['cooldown']
        self.attack_requested = False

        if self.current_weapon_key == 'sword':
            self._play_sound('sword_swing')
        elif self.current_weapon_key == 'hammer':
            self._play_sound('hammer_hit')
        elif self.current_weapon_key == 'pistol':
            self._play_sound('gun_shot')

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
                if self.current_weapon_key == 'pistol':
                    self._play_sound('reloaded')
                
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        if self.attack_requested:
            if self.windup_timer > 0:
                self.attack_pos = mouse_pos
                self.windup_timer -= dt
                if self.windup_timer <= 0:
                    self.windup_timer = 0
                    hits = self._perform_attack(enemies)
            else:
                self.attack_pos = mouse_pos
                hits = self._perform_attack(enemies)
            
        if self.is_swinging:
            self.swing_timer -= dt
            if self.swing_timer <= 0:
                self.is_swinging = False
                
        return hits

    def draw(self, surface, current_mouse_pos):
        """Отрисовывает курсор, эффекты и UI оружия"""
        cmx, cmy = int(current_mouse_pos[0]), int(current_mouse_pos[1])
        stats = self.stats
        base_radius = max(12, int(stats['range'] * 0.25))

        # 1. АТАКА (Взмах)
        if self.is_swinging:
            mx, my = int(self.attack_pos[0]), int(self.attack_pos[1])
            progress = 1.0 - (self.swing_timer / stats['swing_duration'])
            current_range = int(stats['range'] * (0.4 + 0.6 * progress))
            alpha_factor = 1.0 - progress
            
            r = min(255, int(stats['swing_color'][0] * alpha_factor) + 50)
            g = min(255, int(stats['swing_color'][1] * alpha_factor) + 50)
            b = min(255, int(stats['swing_color'][2] * alpha_factor) + 50)
            
            pygame.draw.circle(surface, (r, g, b), (mx, my), current_range, 5)

        # 2. WINDUP (Зарядка)
        if self.windup_timer > 0:
            pct = 1.0 - (self.windup_timer / stats['windup_duration'])
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                r, g, b = stats['swing_color']
                pygame.draw.circle(surface, (r, g, b), (cmx, cmy), current_r, 3)

        # 3. COOLDOWN
        elif self.cooldown_timer > 0:
            pct = self.cooldown_timer / stats['cooldown']
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (255, 200, 0), (cmx, cmy), current_r, 3)

        # 4. RELOAD (Перезарядка)
        if self.is_reloading:
            bullets_to_reload = self.max_ammo - self.current_ammo
            base_time = self.stats['reload_duration'] * (bullets_to_reload / self.max_ammo) if bullets_to_reload > 0 else 0.0
            pct = 1.0 - (self.reload_timer / base_time) if base_time > 0 else 1.0
            pct = max(0.0, min(1.0, pct))
            current_r = int(base_radius * pct)
            
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (0, 255, 255), (cmx, cmy), current_r, 3)

        # 5. AMMO (Патроны)
        if self.max_ammo > 0:
            dot_r = 3
            spacing = 10
            total_w = (self.max_ammo - 1) * spacing
            start_x = cmx - total_w // 2
            y_pos = cmy - 25
            
            if self.is_reloading:
                reload_text = self.reload_font.render("RELOADING", True, (0, 255, 255))
                text_rect = reload_text.get_rect(center=(cmx, y_pos - 15))
                surface.blit(reload_text, text_rect)
            
            reload_pct = 0.0
            if self.is_reloading:
                bullets_to_reload = self.max_ammo - self.current_ammo
                base_time = self.stats['reload_duration'] * (bullets_to_reload / self.max_ammo) if bullets_to_reload > 0 else 0.0
                reload_pct = 1.0 - (self.reload_timer / base_time) if base_time > 0 else 1.0
                
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

        # 6. ПРИЦЕЛ (Курсор)
        color = stats['cursor_color']
        pygame.draw.line(surface, color, (cmx-10, cmy), (cmx+10, cmy), 2)
        pygame.draw.line(surface, color, (cmx, cmy-10), (cmx, cmy+10), 2)
        pygame.draw.circle(surface, (255, 50, 50), (cmx, cmy), 3)