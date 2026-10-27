import pygame
import math

class BaseWeapon:
    # --- Базовые параметры (переопределяются в дочерних классах) ---
    name = "UNNAMED"
    
    # Урон и хитбокс
    damage = 1
    range = 50.0           # Радиус атаки
    
    # Тайминги
    cooldown = 1.0
    windup_duration = 0.0  # Задержка перед ударом (зарядка молота)
    swing_duration = 0.1   # Длительность визуального взмаха
    
    # Магазин (0 = безлимитное ближнего боя)
    magazine_size = 0
    reload_duration = 0.0
    
    # Визуал
    swing_color = (255, 255, 255)
    cursor_color = (200, 200, 200)
    
    # Словарь путей к звукам
    sounds = {}
    
    def __init__(self):
        # Состояние
        self.cooldown_timer = 0.0
        self.windup_timer = 0.0
        self.is_swinging = False
        self.swing_timer = 0.0
        self.attack_requested = False
        self.attack_pos = (0, 0)
        
        self.max_ammo = self.magazine_size
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.reload_timer = 0.0
        
        self._sounds = {}
        self._load_sounds()
        self._load_font()
    
    def _load_font(self):
        try:
            self.reload_font = pygame.font.Font('fonts/pixel.ttf', 8)
        except:
            self.reload_font = pygame.font.Font(None, 14)
    
    def _load_sounds(self):
        for key, path in self.sounds.items():
            try:
                self._sounds[key] = pygame.mixer.Sound(path)
            except pygame.error:
                pass
    
    def set_volume(self, vol):
        vol = max(0.0, min(1.0, vol))
        for sound in self._sounds.values():
            sound.set_volume(vol)
    
    def _play_sound(self, name):
        if name in self._sounds:
            self._sounds[name].play()
    
    def reset(self):
        """Сброс всех таймеров и состояний"""
        self.cooldown_timer = 0.0
        self.windup_timer = 0.0
        self.is_swinging = False
        self.swing_timer = 0.0
        self.attack_requested = False
        self.attack_pos = (0, 0)
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.reload_timer = 0.0
    
    def request_attack(self, mouse_pos):
        if self.is_reloading:
            self._play_sound('empty')
            return False
        if self.cooldown_timer > 0 or self.is_swinging or self.windup_timer > 0:
            return False
        if self.max_ammo > 0:
            if self.current_ammo <= 0:
                self.is_reloading = True
                self.reload_timer = self.reload_duration
                self._play_sound('empty')
                return False
            self.current_ammo -= 1
        
        self.windup_timer = self.windup_duration
        self.attack_requested = True
        return True
    
    def request_reload(self):
        if self.max_ammo > 0 and self.current_ammo < self.max_ammo and not self.is_reloading:
            self.is_reloading = True
            bullets_to_reload = self.max_ammo - self.current_ammo
            self.reload_timer = self.reload_duration * (bullets_to_reload / self.max_ammo)
    
    def check_hit(self, enemy, mx, my):
        """Проверка попадания. Переопредели для нестандартной формы хитбокса."""
        dist = math.hypot(mx - enemy.x, my - enemy.y)
        return dist <= (self.range + enemy.hitbox_radius)
    
    def on_attack_performed(self):
        """Вызывается после успешной атаки (для звуков и эффектов)"""
        self._play_sound('attack')
    
    def on_reload_complete(self):
        """Вызывается после завершения перезарядки"""
        self._play_sound('reload')
    
    def _perform_attack(self, enemies):
        hits = 0
        mx, my = self.attack_pos
        
        for enemy in enemies:
            if not enemy.is_dead:
                if self.check_hit(enemy, mx, my):
                    if enemy.take_damage(self.damage):
                        hits += 1
        
        self.is_swinging = True
        self.swing_timer = self.swing_duration
        self.cooldown_timer = self.cooldown
        self.attack_requested = False
        
        self.on_attack_performed()
        
        if self.max_ammo > 0 and self.current_ammo == 0:
            self.is_reloading = True
            self.reload_timer = self.reload_duration
        
        return hits
    
    def update(self, dt, mouse_pos, enemies):
        hits = 0
        
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.max_ammo
                self.on_reload_complete()
        
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
        """Общая отрисовка UI, курсора и эффектов"""
        cmx, cmy = int(current_mouse_pos[0]), int(current_mouse_pos[1])
        base_radius = max(12, int(self.range * 0.25))
        
        # 1. АТАКА (Взмах)
        if self.is_swinging:
            mx, my = int(self.attack_pos[0]), int(self.attack_pos[1])
            progress = 1.0 - (self.swing_timer / self.swing_duration)
            current_range = int(self.range * (0.4 + 0.6 * progress))
            alpha_factor = 1.0 - progress
            r = min(255, int(self.swing_color[0] * alpha_factor) + 50)
            g = min(255, int(self.swing_color[1] * alpha_factor) + 50)
            b = min(255, int(self.swing_color[2] * alpha_factor) + 50)
            pygame.draw.circle(surface, (r, g, b), (mx, my), current_range, 5)
        
        # 2. WINDUP (Зарядка)
        if self.windup_timer > 0:
            pct = 1.0 - (self.windup_timer / self.windup_duration) if self.windup_duration > 0 else 1.0
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                r, g, b = self.swing_color
                pygame.draw.circle(surface, (r, g, b), (cmx, cmy), current_r, 3)
        
        # 3. COOLDOWN
        elif self.cooldown_timer > 0:
            pct = self.cooldown_timer / self.cooldown
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (255, 200, 0), (cmx, cmy), current_r, 3)
        
        # 4. RELOAD
        if self.is_reloading and self.max_ammo > 0:
            bullets_to_reload = self.max_ammo - self.current_ammo
            base_time = self.reload_duration * (bullets_to_reload / self.max_ammo)
            pct = 1.0 - (self.reload_timer / base_time) if base_time > 0 else 1.0
            pct = max(0.0, min(1.0, pct))
            current_r = int(base_radius * pct)
            pygame.draw.circle(surface, (50, 50, 50), (cmx, cmy), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (0, 255, 255), (cmx, cmy), current_r, 3)
        
        # 5. AMMO (Патроны) - рисуется ВСЕГДА, если есть магазин
        if self.max_ammo > 0:
            dot_r = 3
            spacing = 10
            total_w = (self.max_ammo - 1) * spacing
            start_x = cmx - total_w // 2
            y_pos = cmy - 25
            
            if self.is_reloading:
                reload_text = self.reload_font.render("RELOADING", True, (0, 255, 255))
                surface.blit(reload_text, reload_text.get_rect(center=(cmx, y_pos - 15)))
                
                bullets_to_reload = self.max_ammo - self.current_ammo
                base_time = self.reload_duration * (bullets_to_reload / self.max_ammo)
                reload_pct = 1.0 - (self.reload_timer / base_time) if base_time > 0 else 1.0
                reload_pct = max(0.0, min(1.0, reload_pct))
                
                loaded_bullets = int(reload_pct * self.max_ammo)
                fractional = (reload_pct * self.max_ammo) - loaded_bullets

            for i in range(self.max_ammo):
                x_pos = start_x + i * spacing
                
                if i < self.current_ammo:
                    # Уже заряженный патрон
                    pygame.draw.circle(surface, (255, 255, 255), (x_pos, y_pos), dot_r)
                elif self.is_reloading:
                    # Патрон в процессе перезарядки
                    idx_in_reload = i - self.current_ammo
                    if idx_in_reload < loaded_bullets:
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), dot_r)
                    elif idx_in_reload == loaded_bullets:
                        current_r = max(1, int(dot_r * fractional))
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), current_r)
                    else:
                        pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)
                else:
                    # Пустой слот (не перезаряжается)
                    pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)
        # 6. ПРИЦЕЛ
        color = self.cursor_color
        pygame.draw.line(surface, color, (cmx - 10, cmy), (cmx + 10, cmy), 2)
        pygame.draw.line(surface, color, (cmx, cmy - 10), (cmx, cmy + 10), 2)
        pygame.draw.circle(surface, (255, 50, 50), (cmx, cmy), 3)