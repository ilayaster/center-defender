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
        
        self.time_survived = 0.0
        self.target_time = DIFFICULTY_TARGETS.get(self.game_settings['difficulty'], 600)
        self.current_minute = 0
        self.spawn_timer = 0.0
        
        self.update_difficulty()

    def update_difficulty(self):
        diff = self.game_settings.get('difficulty', 'Normal')
        self.target_time = DIFFICULTY_TARGETS.get(diff, 600)
        
        if diff == 'Easy':
            self.game_settings['enemy_speed'] = 120.0
        elif diff == 'Normal':
            self.game_settings['enemy_speed'] = 150.0
        elif diff == 'Hard':
            self.game_settings['enemy_speed'] = 190.0

    def reset(self):
        self.enemies = []
        self.score = 0
        self.game_won = False
        self.time_survived = 0.0
        self.current_minute = 0
        self.spawn_timer = 0.0
        self.update_difficulty()

    def update(self, dt, sw, sh):
        self.time_survived += dt
        if self.time_survived >= self.target_time:
            self.time_survived = self.target_time
            self.game_won = True
            return True

        current_minute_idx = int(self.time_survived // 60)
        if current_minute_idx > self.current_minute:
            self.current_minute = current_minute_idx
            self.spawn_timer = 0.0

        patterns = WAVE_PATTERNS.get(self.game_settings['difficulty'], WAVE_PATTERNS['Normal'])
        pattern = patterns[min(current_minute_idx, len(patterns) - 1)]

        self.spawn_timer += dt
        if self.spawn_timer >= pattern['interval']:
            for _ in range(pattern['count']):
                self.enemies.append(Enemy(self.game_settings, sw, sh, self.sprite_manager))
            self.spawn_timer = 0.0

        # 1. Обновляем эффекты ядра (включая уменьшение таймера кулдауна урона и регенерацию)
        self.core.apply_effects(self.enemies, dt)

        # 2. Проверяем столкновения только с живыми врагами
        core_hit = False
        for enemy in self.enemies:
            if enemy.is_dead:
                continue
            if enemy.update(dt, sw, sh, self.core):
                core_hit = True

        # 3. Обрабатываем попадание (внутри Core.on_hit есть защита от спама урона)
        if core_hit:
            kills = self.core.on_hit(self.enemies)
            self.score += kills
            if self.core.current_hp <= 0:
                self.game_won = False
                return True  # Game Over

        # 4. Удаление мертвых врагов из списка
        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead]
        
        return False