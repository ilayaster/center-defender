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
# Здесь можно добавлять новые типы оружия. 
# range: радиус взмаха (хитбокс). cooldown: время между взмахами в секундах.
WEAPONS = {
    'sword': {
        'name': 'Меч',
        'cooldown': 0.45,          # Секунды до следующего взмаха
        'swing_duration': 0.15,    # Сколько длится визуальный эффект взмаха
        'range': 90,               # Радиус поражения (хитбокс взмаха)
        'swing_color': (255, 255, 150), # Цвет эффекта взмаха
        'cursor_color': (220, 220, 220) # Цвет курсора в покое
    },
    # Пример для будущего расширения:
    # 'axe': {
    #     'name': 'Топор',
    #     'cooldown': 0.9,
    #     'swing_duration': 0.25,
    #     'range': 130,
    #     'swing_color': (255, 100, 100),
    #     'cursor_color': (180, 100, 100)
    # }
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
        'display_mode': 'Windowed', # Windowed, Borderless, Fullscreen
        'difficulty': 'Normal',     # Easy, Normal, Hard
        'show_hitboxes': False,
        'spawn_interval': 1.2,      # Будет перезаписано в GameplayManager в зависимости от сложности
        'enemy_speed': 150.0
    }