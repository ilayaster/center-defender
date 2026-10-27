from weapons.sword import Sword
from weapons.hammer import Hammer
from weapons.pistol import Pistol

# Регистрируем все доступные оружия
WEAPON_CLASSES = {
    'sword': Sword,
    'hammer': Hammer,
    'pistol': Pistol,
}

DEFAULT_WEAPON = 'sword'

def get_weapon(weapon_key):
    """Создаёт и возвращает экземпляр оружия по ключу"""
    cls = WEAPON_CLASSES.get(weapon_key)
    if cls is None:
        raise ValueError(f"Неизвестное оружие: {weapon_key}")
    return cls()

def get_available_weapons():
    """Возвращает список ключей всех зарегистрированных оружий"""
    return list(WEAPON_CLASSES.keys())