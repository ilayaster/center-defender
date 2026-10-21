# --- COLORS ---
BG_COLOR = (0, 0, 0)
MENU_BG = (0, 0, 0)
CORE_COLOR = (76, 175, 80)
ENEMY_COLOR = (244, 67, 54)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (60, 60, 60)
BTN_HOVER = (100, 100, 100)
BTN_TEXT = (255, 255, 255)

# --- GAME CONSTANTS ---
FPS = 60
CORE_RADIUS = 30

# --- DIFFICULTY & WAVE SYSTEM ---
# Целевое время выживания в секундах (10, 15 и 20 минут)
DIFFICULTY_TARGETS = {
    'Easy': 600,
    'Normal': 900,
    'Hard': 1200
}

# Паттерны волн для каждой минуты. 
# index 0 = 1-я минута, index 9 = 10-я минута и т.д.
# 'interval': секунды между появлениями пачек (волн) врагов.
# 'count': количество врагов в одной пачке (спавняются одновременно).
WAVE_PATTERNS = {
    'Easy': [
        {'interval': 10.0, 'count': 1},   # Мин 1: Очень спокойно
        {'interval': 8.0, 'count': 2},    # Мин 2
        {'interval': 7.0, 'count': 2},    # Мин 3
        {'interval': 6.0, 'count': 3},    # Мин 4
        {'interval': 5.0, 'count': 3},    # Мин 5
        {'interval': 4.5, 'count': 4},    # Мин 6
        {'interval': 4.0, 'count': 4},    # Мин 7
        {'interval': 3.5, 'count': 5},    # Мин 8
        {'interval': 3.0, 'count': 6},    # Мин 9
        {'interval': 2.5, 'count': 8},    # Мин 10: Финальный раш
    ],
    'Normal': [
        {'interval': 8.0, 'count': 2},    # Мин 1
        {'interval': 7.0, 'count': 3},    # Мин 2
        {'interval': 6.0, 'count': 3},    # Мин 3
        {'interval': 5.0, 'count': 4},    # Мин 4
        {'interval': 4.5, 'count': 5},    # Мин 5
        {'interval': 4.0, 'count': 5},    # Мин 6
        {'interval': 3.5, 'count': 6},    # Мин 7
        {'interval': 3.0, 'count': 7},    # Мин 8
        {'interval': 2.5, 'count': 8},    # Мин 9
        {'interval': 2.0, 'count': 10},   # Мин 10
        {'interval': 1.8, 'count': 12},   # Мин 11
        {'interval': 1.5, 'count': 14},   # Мин 12
        {'interval': 1.2, 'count': 16},   # Мин 13
        {'interval': 1.0, 'count': 18},   # Мин 14
        {'interval': 0.8, 'count': 25},   # Мин 15: Финальный раш
    ],
    'Hard': [
        {'interval': 6.0, 'count': 3},    # Мин 1
        {'interval': 5.5, 'count': 4},    # Мин 2
        {'interval': 5.0, 'count': 4},    # Мин 3
        {'interval': 4.5, 'count': 5},    # Мин 4
        {'interval': 4.0, 'count': 6},    # Мин 5
        {'interval': 3.5, 'count': 7},    # Мин 6
        {'interval': 3.0, 'count': 8},    # Мин 7
        {'interval': 2.5, 'count': 10},   # Мин 8
        {'interval': 2.0, 'count': 12},   # Мин 9
        {'interval': 1.8, 'count': 15},   # Мин 10
        {'interval': 1.5, 'count': 18},   # Мин 11
        {'interval': 1.2, 'count': 20},   # Мин 12
        {'interval': 1.0, 'count': 25},   # Мин 13
        {'interval': 0.8, 'count': 30},   # Мин 14
        {'interval': 0.7, 'count': 35},   # Мин 15
        {'interval': 0.6, 'count': 40},   # Мин 16
        {'interval': 0.5, 'count': 50},   # Мин 17
        {'interval': 0.4, 'count': 60},   # Мин 18
        {'interval': 0.3, 'count': 80},   # Мин 19
        {'interval': 0.2, 'count': 100},  # Мин 20: Абсолютный ад
    ]
}

# --- WEAPON SYSTEM ---
WEAPONS = {
    'sword': {
        'name': 'SWORD',
        'cooldown': 0.45,
        'windup_duration': 0.0,
        'swing_duration': 0.15,
        'range': 60,
        'swing_color': (255, 255, 150),
        'cursor_color': (220, 220, 220),
        'magazine_size': 0,
        'reload_duration': 0.0
    },
    'hammer': {
        'name': 'HAMMER',
        'cooldown': 1.2,
        'windup_duration': 0.35,
        'swing_duration': 0.25,
        'range': 140,
        'swing_color': (255, 100, 50),
        'cursor_color': (180, 100, 100),
        'magazine_size': 0,
        'reload_duration': 0.0
    },
    'pistol': {
        'name': 'PISTOL',
        'cooldown': 0.15,
        'windup_duration': 0.0,
        'swing_duration': 0.1,
        'range': 40,
        'swing_color': (255, 255, 0),
        'cursor_color': (200, 200, 255),
        'magazine_size': 6,
        'reload_duration': 1.5
    }
}

DEFAULT_WEAPON = 'sword'

# --- UI & RESOLUTIONS ---
STANDARD_RESOLUTIONS = [
    (1280, 720),
    (1920, 1080),
    (2560, 1440)
]

def get_default_settings(native_res):
    return {
        'resolution': native_res,
        'display_mode': 'Windowed',
        'difficulty': 'Normal',
        'show_hitboxes': False,
        'enemy_speed': 150.0 # Базовая скорость, можно масштабировать в gameplay.py
    }