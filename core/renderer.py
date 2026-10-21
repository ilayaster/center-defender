import pygame
import math
from settings import BG_COLOR, MENU_BG, TEXT_COLOR, CORE_COLOR, ENEMY_COLOR
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS, 
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER, STATE_WEAPON_SELECT)

class Renderer:
    """Отвечает за отрисовку всех экранов игры"""

    @staticmethod
    def draw_main_menu(screen, font_large, ui_elements, sw, sh):
        """Отрисовывает главное меню"""
        screen.fill(MENU_BG)
        title = font_large.render("DEFEND THE CORE", True, CORE_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 150))
        ui_elements['btn_start'].draw(screen)
        ui_elements['btn_settings'].draw(screen)
        ui_elements['btn_quit'].draw(screen)

    @staticmethod
    def draw_weapon_select_screen(screen, font_large, ui_elements, sw, sh):
        """Отрисовывает экран выбора оружия"""
        screen.fill(MENU_BG)
        title = font_large.render("SELECT WEAPON", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 120))
        ui_elements['btn_weapon_sword'].draw(screen)
        ui_elements['btn_weapon_hammer'].draw(screen)
        ui_elements['btn_weapon_pistol'].draw(screen)
        ui_elements['btn_wep_back'].draw(screen)

    @staticmethod
    def draw_difficulty_screen(screen, font_large, ui_elements, sw, sh):
        """Отрисовывает экран выбора сложности"""
        screen.fill(MENU_BG)
        title = font_large.render("SELECT DIFFICULTY", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 120))
        ui_elements['btn_easy'].draw(screen)
        ui_elements['btn_normal'].draw(screen)
        ui_elements['btn_hard'].draw(screen)
        ui_elements['btn_diff_back'].draw(screen)

    @staticmethod
    def draw_settings_screen(screen, font_large, ui_elements, sw, sh):
        """Отрисовывает экран настроек"""
        screen.fill(MENU_BG)
        title = font_large.render("SETTINGS", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 180))
        ui_elements['dd_res'].draw(screen)
        ui_elements['dd_display'].draw(screen)
        ui_elements['btn_hitboxes'].draw(screen)
        ui_elements['btn_reset'].draw(screen)
        ui_elements['btn_back'].draw(screen)

    @staticmethod
    def draw_playing(screen, font_small, ui_elements, core, enemies, 
                     show_hitboxes, time_left, score, sw, sh):
        """Отрисовывает игровой процесс"""
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        timer_text = font_small.render(f"TIME: {math.ceil(time_left)}", True, TEXT_COLOR)
        timer_rect = timer_text.get_rect(center=(sw // 2, core.rect.top - 15))
        screen.blit(timer_text, timer_rect)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
        score_text = font_small.render(f"SCORE: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (sw - score_text.get_width() - 20, 20))

    @staticmethod
    def draw_paused(screen, font_large, font_small, ui_elements, core, enemies, 
                    show_hitboxes, pause_menu, sw, sh):
        """Отрисовывает экран паузы"""
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
        pause_menu.draw(screen, sw, sh, font_large, font_small)

    @staticmethod
    def draw_gameover(screen, font_large, font_medium, ui_elements, core, enemies, 
                      show_hitboxes, game_won, score, sw, sh):
        """Отрисовывает экран конца игры"""
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        res_text = font_large.render("VICTORY!" if game_won else "DEFEAT", 
                                      True, CORE_COLOR if game_won else ENEMY_COLOR)
        screen.blit(res_text, (sw//2 - res_text.get_width()//2, sh//2 - 100))
        stats_text = font_medium.render(f"FINAL SCORE: {score}", True, TEXT_COLOR)
        screen.blit(stats_text, (sw//2 - stats_text.get_width()//2, sh//2 - 20))
        ui_elements['btn_retry'].draw(screen)
        ui_elements['btn_menu'].draw(screen)

    @classmethod
    def draw(cls, state, screen, font_small, font_medium, font_large, ui_elements,
             core, enemies, show_hitboxes, pause_menu, time_left, score, game_won, sw, sh):
        """Главный метод отрисовки, делегирует вызов нужному экрану"""
        if state == STATE_MENU:
            cls.draw_main_menu(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_WEAPON_SELECT:
            cls.draw_weapon_select_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_DIFFICULTY:
            cls.draw_difficulty_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_SETTINGS:
            cls.draw_settings_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_PLAYING:
            cls.draw_playing(screen, font_small, ui_elements, core, enemies,
                           show_hitboxes, time_left, score, sw, sh)
        elif state == STATE_PAUSED:
            cls.draw_paused(screen, font_large, font_small, ui_elements, core, enemies,
                          show_hitboxes, pause_menu, sw, sh)
        elif state == STATE_GAMEOVER:
            cls.draw_gameover(screen, font_large, font_medium, ui_elements, core, enemies,
                            show_hitboxes, game_won, score, sw, sh)