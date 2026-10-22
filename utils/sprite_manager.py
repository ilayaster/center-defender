import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.animations = {}

    def load(self, name, filename, target_size=None):
        filepath = os.path.join(SPRITES_DIR, filename)
        try:
            img = pygame.image.load(filepath).convert_alpha()
            if target_size:
                img = pygame.transform.scale(img, target_size)
            self.sprites[name] = img
        except pygame.error as e:
            print(f"Warning: Could not load sprite '{filepath}'. Error: {e}")
            size = target_size if target_size else (64, 64)
            fallback = pygame.Surface(size, pygame.SRCALPHA)
            fallback.fill((255, 0, 255))
            self.sprites[name] = fallback

    def get(self, name):
        return self.sprites.get(name)

    def load_enemy_animations(self, base_folder="enemies"):
        enemies_dir = os.path.join(SPRITES_DIR, base_folder)
        if not os.path.exists(enemies_dir):
            print(f"Warning: Enemies directory not found at {enemies_dir}")
            return

        for enemy_type in os.listdir(enemies_dir):
            type_path = os.path.join(enemies_dir, enemy_type)
            if not os.path.isdir(type_path):
                continue

            self.animations[enemy_type] = {}
            
            for filename in os.listdir(type_path):
                if filename.endswith(".png"):
                    name_without_ext = os.path.splitext(filename)[0]
                    parts = name_without_ext.rsplit('_', 1)
                    
                    if len(parts) == 2:
                        state = parts[0]
                        try:
                            frame_idx = int(parts[1])
                        except ValueError:
                            continue
                    else:
                        state = "default"
                        frame_idx = 0

                    if state not in self.animations[enemy_type]:
                        self.animations[enemy_type][state] = []
                    
                    full_path = os.path.join(type_path, filename)
                    try:
                        surf = pygame.image.load(full_path).convert_alpha()
                        # <-- УВЕЛИЧЕНИЕ СПРАЙТА В 3 РАЗА ПРИ ЗАГРУЗКЕ
                        orig_w, orig_h = surf.get_width(), surf.get_height()
                        scaled_surf = pygame.transform.scale(surf, (orig_w * 3, orig_h * 3))
                        
                        self.animations[enemy_type][state].append((frame_idx, scaled_surf))
                    except pygame.error:
                        pass

            for state in self.animations[enemy_type]:
                self.animations[enemy_type][state].sort(key=lambda x: x[0])
                self.animations[enemy_type][state] = [frame[1] for frame in self.animations[enemy_type][state]]

    def get_animation(self, enemy_type, state="walk"):
        if enemy_type in self.animations:
            if state in self.animations[enemy_type]:
                return self.animations[enemy_type][state]
            first_state = next(iter(self.animations[enemy_type].values()))
            return first_state
        
        fallback = self.get(enemy_type)
        if fallback:
            return [fallback]
        return [pygame.Surface((32, 32), pygame.SRCALPHA)]