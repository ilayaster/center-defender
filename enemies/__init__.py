from enemies.walker import Walker
from enemies.jumper import Jumper
from enemies.shield import Shield

ENEMY_CLASSES = {
    'enemy-1': Walker,
    'enemy-2': Jumper,
    'enemy-3': Shield,
}

def get_enemy(enemy_type, settings, screen_w, screen_h, sprite_manager):
    cls = ENEMY_CLASSES.get(enemy_type)
    if cls is None:
        raise ValueError(f"Неизвестный тип врага: {enemy_type}")
    return cls(settings, screen_w, screen_h, sprite_manager)

def get_available_enemies():
    return list(ENEMY_CLASSES.keys())