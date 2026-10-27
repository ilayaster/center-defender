from enemies.base import BaseEnemy

class Shield(BaseEnemy):
    enemy_type = "enemy-3"
    display_name = "Shield"
    max_hp = 3
    speed_multiplier = 0.3
    hitbox_radius_multiplier = 20.0
    anim_state = 'walk'
    frame_duration = 0.15
    hitbox_color = (255, 0, 0)
    slowed_hitbox_color = (100, 100, 255)