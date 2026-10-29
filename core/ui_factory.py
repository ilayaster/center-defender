from ui import Button, DropdownButton, PauseMenu
from ui.slider import Slider
from core.constants import (STATE_MENU, STATE_DIFFICULTY, STATE_SETTINGS,
                            STATE_PLAYING, STATE_PAUSED, STATE_GAMEOVER,
                            STATE_WEAPON_SELECT, STATE_CORE_SELECT)


class UIFactory:
    @staticmethod
    def get_selection_layout(sw, sh):
        """
        Единая геометрия объединённого экрана выбора.
        Используется и здесь (для кнопок), и в Renderer (для текста/спрайта).
        """
        cx, cy = sw // 2, sh // 2

        # На небольших разрешениях слегка сжимаем горизонтальные отступы,
        # чтобы колонки не уезжали за край экрана.
        scale = max(0.6, min(1.0, sw / 1280.0))

        # Колонки разнесены дальше от центра
        weapon_x = cx - int(460 * scale)
        core_x = cx - int(160 * scale)
        desc_x = cx + int(200 * scale)

        # Блок выбора опущен вниз на 60px относительно центра
        sel_y = cy + 60

        # BACK / NEXT — отдельный ряд, значительно ниже остальных кнопок
        action_y = cy + 240

        # Ширина текстового блока с отступом от правого края
        desc_width = max(200, sw - desc_x - 40)

        return {
            'weapon_x': weapon_x,
            'core_x': core_x,
            'desc_x': desc_x,
            'sel_y': sel_y,
            'action_y': action_y,
            'desc_width': desc_width,
            'sprite_center_x': desc_x + desc_width // 2,
            # Спрайт и текст тоже опущены на те же 60px
            'sprite_center_y': sel_y - 30,
            'desc_y': sel_y + 30,
            'back_x': max(20, weapon_x - 20),
            'next_x': desc_x,
        }

    @staticmethod
    def create_main_menu(cx, cy, btn_w, btn_h, font_medium):
        return {
            'btn_start': Button(cx - btn_w // 2, cy - 60, btn_w, btn_h, "START GAME", font_medium),
            'btn_settings': Button(cx - btn_w // 2, cy + 10, btn_w, btn_h, "SETTINGS", font_medium),
            'btn_quit': Button(cx - btn_w // 2, cy + 80, btn_w, btn_h, "QUIT", font_medium)
        }

    @staticmethod
    def create_selection_screen(cx, cy, btn_w, btn_h, font_medium, sw, sh):
        lay = UIFactory.get_selection_layout(sw, sh)
        wx = lay['weapon_x']
        cxr = lay['core_x']
        sy = lay['sel_y']

        return {
            # Оружие — левая колонка, блок опущен вниз
            'btn_weapon_sword': Button(wx, sy - 80, 160, btn_h, "SWORD", font_medium),
            'btn_weapon_hammer': Button(wx, sy, 160, btn_h, "HAMMER", font_medium),
            'btn_weapon_pistol': Button(wx, sy + 80, 160, btn_h, "PISTOL", font_medium),

            # Ядра — правее оружия
            'btn_core_plosive': Button(cxr, sy - 50, 180, btn_h, "CORE-PLOSIVE", font_medium),
            'btn_core_slow': Button(cxr, sy + 10, 180, btn_h, "SLOW-CORE", font_medium),

            # Нижний ряд: BACK слева, NEXT справа
            'btn_sel_back': Button(lay['back_x'], lay['action_y'], 140, btn_h, "BACK", font_medium),
            'btn_next': Button(lay['next_x'], lay['action_y'], 140, btn_h, "NEXT", font_medium),
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
        mus_vol = game_settings.get('music_volume', 0.5)

        return {
            'dd_res': DropdownButton(cx - dd_w // 2, cy - 120, dd_w, dd_h,
                                     f"Resolution: {current_res_text}", res_options,
                                     font_small, sw, enabled=is_res_enabled, max_visible=6),
            'dd_display': DropdownButton(cx - dd_w // 2, cy - 60, dd_w, dd_h,
                                         f"Display: {game_settings['display_mode']}",
                                         ['Windowed', 'Fullscreen', 'Borderless'],
                                         font_small, sw),
            'dd_effects': DropdownButton(cx - dd_w // 2, cy, dd_w, dd_h,
                                         f"Effects: {current_eff}",
                                         ['OFF', 'RETRO', 'RETROIER'],
                                         font_small, sw),
            'slider_volume': Slider(cx - dd_w // 2, cy + 60, dd_w, 20, 0.0, 1.0, sfx_vol, font_small, "SFX Volume"),
            'slider_music_volume': Slider(cx - dd_w // 2, cy + 110, dd_w, 20, 0.0, 1.0, mus_vol, font_small, "Music Volume"),
            'btn_hitboxes': Button(cx - btn_w // 2, cy + 160, btn_w, btn_h, hb_text, font_small),
            'btn_reset': Button(cx - btn_w // 2, cy + 210, btn_w, btn_h, "RESET DEFAULTS", font_small),
            'btn_back': Button(cx - btn_w // 2, cy + 270, btn_w, btn_h, "BACK", font_medium)
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
        sh = game_settings.get('resolution', (sw, 720))[1]

        ui_elements = {}
        ui_elements.update(UIFactory.create_main_menu(cx, cy, btn_w, btn_h, font_medium))
        ui_elements.update(UIFactory.create_selection_screen(cx, cy, btn_w, btn_h, font_medium, sw, sh))
        ui_elements.update(UIFactory.create_difficulty_screen(cx, cy, btn_w, btn_h, font_medium))
        ui_elements.update(UIFactory.create_settings_screen(
            cx, cy, btn_w, btn_h, dd_w, dd_h, font_small, font_medium,
            available_resolutions, native_res, game_settings, sw
        ))
        ui_elements.update(UIFactory.create_gameover_screen(cx, cy, btn_w, btn_h, font_medium))
        pause_menu.create_buttons(cx, cy, btn_w, btn_h, font_medium)
        return ui_elements