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
from core.weapons import WeaponManager # <-- НОВЫЙ ИМПОРТ

class Game:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.info = pygame.display.Info()
        self.native_res = (self.info.current_w, self.info.current_h)
        
        # Фильтрация доступных разрешений
        self.available_resolutions = []
        seen = set()
        for w, h in STANDARD_RESOLUTIONS:
            if w <= self.native_res[0] and h <= self.native_res[1] and (w, h) not in seen:
                self.available_resolutions.append((w, h))
                seen.add((w, h))
        if self.native_res not in seen:
            self.available_resolutions.append(self.native_res)
        self.available_resolutions.sort(key=lambda x: (x[0], x[1]))

        # Инициализация экрана
        self.screen = pygame.display.set_mode(self.native_res, pygame.RESIZABLE)
        pygame.display.set_caption("Defend the Core")
        self.clock = pygame.time.Clock()

        # Менеджеры
        self.sprite_manager = SpriteManager()
        self.asset_manager = AssetManager(self.sprite_manager, self.screen)
        self.pause_menu = PauseMenu()
        self.weapon_manager = WeaponManager() # <-- ИНИЦИАЛИЗАЦИЯ ОРУЖИЯ

        # Настройки
        self.game_settings = get_default_settings(self.native_res)

        # Состояние
        self.current_state = STATE_MENU

        # Игровые объекты
        self.core = None
        self.gameplay = None

        # UI
        self.ui_elements = {}

        # Загрузка и применение настроек
        self.apply_settings()

    def apply_settings(self):
        """Применяет настройки экрана и загружает ресурсы"""
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

        # Загрузка ресурсов
        self.asset_manager.load_all()

        # Создание ядра
        if self.core is None:
            self.core = Core(w, h, self.sprite_manager)
        else:
            self.core.update_size(w, h, self.sprite_manager)

        # Создание менеджера геймплея
        if self.gameplay is None:
            self.gameplay = GameplayManager(self.game_settings, self.core, self.sprite_manager)

        # Создание UI
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
        self.current_state = STATE_PLAYING

    def update_difficulty(self):
        """Обновляет параметры сложности"""
        self.gameplay.update_difficulty()

    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self.game_settings = get_default_settings(self.native_res)
        self.update_difficulty()
        self.apply_settings()

    def toggle_pause(self):
        """Переключает паузу"""
        if self.current_state == STATE_PLAYING:
            self.current_state = STATE_PAUSED
        elif self.current_state == STATE_PAUSED:
            self.current_state = STATE_PLAYING

    def handle_events(self):
        """Обрабатывает все события"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ESC для паузы
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_state in (STATE_PLAYING, STATE_PAUSED):
                    self.toggle_pause()

            # Главное меню
            if self.current_state == STATE_MENU:
                if self.ui_elements['btn_start'].is_clicked(event):
                    self.current_state = STATE_DIFFICULTY
                elif self.ui_elements['btn_settings'].is_clicked(event):
                    self.current_state = STATE_SETTINGS
                elif self.ui_elements['btn_quit'].is_clicked(event):
                    pygame.quit()
                    sys.exit()

            # Выбор сложности
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
                    self.current_state = STATE_MENU

            # Настройки
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

            # Игра
            elif self.current_state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    # <-- НОВАЯ ЛОГИКА АТАКИ ЧЕРЕЗ WEAPON MANAGER
                    hits = self.weapon_manager.attack(mouse_pos, self.gameplay.enemies)
                    if hits > 0:
                        self.gameplay.score += hits

            # Пауза
            elif self.current_state == STATE_PAUSED:
                action = self.pause_menu.handle_event(event)
                if action == 'resume':
                    self.toggle_pause()
                elif action == 'quit_to_menu':
                    self.current_state = STATE_MENU

            # Конец игры
            elif self.current_state == STATE_GAMEOVER:
                if self.ui_elements['btn_retry'].is_clicked(event):
                    self.reset_game()
                elif self.ui_elements['btn_menu'].is_clicked(event):
                    self.current_state = STATE_MENU

    def update(self, dt, sw, sh):
        """Обновляет игровую логику (только в состоянии PLAYING)"""
        if self.current_state == STATE_PLAYING:
            self.weapon_manager.update(dt) # <-- ОБНОВЛЕНИЕ ОРУЖИЯ
            if self.gameplay.update(dt, sw, sh):
                self.current_state = STATE_GAMEOVER

    def draw(self, sw, sh):
        """Отрисовывает текущее состояние"""
        Renderer.draw(
            self.current_state, self.screen,
            self.asset_manager.font_small, self.asset_manager.font_medium,
            self.asset_manager.font_large,
            self.ui_elements, self.core, self.gameplay.enemies,
            self.game_settings['show_hitboxes'], self.pause_menu,
            self.gameplay.time_left, self.gameplay.score, self.gameplay.game_won,
            sw, sh
        )
        
        # <-- ОТРИСОВКА ОРУЖИЯ/КУРСОРА ПОВЕРХ ВСЕГО (только в игре)
        if self.current_state == STATE_PLAYING:
            mouse_pos = pygame.mouse.get_pos()
            self.weapon_manager.draw(self.screen, mouse_pos)

    def run(self):
        """Главный игровой цикл"""
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