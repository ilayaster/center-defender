import pygame
import sys
import os
from settings import *
from ui import DropdownButton, PauseMenu
from entities import Core
from utils import SpriteManager
from core.constants import *
from core.assets import AssetManager
from core.ui_factory import UIFactory
from core.gameplay import GameplayManager
from core.renderer import Renderer
from core.weapons import WeaponManager

class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.info = pygame.display.Info()
        self.native_res = (self.info.current_w, self.info.current_h)
        
        self.available_resolutions = []
        seen = set()
        for w, h in STANDARD_RESOLUTIONS:
            if w <= self.native_res[0] and h <= self.native_res[1] and (w, h) not in seen:
                self.available_resolutions.append((w, h))
                seen.add((w, h))
        if self.native_res not in seen:
            self.available_resolutions.append(self.native_res)
        self.available_resolutions.sort(key=lambda x: (x[0], x[1]))

        self.screen = pygame.display.set_mode(self.native_res, pygame.RESIZABLE)
        pygame.display.set_caption("Defend the Core")
        self.clock = pygame.time.Clock()

        self.sprite_manager = SpriteManager()
        self.asset_manager = AssetManager(self.sprite_manager, self.screen)
        self.pause_menu = PauseMenu()
        self.weapon_manager = WeaponManager()

        self.game_settings = get_default_settings(self.native_res)
        self.current_state = STATE_MENU
        self.core = None
        self.gameplay = None
        self.ui_elements = {}

        # --- Консоль разработчика и история ---
        self.console_active = False
        self.console_input = ""
        self.console_history = []
        self.history_index = -1
        self.temp_input = ""

        self.apply_settings()

    def apply_settings(self):
        w, h = self.game_settings['resolution']
        if self.game_settings['display_mode'] == 'Borderless':
            flags, w, h = pygame.NOFRAME, self.native_res[0], self.native_res[1]
            self.game_settings['resolution'] = self.native_res
        elif self.game_settings['display_mode'] == 'Fullscreen':
            flags = pygame.SCALED | pygame.FULLSCREEN
        else:
            flags = pygame.RESIZABLE

        self.screen = pygame.display.set_mode((w, h), flags)
        pygame.display.set_caption("Defend the Core")
        pygame.event.pump()

        self.asset_manager.load_all()

        if self.core is None:
            self.core = Core(w, h, self.sprite_manager)
        else:
            self.core.update_size(w, h, self.sprite_manager)

        if self.gameplay is None:
            self.gameplay = GameplayManager(self.game_settings, self.core, self.sprite_manager)

        sw, sh = self.screen.get_width(), self.screen.get_height()
        cx, cy = sw // 2, sh // 2
        btn_w, btn_h, dd_w, dd_h = 200, 45, 240, 40
        
        self.ui_elements = UIFactory.create_all(
            cx, cy, btn_w, btn_h, dd_w, dd_h,
            self.asset_manager.font_small, self.asset_manager.font_medium,
            self.available_resolutions, self.native_res, self.game_settings, sw,
            self.pause_menu
        )

    def reset_game(self):
        """Сбрасывает игру и переходит в состояние PLAYING"""
        self.gameplay.reset()
        self.weapon_manager.reset_timers()  # <-- ИСПРАВЛЕНИЕ: Сброс оружия при новом раунде
        self.current_state = STATE_PLAYING

    def update_difficulty(self):
        self.gameplay.update_difficulty()

    def reset_to_defaults(self):
        self.game_settings = get_default_settings(self.native_res)
        self.update_difficulty()
        self.apply_settings()

    def toggle_pause(self):
        if self.current_state == STATE_PLAYING:
            self.current_state = STATE_PAUSED
        elif self.current_state == STATE_PAUSED:
            self.current_state = STATE_PLAYING

    def _execute_console_command(self):
        """Обрабатывает команды консоли"""
        cmd_str = self.console_input.strip()
        if not cmd_str:
            return
        
        self.console_history.append(cmd_str)
        if len(self.console_history) > 20:
            self.console_history.pop(0)
        
        parts = cmd_str.split()
        cmd = parts[0].lower()
        
        if cmd == "skip_time":
            seconds = 60
            if len(parts) > 1:
                try:
                    seconds = int(parts[1])
                except ValueError:
                    pass
            self.gameplay.time_survived += seconds
            print(f"[Console] Time skipped by {seconds}s. Current: {self.gameplay.time_survived:.1f}s")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- 1. ЛОГИКА КОНСОЛИ (Приоритетная, перехватывает все клавиши) ---
            if self.current_state == STATE_PLAYING and self.console_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.console_active = False
                        self.console_input = ""
                        self.history_index = -1
                    elif event.key == pygame.K_RETURN:
                        self._execute_console_command()
                        self.console_active = False
                        self.console_input = ""
                        self.history_index = -1
                        self.temp_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.console_input = self.console_input[:-1]
                    elif event.key == pygame.K_UP:
                        if self.console_history:
                            if self.history_index == -1:
                                self.temp_input = self.console_input
                            self.history_index = min(self.history_index + 1, len(self.console_history) - 1)
                            self.console_input = self.console_history[-(self.history_index + 1)]
                    elif event.key == pygame.K_DOWN:
                        if self.history_index > -1:
                            self.history_index -= 1
                            if self.history_index == -1:
                                self.console_input = self.temp_input
                            else:
                                self.console_input = self.console_history[-(self.history_index + 1)]
                    elif event.unicode and event.unicode.isprintable():
                        self.console_input += event.unicode
                return  # Прерываем обработку остальных событий, пока консоль открыта

            # --- 2. ОБЫЧНАЯ ЛОГИКА ---
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_state in (STATE_PLAYING, STATE_PAUSED):
                    self.toggle_pause()

            if self.current_state == STATE_MENU:
                if self.ui_elements['btn_start'].is_clicked(event):
                    self.current_state = STATE_WEAPON_SELECT
                elif self.ui_elements['btn_settings'].is_clicked(event):
                    self.current_state = STATE_SETTINGS
                elif self.ui_elements['btn_quit'].is_clicked(event):
                    pygame.quit()
                    sys.exit()

            elif self.current_state == STATE_WEAPON_SELECT:
                if self.ui_elements['btn_weapon_sword'].is_clicked(event):
                    self.weapon_manager.set_weapon('sword')
                    self.current_state = STATE_DIFFICULTY
                elif self.ui_elements['btn_weapon_hammer'].is_clicked(event):
                    self.weapon_manager.set_weapon('hammer')
                    self.current_state = STATE_DIFFICULTY
                elif self.ui_elements['btn_weapon_pistol'].is_clicked(event):
                    self.weapon_manager.set_weapon('pistol')
                    self.current_state = STATE_DIFFICULTY
                elif self.ui_elements['btn_wep_back'].is_clicked(event):
                    self.current_state = STATE_MENU

            elif self.current_state == STATE_DIFFICULTY:
                if self.ui_elements['btn_easy'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Easy'
                    self.update_difficulty()
                    self.reset_game()
                elif self.ui_elements['btn_normal'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Normal'
                    self.update_difficulty()
                    self.reset_game()
                elif self.ui_elements['btn_hard'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Hard'
                    self.update_difficulty()
                    self.reset_game()
                elif self.ui_elements['btn_diff_back'].is_clicked(event):
                    self.current_state = STATE_WEAPON_SELECT

            elif self.current_state == STATE_SETTINGS:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for el in self.ui_elements.values():
                        if isinstance(el, DropdownButton):
                            if not el.rect.collidepoint(event.pos) and \
                               not any(r.collidepoint(event.pos) for _, r, _ in el.get_visible_rects()):
                                el.is_open, el.scroll_offset = False, 0
                
                res_val = self.ui_elements['dd_res'].handle_event(event)
                if res_val:
                    self.game_settings['resolution'] = tuple(map(int, res_val.split('x')))
                    self.apply_settings()
                    
                disp_val = self.ui_elements['dd_display'].handle_event(event)
                if disp_val:
                    self.game_settings['display_mode'] = disp_val
                    self.apply_settings()

                if self.ui_elements['btn_hitboxes'].is_clicked(event):
                    self.game_settings['show_hitboxes'] = not self.game_settings['show_hitboxes']
                    hb_text = "Hitboxes: ON" if self.game_settings['show_hitboxes'] else "Hitboxes: OFF"
                    self.ui_elements['btn_hitboxes'].text = hb_text

                if self.ui_elements['btn_reset'].is_clicked(event):
                    self.reset_to_defaults()
                elif self.ui_elements['btn_back'].is_clicked(event):
                    self.current_state = STATE_MENU

            elif self.current_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SLASH or event.key == pygame.K_KP_DIVIDE:
                        self.console_active = True
                    elif event.key == pygame.K_r:
                        self.weapon_manager.request_reload()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.weapon_manager.request_attack()

            elif self.current_state == STATE_PAUSED:
                action = self.pause_menu.handle_event(event)
                if action == 'resume':
                    self.toggle_pause()
                elif action == 'quit_to_menu':
                    self.current_state = STATE_MENU

            elif self.current_state == STATE_GAMEOVER:
                if self.ui_elements['btn_retry'].is_clicked(event):
                    self.reset_game()
                elif self.ui_elements['btn_menu'].is_clicked(event):
                    self.current_state = STATE_MENU

    def update(self, dt, sw, sh):
        if self.current_state == STATE_PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            hits = self.weapon_manager.update(dt, mouse_pos, self.gameplay.enemies)
            if hits > 0:
                self.gameplay.score += hits
                
            if self.gameplay.update(dt, sw, sh):
                self.current_state = STATE_GAMEOVER

    def draw(self, sw, sh):
        Renderer.draw(
            self.current_state, self.screen,
            self.asset_manager.font_small, self.asset_manager.font_medium,
            self.asset_manager.font_large,
            self.ui_elements, self.core, self.gameplay.enemies,
            self.game_settings['show_hitboxes'], self.pause_menu,
            self.gameplay.time_survived, self.gameplay.score, self.gameplay.game_won,
            sw, sh,
            self.console_active, self.console_input  # <-- Передаем состояние консоли
        )
        
        # Рисуем оружие только если игра идет и консоль ЗАКРЫТА
        if self.current_state == STATE_PLAYING and not self.console_active:
            mouse_pos = pygame.mouse.get_pos()
            self.weapon_manager.draw(self.screen, mouse_pos)

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            sw, sh = self.screen.get_width(), self.screen.get_height()
            self.handle_events()
            self.update(dt, sw, sh)
            self.draw(sw, sh)
            pygame.display.flip()

def run():
    game = Game()
    game.run()