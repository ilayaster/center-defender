from ui import Button, DropdownButton, PauseMenu
from ui.slider import Slider
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS, 
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER, STATE_WEAPON_SELECT, STATE_CORE_SELECT)

class UIFactory:
    @staticmethod
    def create_main_menu(cx, cy, btn_w, btn_h, font_medium):
        return {
            'btn_start': Button(cx - btn_w // 2, cy - 60, btn_w, btn_h, "START GAME", font_medium),
            'btn_settings': Button(cx - btn_w // 2, cy + 10, btn_w, btn_h, "SETTINGS", font_medium),
            'btn_quit': Button(cx - btn_w // 2, cy + 80, btn_w, btn_h, "QUIT", font_medium)
        }

    @staticmethod
    def create_weapon_select_screen(cx, cy, btn_w, btn_h, font_medium):
        spacing = 30
        actual_btn_w = 160
        total_width = actual_btn_w * 3 + spacing * 2
        start_x = cx - total_width // 2
        return {
            'btn_weapon_sword': Button(start_x, cy - 30, actual_btn_w, btn_h, "SWORD", font_medium),
            'btn_weapon_hammer': Button(start_x + actual_btn_w + spacing, cy - 30, actual_btn_w, btn_h, "HAMMER", font_medium),
            'btn_weapon_pistol': Button(start_x + (actual_btn_w + spacing) * 2, cy - 30, actual_btn_w, btn_h, "PISTOL", font_medium),
            'btn_wep_back': Button(cx - btn_w // 2, cy + 60, btn_w, btn_h, "BACK", font_medium)
        }

    @staticmethod
    def create_core_select_screen(cx, cy, btn_w, btn_h, font_medium):
        spacing = 30
        actual_btn_w = 200
        total_width = actual_btn_w * 2 + spacing
        start_x = cx - total_width // 2
        return {
            'btn_core_plosive': Button(start_x, cy - 30, actual_btn_w, btn_h, "CORE-PLOSIVE", font_medium),
            'btn_core_slow': Button(start_x + actual_btn_w + spacing, cy - 30, actual_btn_w, btn_h, "SLOW-CORE", font_medium),
            'btn_core_back': Button(cx - btn_w // 2, cy + 60, btn_w, btn_h, "BACK", font_medium)
        }

    @staticmethod
    def create_difficulty_screen(cx, cy, btn_w, btn_h, font_medium):
        diff_btn_w = 150
        diff_spacing = 20
        total_width = diff_btn_w * 3 + diff_spacing * 2
        start_x = cx - total_width // 2
        return {
            'btn_easy': Button(start_x, cy - 30, diff_btn_w, btn_h, "EASY", font_medium),
            'btn_normal': Button(start_x + diff_btn_w + diff_spacing, cy - 30, diff_btn_w, btn_h, "NORMAL", font_medium),
            'btn_hard': Button(start_x + (diff_btn_w + diff_spacing) * 2, cy - 30, diff_btn_w, btn_h, "HARD", font_medium),
            'btn_diff_back': Button(cx - btn_w // 2, cy + 80, btn_w, btn_h, "BACK", font_medium)
        }

    @staticmethod
    def create_settings_screen(cx, cy, btn_w, btn_h, dd_w, dd_h, font_small, font_medium,
                               available_resolutions, native_res, game_settings, sw):
        res_options = [f"{w}x{h}" for w, h in available_resolutions]
        current_res_text = "Native" if game_settings['resolution'] == native_res else f"{game_settings['resolution'][0]}x{game_settings['resolution'][1]}"
        is_res_enabled = game_settings['display_mode'] != 'Borderless'
        hb_text = "Hitboxes: ON" if game_settings['show_hitboxes'] else "Hitboxes: OFF"
        current_eff = game_settings.get('effect_mode', 'OFF')
        sfx_vol = game_settings.get('sfx_volume', 0.5)
        
        return {
            'dd_res': DropdownButton(cx - dd_w // 2, cy - 100, dd_w, dd_h,
                                     f"Resolution: {current_res_text}", res_options,
                                     font_small, sw, enabled=is_res_enabled, max_visible=6),
            'dd_display': DropdownButton(cx - dd_w // 2, cy - 40, dd_w, dd_h,
                                         f"Display: {game_settings['display_mode']}",
                                         ['Windowed', 'Fullscreen', 'Borderless'],
                                         font_small, sw),
            'dd_effects': DropdownButton(cx - dd_w // 2, cy + 20, dd_w, dd_h,
                                         f"Effects: {current_eff}",
                                         ['OFF', 'RETRO', 'RETROIER'],
                                         font_small, sw),
            'slider_volume': Slider(cx - dd_w // 2, cy + 80, dd_w, 20, 0.0, 1.0, sfx_vol, font_small, "SFX Volume"),
            'btn_hitboxes': Button(cx - btn_w // 2, cy + 130, btn_w, btn_h, hb_text, font_small),
            'btn_reset': Button(cx - btn_w // 2, cy + 190, btn_w, btn_h, "RESET DEFAULTS", font_small),
            'btn_back': Button(cx - btn_w // 2, cy + 250, btn_w, btn_h, "BACK", font_medium)
        }

    @staticmethod
    def create_gameover_screen(cx, cy, btn_w, btn_h, font_medium):
        return {
            'btn_retry': Button(cx - btn_w // 2, cy + 50, btn_w, btn_h, "RETRY", font_medium),
            'btn_menu': Button(cx - btn_w // 2, cy + 120, btn_w, btn_h, "MAIN MENU", font_medium)
        }

    @staticmethod
    def create_all(cx, cy, btn_w, btn_h, dd_w, dd_h, font_small, font_medium,
                   available_resolutions, native_res, game_settings, sw, pause_menu):
        ui_elements = {}
        ui_elements.update(UIFactory.create_main_menu(cx, cy, btn_w, btn_h, font_medium))
        ui_elements.update(UIFactory.create_weapon_select_screen(cx, cy, btn_w, btn_h, font_medium))
        ui_elements.update(UIFactory.create_core_select_screen(cx, cy, btn_w, btn_h, font_medium))  # <-- ДОБАВЛЕНО
        ui_elements.update(UIFactory.create_difficulty_screen(cx, cy, btn_w, btn_h, font_medium))
        ui_elements.update(UIFactory.create_settings_screen(
            cx, cy, btn_w, btn_h, dd_w, dd_h, font_small, font_medium,
            available_resolutions, native_res, game_settings, sw
        ))
        ui_elements.update(UIFactory.create_gameover_screen(cx, cy, btn_w, btn_h, font_medium))
        pause_menu.create_buttons(cx, cy, btn_w, btn_h, font_medium)
        return ui_elements