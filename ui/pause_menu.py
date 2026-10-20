import pygame
from ui.button import Button
from settings import TEXT_COLOR

class PauseMenu:
    def __init__(self):
        self.buttons = {}

    def create_buttons(self, cx, cy, btn_w, btn_h, font):
        """Создает кнопки меню паузы"""
        self.buttons.clear()
        self.buttons['btn_resume'] = Button(cx - btn_w // 2, cy + 50, btn_w, btn_h, "RESUME", font)
        self.buttons['btn_quit_menu'] = Button(cx - btn_w // 2, cy + 120, btn_w, btn_h, "QUIT TO MENU", font)

    def draw(self, surface, sw, sh, font_large, font_small):
        """Отрисовывает затемнение, текст и кнопки"""
        # Затемнение фона
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Текст "PAUSED"
        pause_text = font_large.render("PAUSED", True, TEXT_COLOR)
        surface.blit(pause_text, (sw // 2 - pause_text.get_width() // 2, sh // 2 - 100))

        # Подсказка
        hint_text = font_small.render("Press ESC to resume", True, TEXT_COLOR)
        surface.blit(hint_text, (sw // 2 - hint_text.get_width() // 2, sh // 2 - 20))

        # Кнопки
        self.buttons['btn_resume'].draw(surface)
        self.buttons['btn_quit_menu'].draw(surface)

    def handle_event(self, event):
        """Проверяет клики по кнопкам и возвращает действие"""
        if self.buttons['btn_resume'].is_clicked(event):
            return 'resume'
        if self.buttons['btn_quit_menu'].is_clicked(event):
            return 'quit_to_menu'
        return None