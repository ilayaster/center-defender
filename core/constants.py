# Состояния игры
STATE_MENU = 0
STATE_DIFFICULTY = 1
STATE_SETTINGS = 2
STATE_PLAYING = 3
STATE_GAMEOVER = 4
STATE_PAUSED = 5

# Стандартные разрешения
STANDARD_RESOLUTIONS = [
    (640, 480), (800, 600), (1024, 768), (1280, 720), (1280, 800),
    (1366, 768), (1440, 900), (1600, 900), (1680, 1050),
    (1920, 1080), (2560, 1440), (3840, 2160)
]

# Настройки по умолчанию
def get_default_settings(native_res):
    return {
        'difficulty': 'Normal',
        'resolution': native_res,
        'display_mode': 'Borderless',
        'enemy_speed': 150,
        'spawn_interval': 1.0,
        'show_hitboxes': False
    }

# Параметры сложности
DIFFICULTY_PARAMS = {
    'Easy': (100, 1.5),
    'Normal': (150, 1.0),
    'Hard': (220, 0.5)
}