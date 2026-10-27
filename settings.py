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
        { # Минута 1
            'enemy-1': {'interval': 3.0, 'count': 1},
        },
        { # Минута 2
            'enemy-1': {'interval': 2.5, 'count': 2},
            'enemy-2': {'interval': 5.0, 'count': 1},
        },
        { # Минута 3+
            'enemy-1': {'interval': 2.0, 'count': 2},
            'enemy-2': {'interval': 4.0, 'count': 1},
            'enemy-3': {'interval': 10.0, 'count': 1},
        }
    ],
    'Normal': [
        { # Минута 1
            'enemy-1': {'interval': 2.0, 'count': 2},
            'enemy-2': {'interval': 5.0, 'count': 1},
        },
        { # Минута 2
            'enemy-1': {'interval': 1.5, 'count': 2},
            'enemy-2': {'interval': 4.0, 'count': 1},
            'enemy-3': {'interval': 8.0, 'count': 1},
        },
        { # Минута 3
            'enemy-1': {'interval': 1.2, 'count': 3},
            'enemy-2': {'interval': 3.0, 'count': 2},
            'enemy-3': {'interval': 6.0, 'count': 1},
        },
        { # Минута 4+
            'enemy-1': {'interval': 1.0, 'count': 3},
            'enemy-2': {'interval': 2.5, 'count': 2},
            'enemy-3': {'interval': 5.0, 'count': 1},
        }
    ],
    'Hard': [
        { # Минута 1
            'enemy-1': {'interval': 1.5, 'count': 2},
            'enemy-2': {'interval': 4.0, 'count': 1},
        },
        { # Минута 2
            'enemy-1': {'interval': 1.0, 'count': 3},
            'enemy-2': {'interval': 3.0, 'count': 2},
            'enemy-3': {'interval': 7.0, 'count': 1},
        },
        { # Минута 3+
            'enemy-1': {'interval': 0.8, 'count': 3},
            'enemy-2': {'interval': 2.0, 'count': 2},
            'enemy-3': {'interval': 4.0, 'count': 1},
        }
    ]
}

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
        'sfx_volume': 0.5,
        'music_volume': 0.5,
        'enemy_speed': 150.0
        # 'enemy_stats' удален, так как статы теперь инкапсулированы в классах врагов
    }