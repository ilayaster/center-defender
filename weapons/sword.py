from weapons.base import BaseWeapon

class Sword(BaseWeapon):
    name = "SWORD"
    damage = 1
    range = 60
    
    cooldown = 0.45
    windup_duration = 0.0
    swing_duration = 0.15
    
    magazine_size = 0
    reload_duration = 0.0
    
    swing_color = (255, 255, 150)
    cursor_color = (220, 220, 220)
    
    sounds = {
        'attack': 'sfx/sword_swing.wav',
        'empty': 'sfx/empty_gun.wav',
    }