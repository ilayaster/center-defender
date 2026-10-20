import math
from entities import Enemy
from core.constants import DIFFICULTY_PARAMS, STATE_GAMEOVER

class GameplayManager:
    """Управляет игровой логикой: спавн, обновление, коллизии"""
    
    def __init__(self, game_settings, core, sprite_manager):
        self.game_settings = game_settings
        self.core = core
        self.sprite_manager = sprite_manager
        
        self.enemies = []
        self.score = 0
        self.time_left = 30
        self.spawn_timer = 0
        self.game_won = False
    
    def reset(self):
        """Сбрасывает игровые переменные"""
        self.enemies.clear()
        self.score = 0
        self.time_left = 30
        self.spawn_timer = 0
        self.game_won = False
    
    def update_difficulty(self):
        """Применяет параметры сложности"""
        speed, interval = DIFFICULTY_PARAMS[self.game_settings['difficulty']]
        self.game_settings['enemy_speed'] = speed
        self.game_settings['spawn_interval'] = interval
    
    def update(self, dt, sw, sh):
        """
        Обновляет игровую логику.
        Возвращает True, если игра должна перейти в состояние GAMEOVER
        """
        # Обновление таймера
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0
            self.game_won = True
            return True
        
        # Спавн врагов
        self.spawn_timer += dt
        if self.spawn_timer >= self.game_settings['spawn_interval']:
            self.enemies.append(Enemy(self.game_settings, sw, sh, self.sprite_manager))
            self.spawn_timer = 0
            # Постепенное усложнение
            if self.game_settings['spawn_interval'] > 0.2:
                self.game_settings['spawn_interval'] -= 0.02
        
        # Обновление врагов и проверка коллизий
        for enemy in self.enemies:
            if enemy.update(dt, sw, sh, self.core):
                self.game_won = False
                return True
        
        # Удаление мертвых врагов
        self.enemies = [e for e in self.enemies if not e.is_dead]
        
        return False
    
    def handle_click(self, mouse_pos):
        """Обрабатывает клик мыши во время игры. Возвращает True, если враг убит."""
        for enemy in self.enemies:
            if math.hypot(mouse_pos[0] - enemy.x, mouse_pos[1] - enemy.y) < enemy.hitbox_radius:
                enemy.is_dead = True
                self.score += 1
                return True
        return False