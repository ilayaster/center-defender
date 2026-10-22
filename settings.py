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
DIFFICULTY_TARGETS = {
    'Easy': 600,
    'Normal': 900,
    'Hard': 1200
}

WAVE_PATTERNS = {
    'Easy': [
        {'interval': 10.0, 'count': 1}, {'interval': 8.0, 'count': 2},
        {'interval': 7.0, 'count': 2}, {'interval': 6.0, 'count': 3},
        {'interval': 5.0, 'count': 3}, {'interval': 4.5, 'count': 4},
        {'interval': 4.0, 'count': 4}, {'interval': 3.5, 'count': 5},
        {'interval': 3.0, 'count': 6}, {'interval': 2.5, 'count': 8},
    ],
    'Normal': [
        {'interval': 8.0, 'count': 2}, {'interval': 7.0, 'count': 3},
        {'interval': 6.0, 'count': 3}, {'interval': 5.0, 'count': 4},
        {'interval': 4.5, 'count': 5}, {'interval': 4.0, 'count': 5},
        {'interval': 3.5, 'count': 6}, {'interval': 3.0, 'count': 7},
        {'interval': 2.5, 'count': 8}, {'interval': 2.0, 'count': 10},
        {'interval': 1.8, 'count': 12}, {'interval': 1.5, 'count': 14},
        {'interval': 1.2, 'count': 16}, {'interval': 1.0, 'count': 18},
        {'interval': 0.8, 'count': 25},
    ],
    'Hard': [
        {'interval': 6.0, 'count': 3}, {'interval': 5.5, 'count': 4},
        {'interval': 5.0, 'count': 4}, {'interval': 4.5, 'count': 5},
        {'interval': 4.0, 'count': 6}, {'interval': 3.5, 'count': 7},
        {'interval': 3.0, 'count': 8}, {'interval': 2.5, 'count': 10},
        {'interval': 2.0, 'count': 12}, {'interval': 1.8, 'count': 15},
        {'interval': 1.5, 'count': 18}, {'interval': 1.2, 'count': 20},
        {'interval': 1.0, 'count': 25}, {'interval': 0.8, 'count': 30},
        {'interval': 0.7, 'count': 35}, {'interval': 0.6, 'count': 40},
        {'interval': 0.5, 'count': 50}, {'interval': 0.4, 'count': 60},
        {'interval': 0.3, 'count': 80}, {'interval': 0.2, 'count': 100},
    ]
}

# --- WEAPON SYSTEM ---
WEAPONS = {
    'sword': {
        'name': 'SWORD', 'cooldown': 0.45, 'windup_duration': 0.0, 'swing_duration': 0.15,
        'range': 60, 'swing_color': (255, 255, 150), 'cursor_color': (220, 220, 220),
        'magazine_size': 0, 'reload_duration': 0.0
    },
    'hammer': {
        'name': 'HAMMER', 'cooldown': 1.2, 'windup_duration': 0.35, 'swing_duration': 0.25,
        'range': 140, 'swing_color': (255, 100, 50), 'cursor_color': (180, 100, 100),
        'magazine_size': 0, 'reload_duration': 0.0
    },
    'pistol': {
        'name': 'PISTOL', 'cooldown': 0.15, 'windup_duration': 0.0, 'swing_duration': 0.1,
        'range': 40, 'swing_color': (255, 255, 0), 'cursor_color': (200, 200, 255),
        'magazine_size': 6, 'reload_duration': 1.5  # Базовое время для полной перезарядки
    }
}

DEFAULT_WEAPON = 'sword'

# --- UI & RESOLUTIONS ---
STANDARD_RESOLUTIONS = [
    (1280, 720), (1920, 1080), (2560, 1440)
]

def get_default_settings(native_res):
    return {
        'resolution': native_res,
        'display_mode': 'Windowed',
        'difficulty': 'Normal',
        'show_hitboxes': False,
        'effect_mode': 'OFF',
        'sfx_volume': 0.5,  # <-- НОВЫЙ ПАРАМЕТР (от 0.0 до 1.0)
        'enemy_speed': 150.0
    }