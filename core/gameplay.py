import math
from entities.enemy import Enemy

class GameplayManager:
    def __init__(self, game_settings, core, sprite_manager):
        self.game_settings = game_settings
        self.core = core
        self.sprite_manager = sprite_manager
        
        self.enemies = []
        self.spawn_timer = 0.0
        self.time_left = game_settings.get('game_duration', 30) # Резервное значение
        self.score = 0
        self.game_won = False
        
        self.update_difficulty()

    def update_difficulty(self):
        """Обновляет параметры в зависимости от выбранной сложности"""
        diff = self.game_settings.get('difficulty', 'Normal')
        if diff == 'Easy':
            self.game_settings['spawn_interval'] = 1.5
            self.game_settings['enemy_speed'] = 100.0
        elif diff == 'Normal':
            self.game_settings['spawn_interval'] = 1.0
            self.game_settings['enemy_speed'] = 150.0
        elif diff == 'Hard':
            self.game_settings['spawn_interval'] = 0.6
            self.game_settings['enemy_speed'] = 200.0

    def reset(self):
        """Сбрасывает состояние игры для нового раунда"""
        self.enemies = []
        self.spawn_timer = 0.0
        self.time_left = 30 # GAME_DURATION из settings
        self.score = 0
        self.game_won = False
        self.update_difficulty()

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

        # Постепенное усложнение (уменьшаем интервал спавна со временем)
        if self.game_settings['spawn_interval'] > 0.2:
            self.game_settings['spawn_interval'] -= 0.01 * dt

        # Обновление врагов и проверка коллизий с ядром
        for enemy in self.enemies:
            if enemy.update(dt, sw, sh, self.core):
                self.game_won = False
                return True # Враг достиг ядра

        # Удаление мертвых врагов
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead]
        
        return False