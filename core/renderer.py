import pygame
import math
import os
from settings import BG_COLOR, MENU_BG, TEXT_COLOR, CORE_COLOR, ENEMY_COLOR
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS,
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
                            STATE_WEAPON_SELECT, STATE_CORE_SELECT)
from core.ui_factory import UIFactory


# ВАЖНО: имена файлов спрайтов не совпадают с ключами выбора.
# slow-core — это NOT "core-slow".
CORE_SPRITE_NAMES = {
    'plosive': 'core-plosive',
    'slow': 'slow-core',
}

WEAPON_DESCRIPTIONS = {
    'sword': "SWORD: Very fast attacks, short range. Best for precise, rapid cleanup of stray enemies.",
    'hammer': "HAMMER: Slow wind-up, massive range and damage. Ideal for clearing dense groups.",
    'pistol': "PISTOL: Ranged attacks with a magazine. Requires periodic reloading, but keeps you safe at a distance.",
}

CORE_DESCRIPTIONS = {
    'plosive': "CORE-PLOSIVE: 5 HP. Explodes on contact, killing enemies in a massive radius. Regenerates 1 HP every 60s.",
    'slow': "SLOW-CORE: 3 HP. Larger hitbox. Slows all enemies in a wide radius. Kills enemies on contact. Regenerates 1 HP every 80s.",
}


class Renderer:
    @staticmethod
    def _wrap_text(text, font, max_width):
        words = text.split(' ')
        lines, current = [], []
        for word in words:
            test = ' '.join(current + [word])
            if font.size(test)[0] <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(' '.join(current))
                current = [word]
        if current:
            lines.append(' '.join(current))
        return lines

    @staticmethod
    def _paint_button_state(screen, button, is_selected, has_selection):
        """Выбранная кнопка светлее, остальные — темнее."""
        button.draw(screen)
        if not has_selection:
            return

        rect = button.rect
        if is_selected:
            light = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            light.fill((255, 255, 255, 45))
            screen.blit(light, rect)
            pygame.draw.rect(screen, CORE_COLOR, rect, 2, border_radius=4)
        else:
            dark = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 150))
            screen.blit(dark, rect)

    @staticmethod
    def draw_main_menu(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("CORE DEFENSE", True, CORE_COLOR)
        screen.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 150))
        ui_elements['btn_start'].draw(screen)
        ui_elements['btn_settings'].draw(screen)
        ui_elements['btn_quit'].draw(screen)

    @staticmethod
    def draw_combined_select_screen(screen, font_large, font_small, ui_elements, sw, sh,
                                    sprite_manager, weapon_selected, core_selected):
        screen.fill(MENU_BG)

        lay = UIFactory.get_selection_layout(sw, sh)

        title = font_large.render("SELECT LOADOUT", True, TEXT_COLOR)
        screen.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 140))

        # --- Оружие: всегда видно ---
        for w in ['sword', 'hammer', 'pistol']:
            Renderer._paint_button_state(
                screen, ui_elements[f'btn_weapon_{w}'],
                weapon_selected == w, weapon_selected is not None
            )

        # --- Ядра: только после выбора оружия ---
        if weapon_selected is not None:
            for c in ['plosive', 'slow']:
                Renderer._paint_button_state(
                    screen, ui_elements[f'btn_core_{c}'],
                    core_selected == c, core_selected is not None
                )

        # --- Нижний ряд кнопок ---
        ui_elements['btn_sel_back'].draw(screen)
        if core_selected is not None:
            ui_elements['btn_next'].draw(screen)

        # --- Hover ---
        mouse_pos = pygame.mouse.get_pos()

        hover_core = None
        if weapon_selected is not None:
            for c in ['plosive', 'slow']:
                if ui_elements[f'btn_core_{c}'].rect.collidepoint(mouse_pos):
                    hover_core = c
                    break

        hover_weapon = None
        if hover_core is None:
            for w in ['sword', 'hammer', 'pistol']:
                if ui_elements[f'btn_weapon_{w}'].rect.collidepoint(mouse_pos):
                    hover_weapon = w
                    break

        # --- Приоритет: hover ядра > hover оружия > выбранное ядро > выбранное оружие ---
        desc = "Choose your weapon and core to define your playstyle."
        sprite_name = None

        if hover_core:
            desc = CORE_DESCRIPTIONS[hover_core]
            sprite_name = CORE_SPRITE_NAMES[hover_core]
        elif hover_weapon:
            desc = WEAPON_DESCRIPTIONS[hover_weapon]
        elif core_selected:
            desc = CORE_DESCRIPTIONS[core_selected]
            sprite_name = CORE_SPRITE_NAMES[core_selected]
        elif weapon_selected:
            desc = WEAPON_DESCRIPTIONS[weapon_selected]

        # --- Фиксированные координаты: текст никогда не прыгает ---
        desc_x = lay['desc_x']
        desc_y = lay['desc_y']
        desc_width = lay['desc_width']
        sprite_center_x = lay['sprite_center_x']
        sprite_center_y = lay['sprite_center_y']

        # --- Спрайт ядра (над описанием, в своей фиксированной зоне) ---
        if sprite_name:
            preview_sprite = None

            if sprite_manager:
                try:
                    preview_sprite = sprite_manager.get(sprite_name)
                except Exception:
                    preview_sprite = None

            if preview_sprite is None:
                sprite_path = f"sprites/{sprite_name}.png"
                if os.path.exists(sprite_path):
                    try:
                        preview_sprite = pygame.image.load(sprite_path).convert_alpha()
                    except pygame.error:
                        preview_sprite = None

            if preview_sprite:
                ow, oh = preview_sprite.get_size()
                tw, th = ow * 3, oh * 3

                # Не даём превью вылезти за текстовую колонку
                max_side = 180
                if max(tw, th) > max_side:
                    k = max_side / max(tw, th)
                    tw, th = max(1, int(tw * k)), max(1, int(th * k))

                scaled_sprite = pygame.transform.scale(preview_sprite, (tw, th))
                sprite_rect = scaled_sprite.get_rect(center=(sprite_center_x, sprite_center_y))
                screen.blit(scaled_sprite, sprite_rect)

        # --- Описание: та же позиция при любом состоянии ---
        lines = Renderer._wrap_text(desc, font_small, desc_width)
        for i, line in enumerate(lines):
            surf = font_small.render(line, True, (200, 200, 200))
            screen.blit(surf, (desc_x, desc_y + i * 30))

    @staticmethod
    def draw_difficulty_screen(screen, font_large, font_small, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SELECT DIFFICULTY", True, TEXT_COLOR)
        screen.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 140))

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
        screen.blit(desc_surf, (sw // 2 - desc_surf.get_width() // 2, sh // 2 - 80))

    @staticmethod
    def draw_settings_screen(screen, font_large, ui_elements, sw, sh):
        screen.fill(MENU_BG)
        title = font_large.render("SETTINGS", True, TEXT_COLOR)
        screen.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 260))
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
        cell_size = 24
        gap = 6
        total_width = core.max_hp * cell_size + (core.max_hp - 1) * gap
        start_x = int(core.x) - (total_width // 2)
        y = int(core.y) - core.hitbox_radius - 55

        is_slow = (core.name == 'SLOW')

        if core.current_hp < core.max_hp:
            time_left = int(core.regen_time_per_hp - core.regen_timer) + 1
            regen_text = f"REGEN: {time_left}s"
            text_surf = font_small.render(regen_text, True, (255, 255, 100))
            screen.blit(text_surf, (int(core.x) - text_surf.get_width() // 2, y - 20))

        for i in range(core.max_hp):
            rect = pygame.Rect(start_x + i * (cell_size + gap), y, cell_size, cell_size)

            if i < core.current_hp:
                color = (50, 150, 255) if is_slow else (255, 100, 50)
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
                        fill_color = (100, 255, 100) if is_slow else (255, 200, 50)
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
        screen.blit(res_text, (sw // 2 - res_text.get_width() // 2, sh // 2 - 100))
        stats_text = font_medium.render(f"FINAL SCORE: {score}", True, TEXT_COLOR)
        screen.blit(stats_text, (sw // 2 - stats_text.get_width() // 2, sh // 2 - 20))
        ui_elements['btn_retry'].draw(screen)
        ui_elements['btn_menu'].draw(screen)

    @classmethod
    def draw(cls, state, screen, font_small, font_medium, font_large, ui_elements,
             core, enemies, show_hitboxes, pause_menu, time_survived, score, game_won, sw, sh,
             console_active=False, console_input="", sprite_manager=None,
             weapon_selected=None, core_selected=None):
        if state == STATE_MENU:
            cls.draw_main_menu(screen, font_large, ui_elements, sw, sh)
        elif state == STATE_WEAPON_SELECT:
            cls.draw_combined_select_screen(screen, font_large, font_small, ui_elements, sw, sh,
                                            sprite_manager, weapon_selected, core_selected)
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