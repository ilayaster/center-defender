import math
from entities.enemy import Enemy
from settings import DIFFICULTY_TARGETS, WAVE_PATTERNS

class GameplayManager:
    def __init__(self, game_settings, core, sprite_manager):
        self.game_settings = game_settings
        self.core = core
        self.sprite_manager = sprite_manager
        
        self.enemies = []
        self.score = 0
        self.game_won = False
        
        # Система времени и волн
        self.time_survived = 0.0
        self.target_time = DIFFICULTY_TARGETS.get(self.game_settings['difficulty'], 600)
        self.current_minute = 0
        self.spawn_timer = 0.0  # Таймер для отсчета интервала между пачками
        
        self.update_difficulty()

    def update_difficulty(self):
        """Обновляет параметры в зависимости от выбранной сложности"""
        diff = self.game_settings.get('difficulty', 'Normal')
        self.target_time = DIFFICULTY_TARGETS.get(diff, 600)
        
        if diff == 'Easy':
            self.game_settings['enemy_speed'] = 120.0
        elif diff == 'Normal':
            self.game_settings['enemy_speed'] = 150.0
        elif diff == 'Hard':
            self.game_settings['enemy_speed'] = 190.0

    def reset(self):
        """Сбрасывает состояние игры для нового раунда"""
        self.enemies = []
        self.score = 0
        self.game_won = False
        self.time_survived = 0.0
        self.current_minute = 0
        self.spawn_timer = 0.0
        self.update_difficulty()

    def update(self, dt, sw, sh):
        """Обновляет игровую логику. Возвращает True при GAMEOVER"""
        # 1. Обновление времени выживания
        self.time_survived += dt
        if self.time_survived >= self.target_time:
            self.time_survived = self.target_time
            self.game_won = True
            return True

        # 2. Определение текущей минуты
        current_minute_idx = int(self.time_survived // 60)
        
        # Если наступила новая минута, сбрасываем таймер спавна для нового паттерна
        if current_minute_idx > self.current_minute:
            self.current_minute = current_minute_idx
            self.spawn_timer = 0.0

        # 3. Получение паттерна для текущей минуты
        patterns = WAVE_PATTERNS.get(self.game_settings['difficulty'], WAVE_PATTERNS['Normal'])
        pattern = patterns[min(current_minute_idx, len(patterns) - 1)]

        # 4. Логика спавна: каждые `interval` секунд спавним `count` врагов (пачкой)
        self.spawn_timer += dt
        if self.spawn_timer >= pattern['interval']:
            for _ in range(pattern['count']):
                self.enemies.append(Enemy(self.game_settings, sw, sh, self.sprite_manager))
            self.spawn_timer = 0.0  # Сбрасываем таймер для следующей пачки

        # 5. Обновление врагов и проверка коллизий с ядром
        for enemy in self.enemies:
            if enemy.update(dt, sw, sh, self.core):
                self.game_won = False
                return True

        # 6. Удаление мертвых врагов
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead]
        
        return False