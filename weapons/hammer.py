from weapons.base import BaseWeapon

class Hammer(BaseWeapon):
    name = "HAMMER"
    damage = 1
    range = 140
    
    cooldown = 1.2
    windup_duration = 0.35
    swing_duration = 0.25
    
    magazine_size = 0
    reload_duration = 0.0
    
    swing_color = (255, 100, 50)
    cursor_color = (180, 100, 100)
    
    sounds = {
        'attack': 'sfx/hammer_hit.wav',
        'empty': 'sfx/empty_gun.wav',
    }