import pygame
import sys
import math
import os
from settings import *
from ui import Button, DropdownButton
from enemy import Enemy

def run():
    # --- CRITICAL: Center the window on the screen ---
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    
    info = pygame.display.Info()
    native_res = (info.current_w, info.current_h)
    
    raw_modes = pygame.display.list_modes()
    available_resolutions = []
    seen = set()
    
    if raw_modes != -1:
        for w, h in raw_modes:
            if w >= 800 and h >= 600 and (w, h) not in seen:
                available_resolutions.append((w, h))
                seen.add((w, h))
            if len(available_resolutions) >= 5:
                break
    
    if native_res in available_resolutions:
        available_resolutions.remove(native_res)
    available_resolutions.insert(0, native_res)

    initial_res = available_resolutions[0]
    
    screen = pygame.display.set_mode(initial_res, 0)
    pygame.display.set_caption("Defend the Core")
    clock = pygame.time.Clock()

    def get_fonts():
        sh = screen.get_height()
        size_small = max(16, min(22, sh // 45))
        size_medium = max(20, min(28, sh // 32))
        size_large = max(32, min(48, sh // 18))
        return (
            pygame.font.SysFont("arial", size_small, bold=True),
            pygame.font.SysFont("arial", size_medium, bold=True),
            pygame.font.SysFont("arial", size_large, bold=True)
        )

    font_small, font_medium, font_large = get_fonts()

    game_settings = {
        'difficulty': 'Normal',
        'resolution': initial_res,
        'display_mode': 'Borderless',
        'enemy_speed': 150,
        'spawn_interval': 1.0
    }

    STATE_MENU = 0
    STATE_SETTINGS = 1
    STATE_PLAYING = 2
    STATE_GAMEOVER = 3
    current_state = STATE_MENU

    enemies = []
    score = 0
    time_left = GAME_DURATION
    spawn_timer = 0
    game_won = False

    ui_elements = {}

    def create_ui():
        nonlocal ui_elements, font_small, font_medium
        ui_elements.clear() 
        
        sw, sh = screen.get_width(), screen.get_height()
        cx, cy = sw // 2, sh // 2
        
        btn_w, btn_h = 200, 45
        dd_w, dd_h = 240, 40
        
        ui_elements['btn_start'] = Button(cx - btn_w//2, cy - 60, btn_w, btn_h, "START GAME", font_medium)
        ui_elements['btn_settings'] = Button(cx - btn_w//2, cy + 10, btn_w, btn_h, "SETTINGS", font_medium)
        ui_elements['btn_quit'] = Button(cx - btn_w//2, cy + 80, btn_w, btn_h, "QUIT", font_medium)
        
        ui_elements['dd_diff'] = DropdownButton(
            cx - dd_w//2, cy - 80, dd_w, dd_h, 
            f"Difficulty: {game_settings['difficulty']}", 
            ['Easy', 'Normal', 'Hard'], 
            font_small, sw
        )
        
        res_options = [f"{w}x{h}" for w, h in available_resolutions]
        current_res_text = "Native" if game_settings['resolution'] == native_res else f"{game_settings['resolution'][0]}x{game_settings['resolution'][1]}"
        
        is_res_enabled = game_settings['display_mode'] != 'Borderless'
        ui_elements['dd_res'] = DropdownButton(
            cx - dd_w//2, cy - 20, dd_w, dd_h,
            f"Resolution: {current_res_text}",
            res_options,
            font_small, sw,
            enabled=is_res_enabled,
            max_visible=5 # Show max 5 resolutions at once
        )
        
        ui_elements['dd_display'] = DropdownButton(
            cx - dd_w//2, cy + 40, dd_w, dd_h,
            f"Display: {game_settings['display_mode']}",
            ['Windowed', 'Fullscreen', 'Borderless'],
            font_small, sw
        )
        
        ui_elements['btn_back'] = Button(cx - btn_w//2, cy + 120, btn_w, btn_h, "BACK", font_medium)
        
        ui_elements['btn_retry'] = Button(cx - btn_w//2, cy + 50, btn_w, btn_h, "RETRY", font_medium)
        ui_elements['btn_menu'] = Button(cx - btn_w//2, cy + 120, btn_w, btn_h, "MAIN MENU", font_medium)

    def apply_settings():
        nonlocal screen, font_small, font_medium, font_large
        w, h = game_settings['resolution']
        
        if game_settings['display_mode'] == 'Borderless':
            flags = pygame.NOFRAME
            w, h = native_res
            game_settings['resolution'] = native_res
        elif game_settings['display_mode'] == 'Fullscreen':
            flags = pygame.FULLSCREEN
        else:
            flags = 0 # Standard windowed mode with OS borders
            
        screen = pygame.display.set_mode((w, h), flags)
        pygame.display.set_caption("Defend the Core")
        
        # --- CRITICAL: Force SDL to process window changes immediately ---
        pygame.event.pump() 
        
        font_small, font_medium, font_large = get_fonts()
        create_ui()

    def reset_game():
        nonlocal enemies, score, time_left, spawn_timer, game_won, current_state
        enemies = []
        score = 0
        time_left = GAME_DURATION
        spawn_timer = 0
        game_won = False
        current_state = STATE_PLAYING

    def update_difficulty():
        if game_settings['difficulty'] == 'Easy':
            game_settings['enemy_speed'] = 100
            game_settings['spawn_interval'] = 1.5
        elif game_settings['difficulty'] == 'Normal':
            game_settings['enemy_speed'] = 150
            game_settings['spawn_interval'] = 1.0
        elif game_settings['difficulty'] == 'Hard':
            game_settings['enemy_speed'] = 220
            game_settings['spawn_interval'] = 0.5

    apply_settings()
    update_difficulty()

    while True:
        dt = clock.tick(FPS) / 1000.0
        sw, sh = screen.get_width(), screen.get_height()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_state == STATE_MENU:
                if ui_elements['btn_start'].is_clicked(event): reset_game()
                if ui_elements['btn_settings'].is_clicked(event): current_state = STATE_SETTINGS
                if ui_elements['btn_quit'].is_clicked(event): pygame.quit(); sys.exit()

            elif current_state == STATE_SETTINGS:
                # Close dropdowns if clicked outside of them
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for key, el in ui_elements.items():
                        if isinstance(el, DropdownButton):
                            visible_rects = el.get_visible_rects() if el.is_open else []
                            in_rect = el.rect.collidepoint(event.pos)
                            in_options = any(r.collidepoint(event.pos) for _, r, _ in visible_rects)
                            if not in_rect and not in_options:
                                el.is_open = False
                                el.scroll_offset = 0

                diff_val = ui_elements['dd_diff'].handle_event(event)
                if diff_val:
                    game_settings['difficulty'] = diff_val
                    update_difficulty()
                    ui_elements['dd_diff'].text = f"Difficulty: {diff_val}"
                    
                res_val = ui_elements['dd_res'].handle_event(event)
                if res_val:
                    w, h = map(int, res_val.split('x'))
                    game_settings['resolution'] = (w, h)
                    apply_settings()
                    
                disp_val = ui_elements['dd_display'].handle_event(event)
                if disp_val:
                    game_settings['display_mode'] = disp_val
                    apply_settings()

                if ui_elements['btn_back'].is_clicked(event): current_state = STATE_MENU

            elif current_state == STATE_PLAYING:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for enemy in enemies:
                        dist = math.hypot(mouse_pos[0] - enemy.x, mouse_pos[1] - enemy.y)
                        if dist < enemy.radius:
                            enemy.is_dead = True
                            score += 1
                            break

            elif current_state == STATE_GAMEOVER:
                if ui_elements['btn_retry'].is_clicked(event): reset_game()
                if ui_elements['btn_menu'].is_clicked(event): current_state = STATE_MENU

        if current_state == STATE_MENU:
            screen.fill(MENU_BG)
            title = font_large.render("DEFEND THE CORE", True, CORE_COLOR)
            screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 150))
            
            ui_elements['btn_start'].draw(screen)
            ui_elements['btn_settings'].draw(screen)
            ui_elements['btn_quit'].draw(screen)

        elif current_state == STATE_SETTINGS:
            screen.fill(MENU_BG)
            title = font_large.render("SETTINGS", True, TEXT_COLOR)
            screen.blit(title, (sw//2 - title.get_width()//2, sh//2 - 180))
            
            ui_elements['dd_diff'].draw(screen)
            ui_elements['dd_res'].draw(screen)
            ui_elements['dd_display'].draw(screen)
            ui_elements['btn_back'].draw(screen)

        elif current_state == STATE_PLAYING:
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                game_won = True
                current_state = STATE_GAMEOVER

            spawn_timer += dt
            if spawn_timer >= game_settings['spawn_interval']:
                enemies.append(Enemy(game_settings, sw, sh))
                spawn_timer = 0
                if game_settings['spawn_interval'] > 0.2:
                    game_settings['spawn_interval'] -= 0.02

            for enemy in enemies:
                if enemy.update(dt, sw, sh):
                    game_won = False
                    current_state = STATE_GAMEOVER

            enemies = [e for e in enemies if not e.is_dead]

            screen.fill(BG_COLOR)
            pygame.draw.circle(screen, CORE_COLOR, (sw // 2, sh // 2), CORE_RADIUS)
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), CORE_RADIUS, 3)
            for enemy in enemies:
                enemy.draw(screen)

            timer_text = font_small.render(f"Time: {math.ceil(time_left)}", True, TEXT_COLOR)
            score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(timer_text, (20, 20))
            screen.blit(score_text, (sw - 120, 20))

        elif current_state == STATE_GAMEOVER:
            screen.fill(BG_COLOR)
            pygame.draw.circle(screen, CORE_COLOR, (sw // 2, sh // 2), CORE_RADIUS)
            for enemy in enemies: 
                enemy.draw(screen)
            
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if game_won:
                res_text = font_large.render("VICTORY!", True, CORE_COLOR)
            else:
                res_text = font_large.render("DEFEAT", True, ENEMY_COLOR)
            
            stats_text = font_medium.render(f"Final Score: {score}", True, TEXT_COLOR)
            
            screen.blit(res_text, (sw//2 - res_text.get_width()//2, sh//2 - 100))
            screen.blit(stats_text, (sw//2 - stats_text.get_width()//2, sh//2 - 20))
            
            ui_elements['btn_retry'].draw(screen)
            ui_elements['btn_menu'].draw(screen)

        pygame.display.flip()