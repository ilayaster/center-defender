import pygame
import math
from settings import WEAPONS, DEFAULT_WEAPON

class WeaponManager:
    def __init__(self):
        self.current_weapon_key = DEFAULT_WEAPON
        self.stats = WEAPONS[self.current_weapon_key]
        self.reload_font = pygame.font.Font(None, 18) # Маленький шрифт для текста
        self.reset_timers()

    def set_weapon(self, weapon_key):
        """Переключает текущее оружие и сбрасывает таймеры"""
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

        # Логика магазина
        self.max_ammo = self.stats.get('magazine_size', 0)
        self.current_ammo = self.max_ammo
        self.is_reloading = False
        self.reload_timer = 0.0

    def request_attack(self):
        """
        Запрашивает атаку. 
        Если магазин пуст, начинает перезарядку.
        """
        if self.is_reloading or self.cooldown_timer > 0 or self.is_swinging or self.windup_timer > 0:
            return False

        # Проверка магазина
        if self.max_ammo > 0:
            if self.current_ammo <= 0:
                # Патронов нет, начинаем перезарядку
                self.is_reloading = True
                self.reload_timer = self.stats['reload_duration']
                return False
            self.current_ammo -= 1

        self.windup_timer = self.stats['windup_duration']
        self.attack_requested = True
        return True

    def _perform_attack(self, mouse_pos, enemies):
        """Внутренний метод нанесения урона по площади"""
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

        # Автоматическая перезарядка, если патроны кончились
        if self.max_ammo > 0 and self.current_ammo == 0:
            self.is_reloading = True
            self.reload_timer = self.stats['reload_duration']

        return hits

    def update(self, dt, mouse_pos, enemies):
        """Обновляет таймеры, перезарядку и наносит урон"""
        hits = 0
        
        # 1. Логика перезарядки
        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self.is_reloading = False
                self.current_ammo = self.max_ammo # Восстанавливаем обойму
                
        # 2. Обновление кулдауна
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        # 3. Обработка запроса на атаку и windup
        if self.attack_requested:
            if self.windup_timer > 0:
                self.windup_timer -= dt
                if self.windup_timer <= 0:
                    self.windup_timer = 0
                    hits = self._perform_attack(mouse_pos, enemies)
            else:
                hits = self._perform_attack(mouse_pos, enemies)
            
        # 4. Обновление анимации взмаха
        if self.is_swinging:
            self.swing_timer -= dt
            if self.swing_timer <= 0:
                self.is_swinging = False
                
        return hits

    def draw(self, surface, mouse_pos):
        """Отрисовывает курсор, эффекты и UI оружия"""
        mx, my = int(mouse_pos[0]), int(mouse_pos[1])
        stats = self.stats
        base_radius = max(12, int(stats['range'] * 0.25))

        # 1. Индикатор перезарядки (Заполняющееся кольцо)
        if self.is_reloading:
            pct = 1.0 - (self.reload_timer / self.stats['reload_duration'])
            current_r = int(base_radius * pct)
            
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (0, 255, 255), (mx, my), current_r, 3)

        # 2. Индикатор кулдауна (Сжимающееся кольцо)
        elif self.cooldown_timer > 0:
            pct = self.cooldown_timer / stats['cooldown']
            current_r = int(base_radius * pct)
            
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                pygame.draw.circle(surface, (255, 200, 0), (mx, my), current_r, 3)

        # 3. Индикатор Windup
        if self.windup_timer > 0:
            pct = 1.0 - (self.windup_timer / stats['windup_duration'])
            current_r = int(base_radius * pct)
            
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            if current_r > 1:
                r, g, b = stats['swing_color']
                pygame.draw.circle(surface, (r, g, b), (mx, my), current_r, 3)

        # 4. Индикатор патронов и текст RELOADING
        if self.max_ammo > 0:
            dot_r = 3
            spacing = 10
            total_w = (self.max_ammo - 1) * spacing
            start_x = mx - total_w // 2
            y_pos = my - 25  # Над прицелом
            
            # Текст "RELOADING"
            if self.is_reloading:
                reload_text = self.reload_font.render("RELOADING", True, (0, 255, 255))
                text_rect = reload_text.get_rect(center=(mx, y_pos - 15))
                surface.blit(reload_text, text_rect)

            # Логика визуального добавления патронов
            reload_pct = 0.0
            if self.is_reloading:
                reload_pct = 1.0 - (self.reload_timer / self.stats['reload_duration'])
                
            # Сколько патронов уже полностью "вставлено"
            loaded_bullets = int(reload_pct * self.max_ammo)
            # Дробная часть для текущего вставляющегося патрона
            fractional = (reload_pct * self.max_ammo) - loaded_bullets

            for i in range(self.max_ammo):
                x_pos = start_x + i * spacing
                
                if i < self.current_ammo:
                    # Патрон уже в обойме (белый)
                    pygame.draw.circle(surface, (255, 255, 255), (x_pos, y_pos), dot_r)
                elif self.is_reloading:
                    idx_in_reload = i - self.current_ammo
                    if idx_in_reload < loaded_bullets:
                        # Патрон уже зарядился в этом цикле (голубой)
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), dot_r)
                    elif idx_in_reload == loaded_bullets:
                        # Патрон сейчас заряжается (плавно растет радиус)
                        current_r = max(1, int(dot_r * fractional))
                        pygame.draw.circle(surface, (0, 255, 255), (x_pos, y_pos), current_r)
                    else:
                        # Патрон еще не начал заряжаться (темно-серый)
                        pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)
                else:
                    # Перезарядка не идет, патрона нет
                    pygame.draw.circle(surface, (80, 80, 80), (x_pos, y_pos), dot_r)

        # 5. Отрисовка оружия (взмах или прицел)
        if self.is_swinging:
            progress = 1.0 - (self.swing_timer / stats['swing_duration'])
            current_range = int(stats['range'] * (0.4 + 0.6 * progress))
            alpha_factor = 1.0 - progress
            
            r = min(255, int(stats['swing_color'][0] * alpha_factor) + 50)
            g = min(255, int(stats['swing_color'][1] * alpha_factor) + 50)
            b = min(255, int(stats['swing_color'][2] * alpha_factor) + 50)
            
            pygame.draw.circle(surface, (r, g, b), (mx, my), current_range, 5)
        else:
            # Обычный курсор в покое
            color = stats['cursor_color']
            pygame.draw.line(surface, color, (mx-10, my), (mx+10, my), 2)
            pygame.draw.line(surface, color, (mx, my-10), (mx, my+10), 2)
            pygame.draw.circle(surface, (255, 50, 50), (mx, my), 3)