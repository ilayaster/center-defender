# --- COLORS ---
BG_COLOR = (0, 0, 0)        # Черный фон
MENU_BG = (0, 0, 0)         # Черный фон меню
CORE_COLOR = (76, 175, 80)
ENEMY_COLOR = (244, 67, 54)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (60, 60, 60)
BTN_HOVER = (100, 100, 100)
BTN_TEXT = (255, 255, 255)

# --- GAME CONSTANTS ---
FPS = 60
CORE_RADIUS = 30
GAME_DURATION = 30

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
        'magazine_size': 0,      # 0 означает бесконечный магазин
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
        'cooldown': 0.15,          # Очень быстрая стрельба
        'windup_duration': 0.0,
        'swing_duration': 0.1,     # Короткая вспышка
        'range': 40,               # Маленький хитбокс
        'swing_color': (255, 255, 0),
        'cursor_color': (200, 200, 255),
        'magazine_size': 6,        # 6 патронов в обойме
        'reload_duration': 1.5     # 1.5 секунды на перезарядку
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
        'spawn_interval': 1.2,
        'enemy_speed': 150.0
    }