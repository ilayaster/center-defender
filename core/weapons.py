from weapons import get_weapon, get_available_weapons, DEFAULT_WEAPON

class WeaponManager:
    def __init__(self):
        self.current_weapon_key = DEFAULT_WEAPON
        self.weapon = get_weapon(self.current_weapon_key)
        self.volume = 0.5
        self.weapon.set_volume(self.volume)
    
    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        self.weapon.set_volume(self.volume)
    
    def set_weapon(self, weapon_key):
        if weapon_key in get_available_weapons():
            self.current_weapon_key = weapon_key
            self.weapon = get_weapon(self.current_weapon_key)
            self.weapon.set_volume(self.volume)
    
    def reset_timers(self):
        self.weapon.reset()
    
    def request_attack(self, mouse_pos):
        return self.weapon.request_attack(mouse_pos)
    
    def request_reload(self):
        self.weapon.request_reload()
    
    def update(self, dt, mouse_pos, enemies):
        return self.weapon.update(dt, mouse_pos, enemies)
    
    def draw(self, surface, current_mouse_pos):
        self.weapon.draw(surface, current_mouse_pos)