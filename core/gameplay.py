import math
from entities.enemy import Enemy
from settings import DIFFICULTY_TARGETS, WAVE_PATTERNS, ENEMY_STATS

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
        
        self.spawn_timers = {}
        
        # <-- ГАРАНТИЯ: добавляем статы врагов в настройки явно
        if 'enemy_stats' not in self.game_settings:
            self.game_settings['enemy_stats'] = ENEMY_STATS
        
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
        self.spawn_timers = {}
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
            self.spawn_timers = {}

        patterns = WAVE_PATTERNS.get(self.game_settings['difficulty'], WAVE_PATTERNS['Normal'])
        current_phase = patterns[min(current_minute_idx, len(patterns) - 1)]

        for enemy_type, spawn_data in current_phase.items():
            if enemy_type not in self.spawn_timers:
                self.spawn_timers[enemy_type] = 0.0

            self.spawn_timers[enemy_type] += dt
            
            if self.spawn_timers[enemy_type] >= spawn_data['interval']:
                for _ in range(spawn_data['count']):
                    self.enemies.append(Enemy(enemy_type, self.game_settings, sw, sh, self.sprite_manager))
                
                self.spawn_timers[enemy_type] = 0.0

        self.core.apply_effects(self.enemies, dt)

        core_hit = False
        for enemy in self.enemies:
            if enemy.is_dead:
                continue
            if enemy.update(dt, sw, sh, self.core):
                core_hit = True

        if core_hit:
            kills = self.core.on_hit(self.enemies)
            self.score += kills
            if self.core.current_hp <= 0:
                self.game_won = False
                return True

        self.enemies = [enemy for enemy in self.enemies if not enemy.is_dead]
        
        return False