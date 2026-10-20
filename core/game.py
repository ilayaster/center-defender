import pygame
import sys
import math
import os
from settings import *
from ui import Button, DropdownButton
from entities import Enemy
from utils import SpriteManager

class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        
        self.info = pygame.display.Info()
        self.native_res = (self.info.current_w, self.info.current_h)
        
        standard_resolutions = [
            (640, 480), (800, 600), (1024, 768), (1280, 720), (1280, 800),
            (1366, 768), (1440, 900), (1600, 900), (1680, 1050),
            (1920, 1080), (2560, 1440), (3840, 2160)
        ]
        
        self.available_resolutions = []
        seen = set()
        for w, h in standard_resolutions:
            if w <= self.native_res[0] and h <= self.native_res[1] and (w, h) not in seen:
                self.available_resolutions.append((w, h))
                seen.add((w, h))
        
        if self.native_res not in seen:
            self.available_resolutions.append(self.native_res)
        self.available_resolutions.sort(key=lambda x: (x[0], x[1]))

        self.screen = pygame.display.set_mode(self.native_res, 0)
        pygame.display.set_caption("Defend the Core")
        self.clock = pygame.time.Clock()

        self.sprite_manager = SpriteManager()
        self.load_sprites()

        self.DEFAULT_SETTINGS = {
            'difficulty': 'Normal',
            'resolution': self.native_res,
            'display_mode': 'Borderless',
            'enemy_speed': 150,
            'spawn_interval': 1.0,
            'show_hitboxes': False
        }
        self.game_settings = self.DEFAULT_SETTINGS.copy()

        self.STATE_MENU, self.STATE_SETTINGS, self.STATE_PLAYING, self.STATE_GAMEOVER = 0, 1, 2, 3
        self.current_state = self.STATE_MENU

        self.enemies, self.score, self.time_left, self.spawn_timer = [], 0, GAME_DURATION, 0
        self.game_won = False
        self.ui_elements = {}

        self.apply_settings()
        self.update_difficulty()

    def load_sprites(self):
        scale_factor = self.screen.get_height() / 1080.0
        self.sprite_manager.load('core', 'core.png', (int(128 * scale_factor), int(128 * scale_factor)))
        self.sprite_manager.load('enemy', 'enemy.png', (int(48 * scale_factor), int(48 * scale_factor)))

    def get_fonts(self):
        sh = self.screen.get_height()
        # УМЕНЬШЕНЫ размеры шрифтов
        size_small = max(12, min(16, sh // 60))
        size_medium = max(14, min(20, sh // 45))
        size_large = max(24, min(36, sh // 25))
        
        try:
            font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "pixel.ttf")
            font_small = pygame.font.Font(font_path, size_small)
            font_medium = pygame.font.Font(font_path, size_medium)
            font_large = pygame.font.Font(font_path, size_large)
        except FileNotFoundError:
            font_small = pygame.font.SysFont("courier", size_small, bold=True)
            font_medium = pygame.font.SysFont("courier", size_medium, bold=True)
            font_large = pygame.font.SysFont("courier", size_large, bold=True)
            
        return font_small, font_medium, font_large

    def create_ui(self):
        self.ui_elements.clear()
        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx, cy = sw // 2, sh // 2
        btn_w, btn_h, dd_w, dd_h = 200, 45, 240, 40
        
        self.ui_elements['btn_start'] = Button(cx - btn_w//2, cy - 60, btn_w, btn_h, "START GAME", self.font_medium)
        self.ui_elements['btn_settings'] = Button(cx - btn_w//2, cy + 10, btn_w, btn_h, "SETTINGS", self.font_medium)
        self.ui_elements['btn_quit'] = Button(cx - btn_w//2, cy + 80, btn_w, btn_h, "QUIT", self.font_medium)
        
        self.ui_elements['dd_diff'] = DropdownButton(cx - dd_w//2, cy - 100, dd_w, dd_h, f"Difficulty: {self.game_settings['difficulty']}", ['Easy', 'Normal', 'Hard'], self.font_small, sw)
        
        res_options = [f"{w}x{h}" for w, h in self.available_resolutions]
        current_res_text = "Native" if self.game_settings['resolution'] == self.native_res else f"{self.game_settings['resolution'][0]}x{self.game_settings['resolution'][1]}"
        self.ui_elements['dd_res'] = DropdownButton(cx - dd_w//2, cy - 40, dd_w, dd_h, f"Resolution: {current_res_text}", res_options, self.font_small, sw, enabled=(self.game_settings['display_mode'] != 'Borderless'), max_visible=6)
        
        self.ui_elements['dd_display'] = DropdownButton(cx - dd_w//2, cy + 20, dd_w, dd_h, f"Display: {self.game_settings['display_mode']}", ['Windowed', 'Fullscreen', 'Borderless'], self.font_small, sw)
        
        # НОВОЕ: Обычная кнопка для хитбоксов (не dropdown)
        hb_text = "Hitboxes: ON" if self.game_settings['show_hitboxes'] else "Hitboxes: OFF"
        self.ui_elements['btn_hitboxes'] = Button(cx - btn_w//2, cy + 80, btn_w, btn_h, hb_text, self.font_small)
        
        self.ui_elements['btn_reset'] = Button(cx - btn_w//2, cy + 140, btn_w, btn_h, "RESET DEFAULTS", self.font_small)
        self.ui_elements['btn_back'] = Button(cx - btn_w//2, cy + 200, btn_w, btn_h, "BACK", self.font_medium)
        self.ui_elements['btn_retry'] = Button(cx - btn_w//2, cy + 50, btn_w, btn_h, "RETRY", self.font_medium)
        self.ui_elements['btn_menu'] = Button(cx - btn_w//2, cy + 120, btn_w, btn_h, "MAIN MENU", self.font_medium)

    def apply_settings(self):
        w, h = self.game_settings['resolution']
        if self.game_settings['display_mode'] == 'Borderless':
            flags, w, h = pygame.NOFRAME, self.native_res[0], self.native_res[1]
            self.game_settings['resolution'] = self.native_res
        elif self.game_settings['display_mode'] == 'Fullscreen':
            flags = pygame.SCALED | pygame.FULLSCREEN
        else:
            flags = 0
            
        self.screen = pygame.display.set_mode((w, h), flags)
        pygame.display.set_caption("Defend the Core")
        pygame.event.pump()
        
        self.load_sprites()
        self.font_small, self.font_medium, self.font_large = self.get_fonts()
        self.create_ui()

    def reset_game(self):
        self.enemies, self.score, self.time_left, self.spawn_timer, self.game_won = [], 0, GAME_DURATION, 0, False
        self.current_state = self.STATE_PLAYING

    def update_difficulty(self):
        diffs = {'Easy': (100, 1.5), 'Normal': (150, 1.0), 'Hard': (220, 0.5)}
        self.game_settings['enemy_speed'], self.game_settings['spawn_interval'] = diffs[self.game_settings['difficulty']]

    def reset_to_defaults(self):
        self.game_settings = self.DEFAULT_SETTINGS.copy()
        self.update_difficulty()
        self.apply_settings()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.current_state == self.STATE_MENU:
                if self.ui_elements['btn_start'].is_clicked(event): self.reset_game()
                elif self.ui_elements['btn_settings'].is_clicked(event): self.current_state = self.STATE_SETTINGS
                elif self.ui_elements['btn_quit'].is_clicked(event): pygame.quit(); sys.exit()

            elif self.current_state == self.STATE_SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for el in self.ui_elements.values():
                        if isinstance(el, DropdownButton):
                            if not el.rect.collidepoint(event.pos) and not any(r.collidepoint(event.pos) for _, r, _ in el.get_visible_rects()):
                                el.is_open, el.scroll_offset = False, 0

                diff_val = self.ui_elements['dd_diff'].handle_event(event)
                if diff_val:
                    self.game_settings['difficulty'] = diff_val
                    self.update_difficulty()
                    self.ui_elements['dd_diff'].text = f"Difficulty: {diff_val}"
                    
                res_val = self.ui_elements['dd_res'].handle_event(event)
                if res_val:
                    self.game_settings['resolution'] = tuple(map(int, res_val.split('x')))
                    self.apply_settings()
                    
                disp_val = self.ui_elements['dd_display'].handle_event(event)
                if disp_val:
                    self.game_settings['display_mode'] = disp_val
                    self.apply_settings()

                # НОВОЕ: Обработка клика по кнопке хитбоксов (переключение)
                if self.ui_elements['btn_hitboxes'].is_clicked(event):
                    self.game_settings['show_hitboxes'] = not self.game_settings['show_hitboxes']
                    hb_text = "Hitboxes: ON" if self.game_settings['show_hitboxes'] else "Hitboxes: OFF"
                    self.ui_elements['btn_hitboxes'].text = hb_text

                if self.ui_elements['btn_reset'].is_clicked(event): self.reset_to_defaults()
                elif self.ui_elements['btn_back'].is_clicked(event): self.current_state = self.STATE_MENU

            elif self.current_state == self.STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for enemy in self.enemies:
                        if math.hypot(mouse_pos[0] - enemy.x, mouse_pos[1] - enemy.y) < enemy.radius:
                            enemy.is_dead = True
                            self.score += 1
                            break

            elif self.current_state == self.STATE_GAMEOVER:
                if self.ui_elements['btn_retry'].is_clicked(event): self.reset_game()
                elif self.ui_elements['btn_menu'].is_clicked(event): self.current_state = self.STATE_MENU

    def draw(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()

        if self.current_state == self.STATE_MENU:
            self.screen.fill(MENU_BG)
            title = self.font_large.render("DEFEND THE CORE", True, CORE_COLOR)
            self.screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 150))
            self.ui_elements['btn_start'].draw(self.screen)
            self.ui_elements['btn_settings'].draw(self.screen)
            self.ui_elements['btn_quit'].draw(self.screen)

        elif self.current_state == self.STATE_SETTINGS:
            self.screen.fill(MENU_BG)
            title = self.font_large.render("SETTINGS", True, TEXT_COLOR)
            self.screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 180))
            self.ui_elements['dd_diff'].draw(self.screen)
            self.ui_elements['dd_res'].draw(self.screen)
            self.ui_elements['dd_display'].draw(self.screen)
            self.ui_elements['btn_hitboxes'].draw(self.screen)
            self.ui_elements['btn_reset'].draw(self.screen)
            self.ui_elements['btn_back'].draw(self.screen)

        elif self.current_state == self.STATE_PLAYING:
            self.time_left -= self.dt
            if self.time_left <= 0:
                self.time_left, self.game_won, self.current_state = 0, True, self.STATE_GAMEOVER

            self.spawn_timer += self.dt
            if self.spawn_timer >= self.game_settings['spawn_interval']:
                self.enemies.append(Enemy(self.game_settings, sw, sh, self.sprite_manager))
                self.spawn_timer = 0
                if self.game_settings['spawn_interval'] > 0.2:
                    self.game_settings['spawn_interval'] -= 0.02

            for enemy in self.enemies:
                if enemy.update(self.dt, sw, sh):
                    self.game_won, self.current_state = False, self.STATE_GAMEOVER

            self.enemies = [e for e in self.enemies if not e.is_dead]
            self.screen.fill(BG_COLOR)
            
            # Отрисовка ядра и таймера над ним
            core_sprite = self.sprite_manager.get('core')
            if core_sprite:
                core_rect = core_sprite.get_rect(center=(sw // 2, sh // 2))
                self.screen.blit(core_sprite, core_rect)
                
                # Таймер над ядром
                timer_text = self.font_small.render(f"TIME: {math.ceil(self.time_left)}", True, TEXT_COLOR)
                timer_rect = timer_text.get_rect(center=(sw // 2, core_rect.top - 15))
                self.screen.blit(timer_text, timer_rect)
                
                # НОВОЕ: Круглый хитбокс ядра (реальный радиус коллизии)
                if self.game_settings['show_hitboxes']:
                    core_hitbox_radius = CORE_RADIUS * (sh / 1080.0)
                    pygame.draw.circle(self.screen, (0, 255, 0), (sw // 2, sh // 2), int(core_hitbox_radius), 2)

            for enemy in self.enemies:
                enemy.draw(self.screen, self.game_settings['show_hitboxes'])

            # НОВОЕ: Счет теперь правильно позиционирован (с учетом ширины текста)
            score_text = self.font_small.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            self.screen.blit(score_text, (sw - score_text.get_width() - 20, 20))

        elif self.current_state == self.STATE_GAMEOVER:
            self.screen.fill(BG_COLOR)
            core_sprite = self.sprite_manager.get('core')
            if core_sprite:
                core_rect = core_sprite.get_rect(center=(sw // 2, sh // 2))
                self.screen.blit(core_sprite, core_rect)
                
            for enemy in self.enemies: 
                enemy.draw(self.screen, self.game_settings['show_hitboxes'])
            
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            res_text = self.font_large.render("VICTORY!" if self.game_won else "DEFEAT", True, CORE_COLOR if self.game_won else ENEMY_COLOR)
            self.screen.blit(res_text, (sw//2 - res_text.get_width()//2, sh//2 - 100))
            
            stats_text = self.font_medium.render(f"FINAL SCORE: {self.score}", True, TEXT_COLOR)
            self.screen.blit(stats_text, (sw//2 - stats_text.get_width()//2, sh//2 - 20))
            
            self.ui_elements['btn_retry'].draw(self.screen)
            self.ui_elements['btn_menu'].draw(self.screen)

    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.draw()
            pygame.display.flip()

def run():
    game = Game()
    game.run()