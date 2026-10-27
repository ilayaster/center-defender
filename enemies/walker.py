from enemies.base import BaseEnemy

class Walker(BaseEnemy):
    enemy_type = "enemy-1"
    display_name = "Walker"
    max_hp = 1
    speed_multiplier = 1.0
    hitbox_radius_multiplier = 20.0
    anim_state = 'walk'
    frame_duration = 0.15
    hitbox_color = (255, 0, 0)
    slowed_hitbox_color = (100, 100, 255)