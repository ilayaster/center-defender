import pygame
import math
import os
from settings import BG_COLOR, MENU_BG, TEXT_COLOR, CORE_COLOR, ENEMY_COLOR
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS, 
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER, STATE_WEAPON_SELECT, STATE_CORE_SELECT)

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
    def draw_weapon_select_screen(screen, font_large, font_small, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT WEAPON", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 140))
        
        ui_elements['btn_weapon_sword'].draw(screen)
        ui_elements['btn_weapon_hammer'].draw(screen)
        ui_elements['btn_weapon_pistol'].draw(screen)
        ui_elements['btn_wep_back'].draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        desc = "Choose your primary method of defense."
        if ui_elements['btn_weapon_sword'].rect.collidepoint(mouse_pos):
            desc = "SWORD: Very fast attacks, short range. Best for precise, rapid cleanup of stray enemies."
        elif ui_elements['btn_weapon_hammer'].rect.collidepoint(mouse_pos):
            desc = "HAMMER: Slow wind-up, massive range and damage. Ideal for clearing dense groups."
        elif ui_elements['btn_weapon_pistol'].rect.collidepoint(mouse_pos):
            desc = "PISTOL: Ranged attacks with a magazine. Requires periodic reloading, but keeps you safe at a distance."

        desc_surf = font_small.render(desc, True, (200, 200, 200))
        screen.blit(desc_surf, (sw//2 - desc_surf.get_width()//2, sh//2 - 80))

    @staticmethod
    def draw_core_select_screen(screen, font_large, font_small, ui_elements, sw, sh, sprite_manager):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT CORE TYPE", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 140))
        
        ui_elements['btn_core_plosive'].draw(screen)
        ui_elements['btn_core_slow'].draw(screen)
        ui_elements['btn_core_back'].draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        is_hover_plosive = ui_elements['btn_core_plosive'].rect.collidepoint(mouse_pos)
        is_hover_slow = ui_elements['btn_core_slow'].rect.collidepoint(mouse_pos)
        
        desc = "Select a core to define your defensive strategy."
        sprite_name = None
        
        if is_hover_plosive:
            sprite_name = 'core-plosive'
            desc = "CORE-PLOSIVE: 5 HP. Explodes on contact, killing enemies in a massive radius. Regenerates 1 HP every 60s."
        elif is_hover_slow:
            sprite_name = 'slow-core'
            desc = "SLOW-CORE: 3 HP. Larger hitbox. Slows all enemies in a wide radius. Kills enemies on contact. Regenerates 1 HP every 80s."

        # РИСУЕМ ПРЕВЬЮ СПРАЙТА ПО ЦЕНТРУ (масштабированное в 3 раза)
        preview_sprite = None
        
        if sprite_name:
            if sprite_manager:
                preview_sprite = sprite_manager.get(sprite_name)
                
            if preview_sprite is None:
                sprite_path = f"sprites/{sprite_name}.png"
                if os.path.exists(sprite_path):
                    try:
                        preview_sprite = pygame.image.load(sprite_path).convert_alpha()
                    except pygame.error:
                        pass

        if preview_sprite:
            # Масштабируем в 3 раза с Nearest Neighbor
            original_width = preview_sprite.get_width()
            original_height = preview_sprite.get_height()
            scaled_sprite = pygame.transform.scale(
                preview_sprite, 
                (original_width * 3, original_height * 3)
            )
            
            sprite_rect = scaled_sprite.get_rect(center=(sw//2, sh//2 - 20))
            screen.blit(scaled_sprite, sprite_rect)

        # <-- ИЗМЕНЕНО: поднимаем описание НАД кнопками
        desc_surf = font_small.render(desc, True, (200, 200, 200))
        screen.blit(desc_surf, (sw//2 - desc_surf.get_width()//2, sh//2 + 40))

    @staticmethod
    def draw_difficulty_screen(screen, font_large, font_small, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT DIFFICULTY", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 140))
        
        ui_elements['btn_easy'].draw(screen)
        ui_elements['btn_normal'].draw(screen)
        ui_elements['btn_hard'].draw(screen)
        ui_elements['btn_diff_back'].draw(screen)

        mouse_pos = pygame.mouse.get_pos()
        desc = "Choose the intensity of the enemy waves."
        if ui_elements['btn_easy'].rect.collidepoint(mouse_pos):
            desc = "EASY: Relaxed pace. Fewer enemies, slower spawn rates. Good for learning the mechanics."
        elif ui_elements['btn_normal'].rect.collidepoint(mouse_pos):
            desc = "NORMAL: The intended experience. Balanced waves that steadily increase in pressure."
        elif ui_elements['btn_hard'].rect.collidepoint(mouse_pos):
            desc = "HARD: Relentless onslaught. Very fast spawns and high enemy speed. For masters only."

        desc_surf = font_small.render(desc, True, (200, 200, 200))
        screen.blit(desc_surf, (sw//2 - desc_surf.get_width()//2, sh//2 - 80))

    @staticmethod
    def draw_settings_screen(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SETTINGS", True, TEXT_COLOR)
        screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 260))
        ui_elements['dd_res'].draw(screen)
        ui_elements['dd_display'].draw(screen)
        ui_elements['dd_effects'].draw(screen)
        ui_elements['slider_volume'].draw(screen)
        ui_elements['slider_music_volume'].draw(screen)
        ui_elements['btn_hitboxes'].draw(screen)
        ui_elements['btn_reset'].draw(screen)
        ui_elements['btn_back'].draw(screen)

    @staticmethod
    def draw_core_hp(screen, core, font_small):
        """Рисует ХП прямо над ядром с ОЧЕВИДНОЙ индикацией регенерации"""
        cell_size = 24
        gap = 6
        total_width = core.max_hp * cell_size + (core.max_hp - 1) * gap
        start_x = int(core.x) - (total_width // 2)
        y = int(core.y) - core.hitbox_radius - 55
        
        if core.current_hp < core.max_hp:
            time_left = int(core.regen_time_per_hp - core.regen_timer) + 1
            regen_text = f"REGEN: {time_left}s"
            text_surf = font_small.render(regen_text, True, (255, 255, 100))
            screen.blit(text_surf, (int(core.x) - text_surf.get_width() // 2, y - 20))

        for i in range(core.max_hp):
            rect = pygame.Rect(start_x + i * (cell_size + gap), y, cell_size, cell_size)
            
            if i < core.current_hp:
                color = (50, 150, 255) if core.core_type == 'slow' else (255, 100, 50)
                pygame.draw.rect(screen, color, rect, border_radius=4)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=4)
            else:
                pygame.draw.rect(screen, (40, 40, 40), rect, border_radius=4)
                pygame.draw.rect(screen, (100, 100, 100), rect, 2, border_radius=4)
                
                if i == core.current_hp and core.current_hp < core.max_hp:
                    progress = core.regen_timer / core.regen_time_per_hp
                    fill_height = int(cell_size * progress)
                    if fill_height > 0:
                        fill_rect = pygame.Rect(rect.x, rect.y + cell_size - fill_height, cell_size, fill_height)
                        fill_color = (100, 255, 100) if core.core_type == 'slow' else (255, 200, 50)
                        pygame.draw.rect(screen, fill_color, fill_rect, border_radius=4)

    @staticmethod
    def draw_playing(screen, font_small, font_medium, ui_elements, core, enemies, 
                     show_hitboxes, time_survived, score, sw, sh, console_active, console_input):
        screen.fill(BG_COLOR)
        core.draw(screen, show_hitboxes)
        for enemy in enemies:
            enemy.draw(screen, show_hitboxes)
            
        Renderer.draw_core_hp(screen, core, font_small)
            
        mins = int(time_survived // 60)
        secs = int(time_survived % 60)
        time_str = f"TIME: {mins}:{secs:02d}"
        time_text = font_medium.render(time_str, True, TEXT_COLOR)
        screen.blit(time_text, (sw // 2 - time_text.get_width() // 2, 20))
        
        score_text = font_small.render(f"SCORE: {score}", True, TEXT_COLOR)
        screen.blit(score_text, (sw // 2 - score_text.get_width() // 2, 50))

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
             console_active=False, console_input="", sprite_manager=None):
        if state == STATE_MENU:
            cls.draw_main_menu(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_WEAPON_SELECT:
            cls.draw_weapon_select_screen(screen, font_large, font_small, ui_elements, sw, sh)
        elif state == STATE_CORE_SELECT:
            cls.draw_core_select_screen(screen, font_large, font_small, ui_elements, sw, sh, sprite_manager)
        elif state == STATE_DIFFICULTY:
            cls.draw_difficulty_screen(screen, font_large, font_small, ui_elements, sw, sh)
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