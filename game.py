import pygame
import sys
import math
import random

# --- COLORS ---
BG_COLOR = (30, 30, 30)
MENU_BG = (20, 20, 25)
CORE_COLOR = (76, 175, 80)
ENEMY_COLOR = (244, 67, 54)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (60, 60, 60)
BTN_HOVER = (100, 100, 100)
BTN_TEXT = (255, 255, 255)

FPS = 60

# --- UI BUTTON CLASS ---
class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = BTN_COLOR
        self.hover_color = BTN_HOVER

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, BTN_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# --- DROPDOWN BUTTON CLASS ---
class DropdownButton:
    def __init__(self, x, y, width, height, text, options, font, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.options = options
        self.font = font
        self.color = BTN_COLOR
        self.hover_color = BTN_HOVER
        self.disabled_color = (40, 40, 40)
        self.disabled_text_color = (100, 100, 100)
        self.enabled = enabled
        self.is_open = False
        
        # Pre-calculate rects for options
        self.option_rects = []
        for i, opt in enumerate(options):
            rect = pygame.Rect(x, y + height + i * height, width, height)
            self.option_rects.append((opt, rect))

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        
        # Determine colors based on enabled state
        if not self.enabled:
            current_color = self.disabled_color
            text_color = self.disabled_text_color
        else:
            current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
            text_color = BTN_TEXT
            
        # Draw main button
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 120, 120), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        text_rect.x -= 10 # Shift left to make room for arrow
        surface.blit(text_surf, text_rect)
        
        # Draw arrow indicator
        arrow_points = []
        if self.is_open:
            arrow_points = [(self.rect.right - 25, self.rect.centery + 5), 
                            (self.rect.right - 15, self.rect.centery + 5), 
                            (self.rect.right - 20, self.rect.centery - 5)]
        else:
            arrow_points = [(self.rect.right - 25, self.rect.centery - 5), 
                            (self.rect.right - 15, self.rect.centery - 5), 
                            (self.rect.right - 20, self.rect.centery + 5)]
        pygame.draw.polygon(surface, text_color, arrow_points)

        # Draw dropdown panel if open
        if self.is_open and self.enabled:
            total_h = len(self.options) * self.rect.height
            bg_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height, self.rect.width, total_h)
            pygame.draw.rect(surface, (40, 40, 45), bg_rect, border_radius=8)
            pygame.draw.rect(surface, (120, 120, 120), bg_rect, 2, border_radius=8)
            
            for opt_text, opt_rect in self.option_rects:
                opt_color = self.hover_color if opt_rect.collidepoint(mouse_pos) else (50, 50, 55)
                pygame.draw.rect(surface, opt_color, opt_rect, border_radius=4)
                opt_surf = self.font.render(opt_text, True, BTN_TEXT)
                opt_rect_text = opt_surf.get_rect(center=opt_rect.center)
                surface.blit(opt_surf, opt_rect_text)

    def handle_event(self, event):
        if not self.enabled:
            return None
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return None
            elif self.is_open:
                for opt_text, opt_rect in self.option_rects:
                    if opt_rect.collidepoint(mouse_pos):
                        self.is_open = False
                        return opt_text # Return selected value
                self.is_open = False # Clicked outside
                return None
        return None

# --- ENEMY CLASS ---
class Enemy:
    def __init__(self, settings, screen_w, screen_h):
        self.radius = 15
        self.speed = settings['enemy_speed']
        
        angle = random.uniform(0, 2 * math.pi)
        distance = max(screen_w, screen_h)
        self.x = (screen_w // 2) + math.cos(angle) * distance
        self.y = (screen_h // 2) + math.sin(angle) * distance
        self.is_dead = False

    def update(self, dt, screen_w, screen_h):
        center_x, center_y = screen_w // 2, screen_h // 2
        dx = center_x - self.x
        dy = center_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt

        if dist < 30 + self.radius:
            return True 
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, ENEMY_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)

# --- MAIN FUNCTION ---
def main():
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
    
    # Dynamic font sizing
    def get_fonts():
        sh = screen.get_height()
        size_small = max(20, sh // 35)
        size_medium = max(28, sh // 25)
        size_large = max(48, sh // 15)
        return (
            pygame.font.SysFont("arial", size_small, bold=True),
            pygame.font.SysFont("arial", size_medium, bold=True),
            pygame.font.SysFont("arial", size_large, bold=True)
        )

    # --- GAME SETTINGS ---
    game_settings = {
        'difficulty': 'Normal',
        'resolution': initial_res,
        'display_mode': 'Borderless',  # DEFAULT TO BORDERLESS
        'enemy_speed': 150,
        'spawn_interval': 1.0
    }

    # Game States
    STATE_MENU = 0
    STATE_SETTINGS = 1
    STATE_PLAYING = 2
    STATE_GAMEOVER = 3
    current_state = STATE_MENU

    # Gameplay variables
    enemies = []
    score = 0
    time_left = 30
    spawn_timer = 0
    game_won = False

    ui_elements = {}

    def create_ui():
        nonlocal ui_elements, font_small, font_medium
        sw, sh = screen.get_width(), screen.get_height()
        cx, cy = sw // 2, sh // 2
        
        # Menu Buttons
        ui_elements['btn_start'] = Button(cx - 100, cy - 60, 200, 50, "START GAME", font_medium)
        ui_elements['btn_settings'] = Button(cx - 100, cy + 10, 200, 50, "SETTINGS", font_medium)
        ui_elements['btn_quit'] = Button(cx - 100, cy + 80, 200, 50, "QUIT", font_medium)
        
        # Settings Dropdowns
        ui_elements['dd_diff'] = DropdownButton(
            cx - 120, cy - 80, 240, 40, 
            f"Difficulty: {game_settings['difficulty']}", 
            ['Easy', 'Normal', 'Hard'], 
            font_small
        )
        
        res_options = [f"{w}x{h}" for w, h in available_resolutions]
        current_res_text = "Native" if game_settings['resolution'] == native_res else f"{game_settings['resolution'][0]}x{game_settings['resolution'][1]}"
        
        # Disable resolution dropdown if Borderless is active
        is_res_enabled = game_settings['display_mode'] != 'Borderless'
        ui_elements['dd_res'] = DropdownButton(
            cx - 120, cy - 20, 240, 40,
            f"Resolution: {current_res_text}",
            res_options,
            font_small,
            enabled=is_res_enabled
        )
        
        ui_elements['dd_display'] = DropdownButton(
            cx - 120, cy + 40, 240, 40,
            f"Display: {game_settings['display_mode']}",
            ['Windowed', 'Fullscreen', 'Borderless'],
            font_small
        )
        
        ui_elements['btn_back'] = Button(cx - 100, cy + 120, 200, 50, "BACK", font_medium)

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
            flags = 0
            
        screen = pygame.display.set_mode((w, h), flags)
        pygame.display.set_caption("Defend the Core")
        
        font_small, font_medium, font_large = get_fonts()
        create_ui()

    def reset_game():
        nonlocal enemies, score, time_left, spawn_timer, game_won, current_state
        enemies = []
        score = 0
        time_left = 30
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

    # Initialize screen and UI
    # We need a dummy screen to get fonts, then apply_settings will set the real one
    screen = pygame.display.set_mode(initial_res, 0) 
    font_small, font_medium, font_large = get_fonts()
    apply_settings() # Applies Borderless and creates UI
    update_difficulty()

    clock = pygame.time.Clock()

    # --- MAIN LOOP ---
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
                            if not el.rect.collidepoint(event.pos) and not any(r.collidepoint(event.pos) for _, r in el.option_rects):
                                el.is_open = False

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

        # --- DRAWING ---
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
            pygame.draw.circle(screen, CORE_COLOR, (sw // 2, sh // 2), 30)
            pygame.draw.circle(screen, (255, 255, 255), (sw // 2, sh // 2), 30, 3)
            for enemy in enemies:
                enemy.draw(screen)

            timer_text = font_small.render(f"Time: {math.ceil(time_left)}", True, TEXT_COLOR)
            score_text = font_small.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(timer_text, (20, 20))
            screen.blit(score_text, (sw - 120, 20))

        elif current_state == STATE_GAMEOVER:
            screen.fill(BG_COLOR)
            pygame.draw.circle(screen, CORE_COLOR, (sw // 2, sh // 2), 30)
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

if __name__ == "__main__":
    main()