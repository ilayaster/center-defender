import pygame
import math
from settings import BG_COLOR, MENU_BG, TEXT_COLOR, CORE_COLOR, ENEMY_COLOR
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS, 
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER, STATE_WEAPON_SELECT)

class Renderer:
    @staticmethod
    def draw_main_menu(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("DEFEND THE CORE", True, CORE_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 150))
        ui_elements['btn_start'].draw(screen)
        ui_elements['btn_settings'].draw(screen)
        ui_elements['btn_quit'].draw(screen)

    @staticmethod
    def draw_weapon_select_screen(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT WEAPON", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 120))
        ui_elements['btn_weapon_sword'].draw(screen)
        ui_elements['btn_weapon_hammer'].draw(screen)
        ui_elements['btn_weapon_pistol'].draw(screen)
        ui_elements['btn_wep_back'].draw(screen)

    @staticmethod
    def draw_difficulty_screen(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT DIFFICULTY", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 120))
        ui_elements['btn_easy'].draw(screen)
        ui_elements['btn_normal'].draw(screen)
        ui_elements['btn_hard'].draw(screen)
        ui_elements['btn_diff_back'].draw(screen)

    @staticmethod
    def draw_settings_screen(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SETTINGS", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 220))
        ui_elements['dd_res'].draw(screen)
        ui_elements['dd_display'].draw(screen)
        ui_elements['dd_effects'].draw(screen)
        ui_elements['btn_hitboxes'].draw(screen)
        ui_elements['btn_reset'].draw(screen)
        ui_elements['btn_back'].draw(screen)

    @staticmethod
    def draw_playing(screen, font_small, font_medium, ui_elements, core, enemies, 
                     show_hitboxes, time_survived, score, sw, sh, console_active, console_input):
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
            
        mins = int(time_survived // 60)
        secs = int(time_survived % 60)
        time_str = f"TIME: {mins}:{secs:02d}"
        time_text = font_medium.render(time_str, True, TEXT_COLOR)
        screen.blit(time_text, (sw // 2 - time_text.get_width() // 2, 20))
        
        score_text = font_small.render(f"SCORE: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (sw // 2 - score_text.get_width() // 2, 55))

        if console_active:
            overlay = pygame.Surface((sw, 40), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, sh - 40))
            console_text = font_small.render(f"> {console_input}_", True, (0, 255, 0))
            screen.blit(console_text, (10, sh - 30))

    @staticmethod
    def draw_paused(screen, font_large, font_small, ui_elements, core, enemies, 
                    show_hitboxes, pause_menu, sw, sh):
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
        pause_menu.draw(screen, sw, sh, font_large, font_small)

    @staticmethod
    def draw_gameover(screen, font_large, font_medium, ui_elements, core, enemies, 
                      show_hitboxes, game_won, score, sw, sh):
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
             core, enemies, show_hitboxes, pause_menu, time_survived, score, game_won, sw, sh,
             console_active=False, console_input=""):
        if state == STATE_MENU:
            cls.draw_main_menu(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_WEAPON_SELECT:
            cls.draw_weapon_select_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_DIFFICULTY:
            cls.draw_difficulty_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_SETTINGS:
            cls.draw_settings_screen(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_PLAYING:
            cls.draw_playing(screen, font_small, font_medium, ui_elements, core, enemies,
                           show_hitboxes, time_survived, score, sw, sh, console_active, console_input)
        elif state == STATE_PAUSED:
            cls.draw_paused(screen, font_large, font_small, ui_elements, core, enemies,
                          show_hitboxes, pause_menu, sw, sh)
        elif state == STATE_GAMEOVER:
            cls.draw_gameover(screen, font_large, font_medium, ui_elements, core, enemies,
                            show_hitboxes, game_won, score, sw, sh)