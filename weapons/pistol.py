from weapons.base import BaseWeapon

class Pistol(BaseWeapon):
    name = "PISTOL"
    damage = 1
    range = 40
    
    cooldown = 0.15
    windup_duration = 0.0
    swing_duration = 0.1
    
    magazine_size = 6
    reload_duration = 1.5
    
    swing_color = (255, 255, 0)
    cursor_color = (200, 200, 255)
    
    sounds = {
        'attack': 'sfx/gun_shot.wav',
        'empty': 'sfx/empty_gun.wav',
        'reload': 'sfx/reloaded.wav',
    }