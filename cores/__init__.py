from cores.plosive import PlosiveCore
from cores.slow import SlowCore

CORE_CLASSES = {
    'plosive': PlosiveCore,
    'slow': SlowCore,
}

DEFAULT_CORE = 'plosive'

def get_core(core_type, screen_w, screen_h, sprite_manager):
    cls = CORE_CLASSES.get(core_type)
    if cls is None:
        raise ValueError(f"Неизвестное ядро: {core_type}")
    return cls(screen_w, screen_h, sprite_manager)

def get_available_cores():
    return list(CORE_CLASSES.keys())