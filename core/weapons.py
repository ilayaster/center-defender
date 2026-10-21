import pygame
import math
from settings import WEAPONS, DEFAULT_WEAPON

class WeaponManager:
    def __init__(self):
        self.current_weapon_key = DEFAULT_WEAPON
        self.stats = WEAPONS[self.current_weapon_key]
        
        self.cooldown_timer = 0.0
        self.is_swinging = False
        self.swing_timer = 0.0

    def update(self, dt):
        """Обновляет таймеры кулдауна и анимации взмаха"""
        if self.cooldown_timer > 0:
            self.cooldown_timer -= dt
            
        if self.is_swinging:
            self.swing_timer -= dt
            if self.swing_timer <= 0:
                self.is_swinging = False

    def attack(self, mouse_pos, enemies):
        """
        Пытается совершить атаку.
        Возвращает количество убитых врагов за этот взмах.
        """
        # Если оружие на кулдауне или уже в анимации взмаха, игнорируем клик
        if self.cooldown_timer > 0 or self.is_swinging:
            return 0

        # Инициализация взмаха
        self.is_swinging = True
        self.swing_timer = self.stats['swing_duration']
        self.cooldown_timer = self.stats['cooldown']

        hits = 0
        weapon_range = self.stats['range']

        # Проверка попадания по всем врагам в радиусе взмаха
        for enemy in enemies:
            if not enemy.is_dead:
                # Расстояние от курсора до врага
                dist = math.hypot(mouse_pos[0] - enemy.x, mouse_pos[1] - enemy.y)
                # Учитываем радиус врага для более щедрого хитбокса
                if dist <= (weapon_range + enemy.hitbox_radius):
                    enemy.is_dead = True
                    hits += 1
                    
        return hits

    def draw(self, surface, mouse_pos):
        """Отрисовывает курсор, эффект взмаха и индикатор кулдауна"""
        mx, my = int(mouse_pos[0]), int(mouse_pos[1])
        stats = self.stats

        # 1. Отрисовка кулдауна (кольцо вокруг курсора)
        if self.cooldown_timer > 0:
            pct = self.cooldown_timer / stats['cooldown']
            base_radius = int(stats['range'] * 0.25) # Кольцо чуть больше центра
            
            # Фоновое темное кольцо
            pygame.draw.circle(surface, (50, 50, 50), (mx, my), base_radius, 3)
            
            # Активное кольцо, уменьшающееся со временем
            current_r = int(base_radius * pct)
            if current_r > 1:
                pygame.draw.circle(surface, (255, 200, 0), (mx, my), current_r, 3)

        # 2. Отрисовка оружия
        if self.is_swinging:
            # Эффект взмаха: расширяющаяся и исчезающая окружность (имитация дуги удара)
            progress = 1.0 - (self.swing_timer / stats['swing_duration'])
            current_range = int(stats['range'] * (0.4 + 0.6 * progress)) # От 40% до 100% радиуса
            alpha_factor = 1.0 - progress # От 1 до 0
            
            # Цвет становится более прозрачным к концу взмаха
            color_val = int(255 * alpha_factor)
            # Смешиваем цвет взмаха с прозрачностью (упрощенно через уменьшение RGB)
            r = min(255, int(stats['swing_color'][0] * alpha_factor) + 50)
            g = min(255, int(stats['swing_color'][1] * alpha_factor) + 50)
            b = min(255, int(stats['swing_color'][2] * alpha_factor) + 50)
            
            pygame.draw.circle(surface, (r, g, b), (mx, my), current_range, 4)
        else:
            # Обычный курсор в покое (прицел)
            color = stats['cursor_color']
            pygame.draw.line(surface, color, (mx-10, my), (mx+10, my), 2)
            pygame.draw.line(surface, color, (mx, my-10), (mx, my+10), 2)
            pygame.draw.circle(surface, (255, 50, 50), (mx, my), 3) # Красная точка в центре