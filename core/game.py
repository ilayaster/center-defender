import os
os.environ['SDL_RENDER_SCALE_QUALITY'] = 'nearest'

import pygame
import sys
import random
from settings import *
from ui import DropdownButton, PauseMenu
from cores import get_core, get_available_cores
from utils.sprite_manager import SpriteManager
from core.constants import *
from core.assets import AssetManager
from core.ui_factory import UIFactory
from core.gameplay import GameplayManager
from core.renderer import Renderer
from core.weapons import WeaponManager
from core.effects import EffectsManager

class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.mixer.init()
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
        pygame.display.set_caption("CORE DEFENSE")
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
        self.selected_core_type = 'plosive'

        # --- Новые флаги для объединенного экрана выбора ---
        self.weapon_selected = None
        self.core_selected = None
        # ---------------------------------------------------

        self.console_active = False
        self.console_input = ""
        self.console_history = []
        self.history_index = -1
        self.temp_input = ""

        self.game_surface = None
        self.effects_manager = None

        self.shake_timer = 0.0
        self.shake_intensity = 0.0

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
        pygame.display.set_caption("CORE DEFENSE")
        pygame.event.pump()

        self.game_surface = pygame.Surface((w, h))
        if self.effects_manager is None:
            self.effects_manager = EffectsManager(w, h)
        else:
            self.effects_manager.resize(w, h)
        self.effects_manager.mode = self.game_settings.get('effect_mode', 'OFF')

        self.asset_manager.load_all()
        self.sprite_manager.load_enemy_animations("enemies")

        if self.core is None or self.core.name != self.selected_core_type.upper():
            self.core = get_core(self.selected_core_type, w, h, self.sprite_manager)
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
        
        self.weapon_manager.set_volume(self.game_settings.get('sfx_volume', 0.5))
        pygame.mixer.music.set_volume(self.game_settings.get('music_volume', 0.5))
        
        self.update_cursor_visibility()

    def update_cursor_visibility(self):
        if self.current_state == STATE_PLAYING and not self.console_active:
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

    def reset_game(self):
        sw, sh = self.screen.get_width(), self.screen.get_height()
        self.core = get_core(self.selected_core_type, sw, sh, self.sprite_manager)
        self.gameplay = GameplayManager(self.game_settings, self.core, self.sprite_manager)
        self.weapon_manager.reset_timers()
        self.current_state = STATE_PLAYING
        
        self.update_cursor_visibility()
        
        music_path = "music/music_round_1.wav"
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.game_settings.get('music_volume', 0.5))
            pygame.mixer.music.play(-1)

    def stop_music(self):
        pygame.mixer.music.stop()

    def update_difficulty(self):
        if self.gameplay:
            self.gameplay.update_difficulty()

    def reset_to_defaults(self):
        self.game_settings = get_default_settings(self.native_res)
        self.update_difficulty()
        self.apply_settings()

    def toggle_pause(self):
        if self.current_state == STATE_PLAYING:
            self.current_state = STATE_PAUSED
            pygame.mixer.music.pause()
        elif self.current_state == STATE_PAUSED:
            self.current_state = STATE_PLAYING
            pygame.mixer.music.unpause()
        self.update_cursor_visibility()

    def _execute_console_command(self):
        cmd_str = self.console_input.strip()
        if not cmd_str: return
        
        self.console_history.append(cmd_str)
        if len(self.console_history) > 20: self.console_history.pop(0)
        
        parts = cmd_str.split()
        cmd = parts[0].lower()
        if cmd == "skip_time":
            seconds = 60
            if len(parts) > 1:
                try: seconds = int(parts[1])
                except ValueError: pass
            self.gameplay.time_survived += seconds

    def _clear_loadout_selection(self):
        """Сбрасывает выбор оружия и ядра."""
        self.weapon_selected = None
        self.core_selected = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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
                            if self.history_index == -1: self.temp_input = self.console_input
                            self.history_index = min(self.history_index + 1, len(self.console_history) - 1)
                            self.console_input = self.console_history[-(self.history_index + 1)]
                    elif event.key == pygame.K_DOWN:
                        if self.history_index > -1:
                            self.history_index -= 1
                            if self.history_index == -1: self.console_input = self.temp_input
                            else: self.console_input = self.console_history[-(self.history_index + 1)]
                    elif event.unicode and event.unicode.isprintable():
                        self.console_input += event.unicode
                self.update_cursor_visibility()
                return

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_state in (STATE_PLAYING, STATE_PAUSED):
                    self.toggle_pause()

            if self.current_state == STATE_MENU:
                if self.ui_elements['btn_start'].is_clicked(event): 
                    self.current_state = STATE_WEAPON_SELECT
                    self.stop_music()
                elif self.ui_elements['btn_settings'].is_clicked(event): 
                    self.current_state = STATE_SETTINGS
                elif self.ui_elements['btn_quit'].is_clicked(event):
                    pygame.quit()
                    sys.exit()

            elif self.current_state == STATE_WEAPON_SELECT:
                # --- Клик по оружию ---
                weapon_clicked = None
                for w in ['sword', 'hammer', 'pistol']:
                    if self.ui_elements[f'btn_weapon_{w}'].is_clicked(event):
                        weapon_clicked = w
                        break

                if weapon_clicked:
                    if self.weapon_selected == weapon_clicked:
                        # Повторный клик по выбранному — отмена выбора оружия (и ядра)
                        self.weapon_selected = None
                        self.core_selected = None
                    else:
                        # Выбираем новое оружие, сбрасываем ядро
                        self.weapon_selected = weapon_clicked
                        self.weapon_manager.set_weapon(weapon_clicked)
                        self.core_selected = None

                # --- Клик по ядру (только если оружие выбрано) ---
                if self.weapon_selected is not None:
                    core_clicked = None
                    for c in ['plosive', 'slow']:
                        if self.ui_elements[f'btn_core_{c}'].is_clicked(event):
                            core_clicked = c
                            break
                    if core_clicked:
                        if self.core_selected == core_clicked:
                            # Повторный клик — отмена выбора ядра
                            self.core_selected = None
                        else:
                            self.core_selected = core_clicked
                            self.selected_core_type = core_clicked

                # --- Клик по NEXT (только если ядро выбрано) ---
                if self.core_selected is not None and self.ui_elements['btn_next'].is_clicked(event):
                    self.current_state = STATE_DIFFICULTY

                # --- Клик по BACK ---
                if self.ui_elements['btn_sel_back'].is_clicked(event):
                    if self.core_selected is not None:
                        # Отменяем выбор ядра
                        self.core_selected = None
                    elif self.weapon_selected is not None:
                        # Отменяем выбор оружия
                        self.weapon_selected = None
                    else:
                        # Возврат в главное меню
                        self.current_state = STATE_MENU

            elif self.current_state == STATE_DIFFICULTY:
                if self.ui_elements['btn_easy'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Easy'
                    self.reset_game()
                elif self.ui_elements['btn_normal'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Normal'
                    self.reset_game()
                elif self.ui_elements['btn_hard'].is_clicked(event):
                    self.game_settings['difficulty'] = 'Hard'
                    self.reset_game()
                elif self.ui_elements['btn_diff_back'].is_clicked(event): 
                    self.current_state = STATE_WEAPON_SELECT

            elif self.current_state == STATE_SETTINGS:
                if self.ui_elements['slider_volume'].handle_event(event):
                    self.game_settings['sfx_volume'] = self.ui_elements['slider_volume'].value
                    self.weapon_manager.set_volume(self.game_settings['sfx_volume'])
                
                if self.ui_elements['slider_music_volume'].handle_event(event):
                    self.game_settings['music_volume'] = self.ui_elements['slider_music_volume'].value
                    pygame.mixer.music.set_volume(self.game_settings['music_volume'])
                
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

                eff_val = self.ui_elements['dd_effects'].handle_event(event)
                if eff_val:
                    self.game_settings['effect_mode'] = eff_val
                    self.ui_elements['dd_effects'].text = f"Effects: {eff_val}"
                    if self.effects_manager:
                        self.effects_manager.mode = eff_val

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
                    mouse_pos = pygame.mouse.get_pos()
                    self.weapon_manager.request_attack(mouse_pos)

            elif self.current_state == STATE_PAUSED:
                action = self.pause_menu.handle_event(event)
                if action == 'resume': 
                    self.toggle_pause()
                elif action == 'quit_to_menu': 
                    self.current_state = STATE_MENU
                    self._clear_loadout_selection()
                    self.stop_music()

            elif self.current_state == STATE_GAMEOVER:
                if self.ui_elements['btn_retry'].is_clicked(event): 
                    self.reset_game()
                elif self.ui_elements['btn_menu'].is_clicked(event): 
                    self.current_state = STATE_MENU
                    self._clear_loadout_selection()
                    self.stop_music()
            
            self.update_cursor_visibility()

    def update(self, dt, sw, sh):
        if self.current_state == STATE_PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            hits = self.weapon_manager.update(dt, mouse_pos, self.gameplay.enemies)
            if hits > 0: self.gameplay.score += hits
            
            prev_hp = self.core.current_hp
            if self.gameplay.update(dt, sw, sh):
                self.current_state = STATE_GAMEOVER
                self.stop_music()
            
            if self.core.current_hp < prev_hp:
                self.shake_timer = 0.3
                self.shake_intensity = 12.0

    def draw(self, sw, sh):
        Renderer.draw(
            self.current_state, self.game_surface,
            self.asset_manager.font_small, self.asset_manager.font_medium,
            self.asset_manager.font_large,
            self.ui_elements, self.core, self.gameplay.enemies,
            self.game_settings['show_hitboxes'], self.pause_menu,
            self.gameplay.time_survived, self.gameplay.score, self.gameplay.game_won,
            sw, sh, self.console_active, self.console_input,
            self.sprite_manager,
            self.weapon_selected, self.core_selected
        )
        
        if self.current_state == STATE_PLAYING and not self.console_active:
            mouse_pos = pygame.mouse.get_pos()
            self.weapon_manager.draw(self.game_surface, mouse_pos)
            
        if self.gameplay:
            self.gameplay.draw_particles(self.game_surface)
            
        if self.effects_manager:
            self.effects_manager.apply(self.game_surface)
            
        offset_x = 0
        offset_y = 0
        if self.shake_timer > 0:
            self.shake_timer -= self.clock.get_time() / 1000.0
            if self.shake_timer > 0:
                offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
                offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
                self.shake_intensity *= 0.9
        
        self.screen.blit(self.game_surface, (offset_x, offset_y))

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