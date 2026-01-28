import arcade
import random
import math
import sys
import os
from dungeons import *
from test_fight import *
from emitter_damage import *

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TITLE = "Игра с меню и спрайтами"
TILE_SIZE = 64
PLAYER_SPEED = 10
MONEY = 0
DUNGEON_MAP = {}
dun = None
LIST_POSESH = []
CARDS_LIST = cards_list()
CURRENT_COLODA = CurrentColoda()
if len(CARDS_LIST) < 15:
    start_coloda()
    init_current_coloda()
    CURRENT_COLODA = CurrentColoda()


class PauseScreenView(arcade.View):
    """Окно паузы с возможностью продолжения игры"""

    def __init__(self, game_view, background_texture=None):
        super().__init__()
        self.game_view = game_view  # Сохраняем ссылку на игровое окно

        # Получаем центр экрана
        center_x = self.window.width // 2
        center_y = self.window.height // 2

        # Кнопки - выровнены по центру и расположены вертикально
        self.continue_button = Button(
            x=center_x,
            y=center_y + 60,
            width=280,
            height=60,
            text="Продолжить",
            color=arcade.color.DARK_GREEN,
            hover_color=arcade.color.GREEN
        )

        self.restart_button = Button(
            x=center_x,
            y=center_y - 20,
            width=280,
            height=60,
            text="Начать заново",
            color=arcade.color.DARK_BLUE,
            hover_color=arcade.color.LIGHT_BLUE
        )

        self.menu_button = Button(
            x=center_x,
            y=center_y - 100,
            width=280,
            height=60,
            text="В главное меню",
            color=arcade.color.DARK_PINK,
            hover_color=arcade.color.PINK
        )

        self.quit_button = Button(
            x=center_x,
            y=center_y - 180,
            width=280,
            height=60,
            text="Выйти из игры",
            color=arcade.color.DARK_RED,
            hover_color=arcade.color.RED
        )

        # Анимационные переменные
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def on_show(self):
        """Вызывается при показе экрана паузы"""
        # Сбрасываем анимацию
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def on_draw(self):
        """Отрисовка экрана паузы"""
        self.clear()

        # Сначала рисуем игровое окно как фон
        if self.game_view:
            self.game_view.on_draw()

        # Затемняющий слой
        arcade.draw_rect_filled(
            arcade.rect.XYWH(
                self.window.width // 2,
                self.window.height // 2,
                self.window.width,
                self.window.height
            ),
            (0, 0, 0, int(self.fade_alpha * 150))  # Меньшая прозрачность, чем в экране смерти
        )

        # Большой заголовок ПАУЗА
        arcade.draw_text(
            "ПАУЗА",
            self.window.width // 2,
            self.window.height * 0.75,
            (255, 255, 0, int(self.text_alpha * 255)),  # Желтый цвет для паузы
            64,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Подсказка для продолжения
        arcade.draw_text(
            "Игра приостановлена",
            self.window.width // 2,
            self.window.height * 0.65,
            (255, 255, 255, int(self.text_alpha * 200)),
            24,
            anchor_x="center",
            anchor_y="center"
        )

        # Рисуем кнопки с учетом прозрачности
        if self.buttons_alpha > 0:
            # Полупрозрачные фоны для кнопок
            for button in [self.continue_button, self.restart_button, self.menu_button, self.quit_button]:
                button_rect = arcade.LRBT(
                    button.x - button.width // 2,
                    button.x + button.width // 2,
                    button.y - button.height // 2,
                    button.y + button.height // 2
                )

                # Фон кнопки с прозрачностью
                current_color = button.hover_color if button.is_hovered else button.color
                r, g, b = current_color[:3]
                arcade.draw_lrbt_rectangle_filled(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    (r, g, b, int(self.buttons_alpha * 255))
                )

                # Рамка кнопки
                border_color = arcade.color.BLACK
                if button.is_pressed:
                    border_color = arcade.color.RED
                arcade.draw_lrbt_rectangle_outline(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    border_color,
                    2
                )

                # Текст кнопки с прозрачностью
                button.text_obj.color = (
                    button.text_obj.color[0],
                    button.text_obj.color[1],
                    button.text_obj.color[2],
                    int(self.buttons_alpha * 255)
                )
                button.text_obj.draw()

    def on_update(self, delta_time):
        """Обновление анимации"""
        self.animation_timer += delta_time

        # Анимация затемнения
        if self.animation_timer > 0.1:
            self.fade_alpha = min(1.0, self.fade_alpha + delta_time * 4)

        # Анимация текста
        if self.animation_timer > 0.2:
            self.text_alpha = min(1.0, self.text_alpha + delta_time * 3)

        # Анимация кнопок
        if self.animation_timer > 0.3:
            self.buttons_alpha = min(1.0, self.buttons_alpha + delta_time * 4)

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        if self.buttons_alpha > 0:
            self.continue_button.check_hover(x, y)
            self.restart_button.check_hover(x, y)
            self.menu_button.check_hover(x, y)
            self.quit_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            self.continue_button.check_hover(x, y) and self.continue_button.on_press()
            self.restart_button.check_hover(x, y) and self.restart_button.on_press()
            self.menu_button.check_hover(x, y) and self.menu_button.on_press()
            self.quit_button.check_hover(x, y) and self.quit_button.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            if self.continue_button.is_pressed and self.continue_button.check_hover(x, y):
                self.continue_button.on_release()
                self.continue_game()

            if self.restart_button.is_pressed and self.restart_button.check_hover(x, y):
                self.restart_button.on_release()
                self.restart_game()

            if self.menu_button.is_pressed and self.menu_button.check_hover(x, y):
                self.menu_button.on_release()
                self.return_to_menu()

            if self.quit_button.is_pressed and self.quit_button.check_hover(x, y):
                self.quit_button.on_release()
                self.quit_game()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        # ESC для продолжения игры
        if key == arcade.key.ESCAPE:
            self.continue_game()

        # P также для продолжения (альтернативная клавиша)
        elif key == arcade.key.P:
            self.continue_game()

    def continue_game(self):
        """Продолжить игру"""
        print("Продолжение игры...")
        self.window.show_view(self.game_view)

    def restart_game(self):
        """Перезапуск игры"""
        """print("Перезапуск игры...")
        # Создаем новую игру с теми же параметрами
        x, y = self.game_view.player.x, self.game_view.player_sprite.center_y
        element = self.game_view.element
        level = self.game_view.level
        game_view = GameView(x, y, element, level)
        self.window.show_view(game_view)"""
        pass

    def return_to_menu(self):
        global LIST_POSESH
        """Возврат в главное меню"""
        print("Возврат в главное меню...")
        LIST_POSESH = []
        try:
            background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
            menu_view = MenuView(background_texture)
        except:
            menu_view = MenuView()
        self.window.show_view(menu_view)

    def quit_game(self):
        """Выход из игры"""
        print("Выход из игры...")
        arcade.close_window()


class DeathScreenView(arcade.View):
    """Окно смерти с случайными фразами"""

    def __init__(self, element, level, background_texture=None):
        global LIST_POSESH
        super().__init__()
        self.background_texture = background_texture
        self.death_phrases = []
        self.current_phrase = ""
        self.load_death_phrases()
        self.select_random_phrase()
        self.element = element
        self.level = level

        LIST_POSESH = []

        # Получаем центр экрана
        center_x = 400
        center_y = 300

        # Кнопки - выровнены по центру и расположены вертикально
        self.restart_button = Button(
            x=center_x + 140,  # Центр по горизонтали
            y=center_y - 30 -60,  # Немного выше центра
            width=280,
            height=60,
            text="Начать заново",
            color=arcade.color.DARK_GREEN,
            hover_color=arcade.color.GREEN
        )

        self.menu_button = Button(
            x=center_x + 140,  # Центр по горизонтали
            y=center_y - 110-60,  # Ниже кнопки рестарта
            width=280,
            height=60,
            text="В главное меню",
            color=arcade.color.DARK_BLUE,
            hover_color=arcade.color.LIGHT_BLUE
        )

        self.quit_button = Button(
            x=center_x + 140,  # Центр по горизонтали
            y=center_y - 190-60,  # Ниже кнопки меню
            width=280,
            height=60,
            text="Выйти из игры",
            color=arcade.color.DARK_RED,
            hover_color=arcade.color.RED
        )

        # Анимационные переменные
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def load_death_phrases(self):
        """Загружает фразы из файла"""
        try:
            file_path = "most_frequent_screen.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                # Разделяем фразы по разделителю */
                sections = content.split('*/')
                all_phrases = []

                for section in sections:
                    # Убираем пустые строки и добавляем непустые фразы
                    lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
                    all_phrases.extend(lines)

                self.death_phrases = all_phrases
                print(f"Загружено {len(self.death_phrases)} фраз смерти")
            else:
                # Фразы по умолчанию, если файл не найден
                self.death_phrases = [
                    "Поражение! Ваше приключение подошло к концу...",
                    "Вы пали в бою, но ваша слава живет в легендах.",
                    "Даже самые смелые герои иногда проигрывают...",
                    "В следующий раз удача будет на вашей стороне!",
                    "Ваше путешествие окончено, но память о вас останется."
                ]
                print("Файл most_frequent_screen.txt не найден. Используются фразы по умолчанию.")

        except Exception as e:
            print(f"Ошибка загрузки фраз смерти: {e}")
            self.death_phrases = ["Произошла ошибка при загрузке сообщения..."]

    def select_random_phrase(self):
        """Выбирает случайную фразу"""
        if self.death_phrases:
            self.current_phrase = random.choice(self.death_phrases)
        else:
            self.current_phrase = "Поражение!"

    def on_show(self):
        """Вызывается при показе экрана смерти"""
        arcade.set_background_color(arcade.color.BLACK)
        # Сбрасываем анимацию
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def on_draw(self):
        """Отрисовка экрана смерти"""
        self.clear()

        # Рисуем фон (если есть текстура)
        if self.background_texture:
            background_rect = arcade.rect.XYWH(
                self.window.width // 2,
                self.window.height // 2,
                self.window.width,
                self.window.height
            )
            arcade.draw_texture_rect(self.background_texture, background_rect)

        # Затемняющий слой
        arcade.draw_rect_filled(arcade.rect.XYWH(
            self.window.width // 2,
            self.window.height // 2,
            self.window.width,
            self.window.height),
            (0, 0, 0, int(self.fade_alpha * 180))
        )

        # Большой заголовок ПОРАЖЕНИЕ
        arcade.draw_text(
            "ПОРАЖЕНИЕ",
            self.window.width // 2,
            self.window.height * 0.7,
            (255, 0, 0, int(self.text_alpha * 255)),
            64,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Выбранная фраза
        if self.current_phrase:
            # Разбиваем длинную фразу на строки
            words = self.current_phrase.split()
            lines = []
            current_line = ""

            for word in words:
                if len(current_line + " " + word) <= 40:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            # Рисуем каждую строку
            line_height = 40
            start_y = self.window.height * 0.55

            for i, line in enumerate(lines):
                arcade.draw_text(
                    line.strip(),
                    self.window.width // 2,
                    start_y - i * line_height,
                    (255, 255, 255, int(self.text_alpha * 255)),
                    28,
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )

        # Рисуем кнопки с учетом прозрачности
        if self.buttons_alpha > 0:
            # Полупрозрачные фоны для кнопок
            for button in [self.restart_button, self.menu_button, self.quit_button]:
                button_rect = arcade.LRBT(
                    button.x - button.width // 2,
                    button.x + button.width // 2,
                    button.y - button.height // 2,
                    button.y + button.height // 2
                )

                # Фон кнопки с прозрачностью
                current_color = button.hover_color if button.is_hovered else button.color
                r, g, b = current_color[:3]
                arcade.draw_lrbt_rectangle_filled(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    (r, g, b, int(self.buttons_alpha * 255))
                )

                # Рамка кнопки
                border_color = arcade.color.BLACK
                if button.is_pressed:
                    border_color = arcade.color.RED
                arcade.draw_lrbt_rectangle_outline(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    border_color,
                    2
                )

                # Текст кнопки с прозрачностью
                button.text_obj.color = (
                    button.text_obj.color[0],
                    button.text_obj.color[1],
                    button.text_obj.color[2],
                    int(self.buttons_alpha * 255)
                )
                button.text_obj.draw()

            # Подсказка (над кнопками)
            arcade.draw_text(
                "Выберите дальнейшее действие",
                self.window.width // 2,
                self.window.height * 0.4,
                (200, 200, 200, int(self.buttons_alpha * 200)),
                20,
                anchor_x="center",
                anchor_y="center"
            )

    def on_update(self, delta_time):
        """Обновление анимации"""
        self.animation_timer += delta_time

        # Анимация затемнения
        if self.animation_timer > 0.5:
            self.fade_alpha = min(1.0, self.fade_alpha + delta_time * 2)

        # Анимация текста
        if self.animation_timer > 1.0:
            self.text_alpha = min(1.0, self.text_alpha + delta_time)

        # Анимация кнопок
        if self.animation_timer > 2.0:
            self.buttons_alpha = min(1.0, self.buttons_alpha + delta_time * 2)

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        if self.buttons_alpha > 0:
            self.restart_button.check_hover(x, y)
            self.menu_button.check_hover(x, y)
            self.quit_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            if self.restart_button.check_hover(x, y):
                self.restart_button.on_press()
            if self.menu_button.check_hover(x, y):
                self.menu_button.on_press()
            if self.quit_button.check_hover(x, y):
                self.quit_button.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            if self.restart_button.is_pressed and self.restart_button.check_hover(x, y):
                self.restart_button.on_release()
                self.restart_game()

            if self.menu_button.is_pressed and self.menu_button.check_hover(x, y):
                self.menu_button.on_release()
                self.return_to_menu()

            if self.quit_button.is_pressed and self.quit_button.check_hover(x, y):
                self.quit_button.on_release()
                self.quit_game()

    def restart_game(self):
        """Перезапуск игры"""
        print("Перезапуск игры...")
        # Создаем новую игру
        x, y = DUNGEON_MAP['player_start']
        game_view = GameView(x, y, self.element, self.level)
        self.window.show_view(game_view)

    def return_to_menu(self):
        """Возврат в главное меню"""
        print("Возврат в главное меню...")
        try:
            background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
            menu_view = MenuView(background_texture)
        except:
            menu_view = MenuView()
        self.window.show_view(menu_view)

    def quit_game(self):
        """Выход из игры"""
        print("Выход из игры...")
        arcade.close_window()


class WinScreenView(arcade.View):
    """Окно победы"""

    def __init__(self, x, y, element, level, room, background_texture=None):
        global MONEY, CARDS_LIST
        super().__init__()
        self.background_texture = background_texture
        self.element = element
        self.level = level
        self.coords = (x, y)
        self.room = room
        self.new_card = None
        if self.level == 'первый':
            self.reward = random.randrange(14, 31)
        elif self.level == "второй":
            self.reward = random.randrange(24, 51)
        elif self.level == 'третий':
            self.reward = random.randrange(40, 71)
        if self.room == '_':
            self.reward = int(self.reward * (random.randrange(15, 25) * 0.1))
            if ((random.randrange(1, 101) <= 10 and self.level in ['первый', 'второй'])
                or (random.randrange(1, 101) <= 20 and self.level == 'третий')):
                self.new_card = get_new_card()
                self.new_card = " ".join(self.new_card['name'].split('/'))
                CARDS_LIST = cards_list()
        MONEY += self.reward


        # Кнопка для перехода в магазин
        self.shop_button = Button(
            x=self.window.width // 2,
            y=50,
            width=280,
            height=60,
            text="Далее",
            color=arcade.color.GOLD,
            hover_color=arcade.color.YELLOW
        )

        # Анимационные переменные
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def on_show(self):
        """Вызывается при показе экрана победы"""
        arcade.set_background_color(arcade.color.BLACK)
        # Сбрасываем анимацию
        self.fade_alpha = 0
        self.text_alpha = 0
        self.buttons_alpha = 0
        self.animation_timer = 0

    def on_draw(self):
        """Отрисовка экрана победы"""
        self.clear()

        # Рисуем фон (если есть текстура)
        if self.background_texture:
            background_rect = arcade.rect.XYWH(
                self.window.width // 2,
                self.window.height // 2,
                self.window.width,
                self.window.height
            )
            arcade.draw_texture_rect(self.background_texture, background_rect)

        # Затемняющий слой
        arcade.draw_rect_filled(arcade.rect.XYWH(
            self.window.width // 2,
            self.window.height // 2,
            self.window.width,
            self.window.height),
            (0, 0, 0, int(self.fade_alpha * 180))
        )

        # Большой заголовок ПОБЕДА
        arcade.draw_text(
            "ПОБЕДА",
            self.window.width // 2,
            self.window.height * 0.7,
            (0, 255, 0, int(self.text_alpha * 255)),  # Зеленый цвет для победы
            64,
            anchor_x="center",
            anchor_y="center",
            bold=True)

        arcade.draw_text(
            'Ты одержал победу в бою!',
            self.window.width // 2,
            400,
            (255, 255, 255, int(self.text_alpha * 255)),
            28,
            anchor_x="center",
            anchor_y="center",
            bold=True)

        arcade.draw_text(
            f'Награда: {self.reward} золота!',
            self.window.width // 2,
            350,
            (255, 215, 0, int(self.text_alpha * 255)),  # Золотой цвет
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True)

        # Рисуем кнопки с учетом прозрачности
        if self.buttons_alpha > 0:
            # Полупрозрачные фоны для кнопок
            for button in [self.shop_button]:
                button_rect = arcade.LRBT(
                    button.x - button.width // 2,
                    button.x + button.width // 2,
                    button.y - button.height // 2,
                    button.y + button.height // 2
                )

                # Фон кнопки с прозрачностью
                current_color = button.hover_color if button.is_hovered else button.color
                r, g, b = current_color[:3]
                arcade.draw_lrbt_rectangle_filled(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    (r, g, b, int(self.buttons_alpha * 255))
                )

                # Рамка кнопки
                border_color = arcade.color.BLACK
                if button.is_pressed:
                    border_color = arcade.color.RED
                arcade.draw_lrbt_rectangle_outline(
                    button_rect.left,
                    button_rect.right,
                    button_rect.bottom,
                    button_rect.top,
                    border_color,
                    2
                )

                # Текст кнопки с прозрачностью
                button.text_obj.color = (
                    button.text_obj.color[0],
                    button.text_obj.color[1],
                    button.text_obj.color[2],
                    int(self.buttons_alpha * 255)
                )
                button.text_obj.draw()

            # Подсказка
            arcade.draw_text(
                "После боя вы будете перенаправлены в магазин",
                self.window.width // 2,
                self.window.height * 0.4,
                (200, 200, 200, int(self.buttons_alpha * 200)),
                20,
                anchor_x="center",
                anchor_y="center"
            )

            if self.new_card is not None:
                arcade.draw_text(
                    f"Получена новая карта: {self.new_card}!",
                    self.window.width // 2,
                    self.window.height * 0.35,
                    (31, 163, 40),
                    24,
                    anchor_x="center",
                    anchor_y="center"
                )

    def on_update(self, delta_time):
        """Обновление анимации"""
        self.animation_timer += delta_time

        # Анимация затемнения
        if self.animation_timer > 0.5:
            self.fade_alpha = min(1.0, self.fade_alpha + delta_time * 2)

        # Анимация текста
        if self.animation_timer > 1.0:
            self.text_alpha = min(1.0, self.text_alpha + delta_time)

        # Анимация кнопок
        if self.animation_timer > 2.0:
            self.buttons_alpha = min(1.0, self.buttons_alpha + delta_time * 2)

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        if self.buttons_alpha > 0:
            self.shop_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            if self.shop_button.check_hover(x, y):
                self.shop_button.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        global LIST_POSESH
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT and self.buttons_alpha > 0:
            if self.shop_button.is_pressed and self.shop_button.check_hover(x, y):
                self.shop_button.on_release()
                if not (self.level == 'третий' and self.room == '_'):
                    self.go_to_shop()
                else:
                    LIST_POSESH = []
                    background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
                    menu_view = MenuView(background_texture)
                    self.window.show_view(menu_view)

    def go_to_shop(self):
        """Переход в магазин для выбора карт"""
        print("Переход в магазин...")
        shop_screen = ShopScreenView(self.coords[0], self.coords[1], self.element, self.level, self.room)
        self.window.show_view(shop_screen)


class ShopScreenView(arcade.View):
    """Экран магазина для выбора карт"""

    def __init__(self, x, y, element, level, room):
        super().__init__()
        self.coords = (x, y)
        self.element = element
        self.level = level
        self.room = room
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768
        self.all_cards = []
        self.selected_cards = []
        self.shop_cards = []
        self.buy_button = None
        self.skip_button = None
        self.selected_count = 0
        self.max_selection = 1
        self.setup()

    def setup(self):
        """Настройка магазина"""
        # Загружаем карты из БД (заглушка)
        self.load_cards_from_db()

        # Отбираем 5 случайных карт для магазина
        self.shop_cards = self.get_random_shop_cards(5)

        # Создаем кнопки
        self.buy_button = Button(
            x=self.SCREEN_WIDTH // 2,
            y=150,
            width=200,
            height=50,
            text=f"Купить",
            color=arcade.color.DARK_GREEN,
            hover_color=arcade.color.GREEN
        )

        self.skip_button = Button(
            x=self.SCREEN_WIDTH // 2,
            y=70,
            width=200,
            height=50,
            text="В подземелье",
            color=arcade.color.DARK_GRAY,
            hover_color=arcade.color.LIGHT_GRAY
        )

        # Создаем объекты для отображения карт в магазине
        self.create_shop_card_objects()

    def load_cards_from_db(self):
        self.all_cards = [None] * 50
        for i in range(50):
            self.all_cards[i] = create_card(i + 1)

    def get_random_shop_cards(self, count):
        """Выбирает случайные карты для магазина"""
        if count > len(self.all_cards):
            count = len(self.all_cards)
        selected_cards = []
        for i in range(count):
            select = random.sample(self.all_cards, 1)[0]
            """while select in CURRENT_COLODA:
                 select = random.sample(self.all_cards, 1)[0]"""
            selected_cards.append(select)
        return selected_cards

    def create_shop_card_objects(self):
        """Создает объекты для отображения карт в магазине"""
        # Очищаем предыдущие объекты
        self.shop_card_objects = []

        # Параметры отображения карт
        card_width = 150
        card_height = 200
        card_spacing = 30

        # Количество карт в магазине (5)
        cards_count = len(self.shop_cards)

        # Вычисляем начальную позицию
        total_width = cards_count * card_width + (cards_count - 1) * card_spacing
        start_x = self.SCREEN_WIDTH // 2 - total_width // 2 + card_width // 2
        start_y = self.SCREEN_HEIGHT // 2 + 50

        # Создаем объекты для каждой карты в магазине
        for i, card_data in enumerate(self.shop_cards):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = start_y

            # Определяем цвет в зависимости от типа карты
            color_map = [arcade.color.LIGHT_SALMON,
                arcade.color.BLUE,
                arcade.color.LIGHT_GREEN,
                arcade.color.LIGHT_GRAY,
                arcade.color.LIGHT_PINK]

            print(card_data)

            color = color_map[(card_data['id'] - 1) // 10]

            # Создаем объект карты для магазина
            shop_card = ShopCard(
                x=card_x,
                y=card_y,
                width=card_width,
                height=card_height,
                card_data=card_data,
                color=color,
                hover_color=arcade.color.WHITE,
                is_selected=card_data in self.selected_cards
            )

            self.shop_card_objects.append(shop_card)

    def on_draw(self):
        """Отрисовка магазина"""
        self.clear()

        # Фон
        arcade.draw_lrbt_rectangle_filled(
            0, self.SCREEN_WIDTH,
            0, self.SCREEN_HEIGHT,
            arcade.color.DARK_SLATE_GRAY
        )

        # Заголовок
        arcade.draw_text(
            "МАГАЗИН",
            self.SCREEN_WIDTH // 2,
            self.SCREEN_HEIGHT - 50,
            arcade.color.GOLD,
            48,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"Золото: {MONEY}",
            self.SCREEN_WIDTH // 2 + 300,
            self.SCREEN_HEIGHT - 50,
            arcade.color.GOLD,
            32,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Инструкция
        arcade.draw_text(
            "Выберите карты, которые хотите добавить в колоду",
            self.SCREEN_WIDTH // 2,
            self.SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            20,
            anchor_x="center",
            anchor_y="center"
        )

        # Рисуем карты в магазине
        for shop_card in self.shop_card_objects:
            shop_card.draw()

        # Рисуем кнопки
        if self.buy_button:
            self.buy_button.draw()
            if self.selected_count == 0:
                self.buy_button.color = arcade.color.DARK_GRAY
                self.buy_button.hover_color = arcade.color.GRAY
            else:
                self.buy_button.color = arcade.color.DARK_GREEN
                self.buy_button.hover_color = arcade.color.GREEN

        if self.skip_button:
            self.skip_button.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for shop_card in self.shop_card_objects:
            shop_card.check_hover(x, y)

        if self.buy_button:
            self.buy_button.check_hover(x, y)

        if self.skip_button:
            self.skip_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Проверяем нажатие на карты
            for shop_card in self.shop_card_objects:
                if shop_card.check_hover(x, y):
                    self.toggle_card_selection(shop_card)

            # Проверяем нажатие на кнопки
            if self.buy_button and self.buy_button.check_hover(x, y) and self.selected_count > 0:
                self.buy_button.on_press()

            if self.skip_button and self.skip_button.check_hover(x, y):
                self.skip_button.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.buy_button and self.buy_button.is_pressed and self.buy_button.check_hover(x, y) and self.selected_count > 0:
                self.buy_button.on_release()
                self.buy_card()

            if self.skip_button and self.skip_button.is_pressed and self.skip_button.check_hover(x, y):
                self.skip_button.on_release()
                self.return_to_game()

    def toggle_card_selection(self, shop_card):
        if shop_card in self.selected_cards:
            self.selected_cards = []
            shop_card.is_selected = False
        else:
            self.selected_cards = [shop_card]
            for i in self.shop_card_objects:
                i.is_selected = False
            shop_card.is_selected = True
        self.update_buttons()

    def update_buttons(self):
        if self.buy_button:
            self.selected_count = len(self.selected_cards)
            if self.selected_count == 0:
                self.buy_button.color = arcade.color.DARK_GRAY
                self.buy_button.hover_color = arcade.color.GRAY
            else:
                self.buy_button.color = arcade.color.DARK_GREEN
                self.buy_button.hover_color = arcade.color.GREEN

    def buy_card(self):
        global CURRENT_COLODA, MONEY
        card = self.selected_cards[0].card_data['id']
        if MONEY - self.selected_cards[0].card_data['mana'] * 2 >= 0:
            MONEY -= self.selected_cards[0].card_data['mana'] * 2
            card_cl = create_card(card)
            CURRENT_COLODA.append(card_cl)
            self.shop_card_objects.remove(self.selected_cards[0])
            self.selected_cards = []
            self.selected_count = 0

    def return_to_game(self):
        """Возврат в основную игру"""
        global DUNGEON_MAP
        global LIST_POSESH
        global dun

        # Возвращаемся в основную игру
        print(f"Возврат в игру после магазина")

        if self.room != '_':
            x, y = self.coords
            game_view = GameView(x, y, self.element, self.level)
            self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.window.show_view(game_view)
        else:
            LIST_POSESH = []
            dung = random_dun()
            a = ['первый', 'второй', 'третий']
            b = a.index(self.level) + 1
            if b == 3:
                pass
            else:
                self.level = a[b]
                dun = dung['dungeon']
                DUNGEON_MAP = {
                    "name": dung['name'],
                    "world_width": TILE_SIZE * 250,
                    "world_height": TILE_SIZE * 250,
                    "player_start": [TILE_SIZE * dung['start'][0], TILE_SIZE * dung['start'][1]],
                    "squares": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '*'],
                    "gorizontal": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '#'],
                    "vertical": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '$'],
                    "walls_1": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '1'],
                    "walls_2": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '2'],
                    "walls_3": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '3'],
                    "walls_4": [
                        [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                        in range(len(dun[y])) if dun[y][x] == '4']
                }
                x, y = DUNGEON_MAP['player_start']
                game_view = GameView(x, y, self.element, self.level)
                self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.window.show_view(game_view)


class ShopCard:
    """Класс для представления карты в магазине"""

    def __init__(self, x, y, width, height, card_data, color, hover_color, is_selected=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.card_data = card_data
        self.color = color
        self.hover_color = hover_color
        self.is_selected = is_selected
        self.is_hovered = False
        self.is_allowed = True

        # Определяем тип карты для отображения
        card_type = card_data.get('type', 'Особый')

        self.text_obj = []
        for p, t in enumerate(self.card_data['name'].split('/')):
            self.text_obj.append(arcade.Text(
                t,
                self.x,
                520 - 14 * p,
                arcade.color.BLACK,
                15,
                anchor_x="center",
                anchor_y="center",
                bold=True
            ))

        # Создаем текстовый объект для описания
        self.desc = []
        for p, i in enumerate(self.card_data['description'].split('/')):
            self.desc.append(arcade.Text(
                i, self.x - 70,
                   470 - p * 12,
                arcade.color.BLACK, 10,
                   width * 0.8
            ))

        self.mana_text = arcade.Text(
            f"Мана: {card_data['mana']}",
            x, y - height // 2 + 45,
            arcade.color.BLACK,
            12,
            anchor_x="center",
            anchor_y="center"
        )

        self.selected_indicator = arcade.Text(
            "✓",
            x + width // 2 - 15,
            y + height // 2 - 15,
            arcade.color.GREEN,
            20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def check_hover(self, x, y):
        """Проверяет, находится ли курсор над картой"""
        left = self.x - self.width // 2
        right = self.x + self.width // 2
        bottom = self.y - self.height // 2
        top = self.y + self.height // 2

        self.is_hovered = (left <= x <= right and bottom <= y <= top)
        return self.is_hovered

    def draw(self):
        """Отрисовывает карту"""
        # Основной прямоугольник карты
        current_color = self.hover_color if self.is_hovered else self.color

        # Если карта выбрана, делаем ее ярче
        if self.is_selected:
            # Увеличиваем яркость выбранной карты
            r, g, b = current_color[:3]
            current_color = (
                min(255, r + 50),
                min(255, g + 50),
                min(255, b + 50)
            )

        arcade.draw_rect_filled(arcade.rect.XYWH(
            self.x, self.y,
            self.width, self.height),
            current_color
        )

        arcade.draw_text(f"Цена: {self.card_data['mana'] * 2}",
                         self.x, self.y - 80,
                         arcade.color.BLACK, 16,
                         anchor_x="center", anchor_y="center")

        # Рамка карты
        border_color = arcade.color.BLACK
        border_width = 2

        # Если карта выбрана, меняем цвет рамки
        if self.is_selected:
            border_color = arcade.color.GOLD
            border_width = 4

        arcade.draw_rect_outline(arcade.rect.XYWH(
            self.x, self.y,
            self.width, self.height),
            border_color,
            border_width
        )

        # Текстовые элементы
        self.mana_text.draw()
        for i in self.desc:
            i.draw()
        for i in self.text_obj:
            i.draw()
        if self.is_selected:
            self.selected_indicator.draw()


class DeckBuilderView(arcade.View):
    def __init__(self, background_texture=None):
        super().__init__()
        self.background_texture = background_texture
        self.all_cards = []  # Все карты по стихиям
        self.selected_cards = []  # Список выбранных карт (id)
        self.current_page = 0  # Текущая страница (стихия)
        self.total_pages = 7  # 7 стихий
        self.card_buttons = []  # Кнопки карт на текущей странице
        self.setup()

        # Загружаем все карты по стихиям
        self.load_all_cards_by_elements()
        # Загружаем текущую колоду
        self.load_current_coloda()
        # Создаем кнопки для текущей страницы
        self.create_card_buttons_for_page()

    def setup(self):
        """Настройка интерфейса"""
        # Кнопка подтверждения
        self.confirm_button = Button(
            x=self.window.width // 2,
            y=80,
            width=320,
            height=60,
            text="Подтвердить колоду",
            color=arcade.color.DARK_GRAY,
            hover_color=arcade.color.GRAY,
            font_size=20
        )

        # Кнопка отмены
        self.cancel_button = Button(
            x=self.window.width // 2 - 300,
            y=80,
            width=180,
            height=50,
            text="Отмена",
            color=arcade.color.DARK_RED,
            hover_color=arcade.color.RED,
            font_size=18
        )

        # Кнопка очистки
        self.clear_button = Button(
            x=self.window.width // 2 + 300,
            y=80,
            width=180,
            height=50,
            text="Очистить все",
            color=arcade.color.DARK_ORANGE,
            hover_color=arcade.color.ORANGE,
            font_size=18
        )

        # Кнопки переключения страниц
        self.prev_page_button = Button(
            x=100,
            y=self.window.height - 75,
            width=120,
            height=50,
            text="← Назад",
            color=arcade.color.DARK_GRAY,
            hover_color=arcade.color.GRAY,
            font_size=16
        )

        self.next_page_button = Button(
            x=self.window.width - 100,
            y=self.window.height - 75,
            width=120,
            height=50,
            text="Вперед →",
            color=arcade.color.DARK_GRAY,
            hover_color=arcade.color.GRAY,
            font_size=16
        )

        # Информация о карте
        self.card_info_text = ""
        self.selected_card_details = None

    def load_all_cards_by_elements(self):
        """Загрузить все карты, сгруппированные по стихиям"""
        try:
            from cards_test_1 import get_cards_by_element, get_element_name

            self.all_cards = []
            for i in range(7):  # 7 стихий
                element_name = get_element_name(i)
                element_cards = get_cards_by_element(element_name)
                self.all_cards.append(element_cards)

            print(f"Загружено {sum(len(cards) for cards in self.all_cards)} карт по {len(self.all_cards)} стихиям")

        except Exception as e:
            print(f"Ошибка загрузки карт по стихиям: {e}")
            self.all_cards = []

    def load_current_coloda(self):
        """Загрузить текущую колоду"""
        try:
            from cards_test_1 import CurrentColoda
            current_cards = CurrentColoda()
            self.selected_cards = [card['id'] for card in current_cards]
            self.update_confirm_button()
        except Exception as e:
            print(f"Ошибка загрузки текущей колоды: {e}")
            self.selected_cards = []

    def create_card_buttons_for_page(self):
        """Создать кнопки для карт на текущей странице (стихии)"""
        self.card_buttons = []

        if self.current_page >= len(self.all_cards):
            return

        current_element_cards = self.all_cards[self.current_page]

        # Параметры отображения - 2 ряда по 5 карт
        card_width = 150
        card_height = 80
        margin_x = 15
        margin_y = 20
        cards_per_row = 5
        rows = 2  # 2 ряда по 5 карт = 10 карт на страницу

        # Начальные координаты
        total_width = cards_per_row * card_width + (cards_per_row - 1) * margin_x
        start_x = self.window.width // 2 - total_width // 2 + card_width // 2
        start_y = self.window.height - 200  # Ниже заголовка

        card_index = 0

        for row in range(rows):
            current_y = start_y - row * (card_height + margin_y)

            for col in range(cards_per_row):
                if card_index < len(current_element_cards):
                    card = current_element_cards[card_index]

                    current_x = start_x + col * (card_width + margin_x)

                    # Проверяем, выбрана ли карта
                    is_selected = card['id'] in self.selected_cards

                    # Создаем кнопку карты
                    card_button = CardButton(
                        x=current_x,
                        y=current_y,
                        width=card_width,
                        height=card_height,
                        card_data=card,
                        is_selected=is_selected
                    )

                    self.card_buttons.append(card_button)
                    card_index += 1

    def get_current_element_name(self):
        """Получить название текущей стихии"""
        try:
            from cards_test_1 import get_element_display_name
            return get_element_display_name(self.current_page)
        except:
            element_names = ['ОГОНЬ', 'ВОДА', 'КАМЕНЬ', 'ВЕТЕР', 'МОЛНИЯ', 'СВЕТ', "ТЬМА"]
            return element_names[self.current_page] if self.current_page < len(element_names) else 'НЕИЗВЕСТНО'

    def update_confirm_button(self):
        """Обновить текст кнопки подтверждения"""
        count = len(self.selected_cards)
        max_cards = 15  # Увеличили лимит до 15

        if count == max_cards:
            self.confirm_button.text = f"Подтвердить колоду ({count}/{max_cards})"
            self.confirm_button.color = arcade.color.DARK_GREEN
            self.confirm_button.hover_color = arcade.color.GREEN
        elif count > max_cards:
            self.confirm_button.text = f"Слишком много карт! ({count}/{max_cards})"
            self.confirm_button.color = arcade.color.DARK_RED
            self.confirm_button.hover_color = arcade.color.RED
        else:
            self.confirm_button.text = f"Подтвердить колоду ({count}/{max_cards})"
            self.confirm_button.color = arcade.color.DARK_GRAY
            self.confirm_button.hover_color = arcade.color.GRAY

    def toggle_card_selection(self, card_id):
        if card_id in self.selected_cards:
            self.selected_cards.remove(card_id)
            self.selected_card_details = None
        else:
            if len(self.selected_cards) < 15:
                if self.card_buttons[card_id - 10 *((card_id - 1) // 10) - 1].is_opened:
                    self.selected_cards.append(card_id)

        # Обновляем состояние кнопок
        for card_button in self.card_buttons:
            card_button.is_selected = card_button.card_data['id'] in self.selected_cards

        self.update_confirm_button()

    def confirm_deck(self):
        global CURRENT_COLODA
        """Подтвердить выбранную колоду"""
        if len(self.selected_cards) != 15:
            return False

        try:
            from cards_test_1 import update_current_coloda
            update_current_coloda(self.selected_cards)
            CURRENT_COLODA = CurrentColoda()
            return True
        except Exception as e:
            print(f"Ошибка обновления колоды: {e}")
            return False

    def clear_selection(self):
        """Очистить все выбранные карты"""
        self.selected_cards = []
        self.selected_card_details = None

        # Обновляем состояние кнопок
        for card_button in self.card_buttons:
            card_button.is_selected = False

        self.update_confirm_button()

    def change_page(self, direction):
        """Сменить страницу (стихию)"""
        if direction == 'next':
            self.current_page = (self.current_page + 1) % self.total_pages
        elif direction == 'prev':
            self.current_page = (self.current_page - 1) % self.total_pages

        # Создаем новые кнопки для новой страницы
        self.create_card_buttons_for_page()
        self.selected_card_details = None

    def on_draw(self):
        """Отрисовка экрана редактора колоды"""
        self.clear()

        # Черный фон
        arcade.draw_rect_filled(arcade.rect.XYWH(
            self.window.width // 2,
            self.window.height // 2,
            self.window.width,
            self.window.height),
            arcade.color.BLACK
        )

        # Заголовок с названием текущей стихии
        current_element = self.get_current_element_name()
        arcade.draw_text(
            f"РЕДАКТОР КОЛОДЫ - {current_element}",
            self.window.width // 2,
            self.window.height - 50,
            arcade.color.GOLD,
            36,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"Выберите 15 карт для вашей колоды (страница {self.current_page + 1}/{self.total_pages})",
            self.window.width // 2,
            self.window.height - 90,
            arcade.color.LIGHT_GRAY,
            18,
            anchor_x="center",
            anchor_y="center"
        )

        # Текущий статус
        count = len(self.selected_cards)
        max_cards = 15
        if count == max_cards:
            status_color = arcade.color.GREEN
        elif count > max_cards:
            status_color = arcade.color.RED
        else:
            status_color = arcade.color.YELLOW

        arcade.draw_text(
            f"Выбрано карт: {count}/{max_cards}",
            self.window.width // 2,
            self.window.height - 120,
            status_color,
            20,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Разделительная линия
        arcade.draw_line(
            10,
            self.window.height - 150,
            self.window.width - 10,
            self.window.height - 150,
            arcade.color.GRAY,
            2
        )

        # Рисуем кнопки карт (10 карт текущей стихии)
        for card_button in self.card_buttons:
            card_button.draw()

        # Панель информации о выбранной карте
        if self.selected_card_details:
            self.draw_card_info_panel()

        # Рисуем кнопки управления
        self.confirm_button.draw()
        self.cancel_button.draw()
        self.clear_button.draw()
        self.prev_page_button.draw()
        self.next_page_button.draw()

    def draw_card_info_panel(self):
        """Отрисовка панели с информацией о выбранной карте"""
        if not self.selected_card_details:
            return

        card = self.selected_card_details

        # Панель информации
        panel_width = 300
        panel_height = 200
        panel_x = self.window.width // 2
        panel_y = 300

        # Фон панели
        arcade.draw_rect_filled(arcade.rect.XYWH(
            panel_x,
            panel_y,
            panel_width,
            panel_height),
            (50, 50, 50, 220)
        )

        # Рамка панели
        arcade.draw_rect_outline(arcade.rect.XYWH(
            panel_x,
            panel_y,
            panel_width,
            panel_height),
            arcade.color.GOLD,
            3
        )

        # Информация о карте
        arcade.draw_text(
            ' '.join(card['name'].split('/')),
            panel_x,
            panel_y + 80,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"Мана: {card['mana']}",
            panel_x,
            panel_y + 50,
            arcade.color.LIGHT_BLUE,
            16,
            anchor_x="center",
            anchor_y="center"
        )

        # Описание карты
        for i, line in enumerate(card['description'].split('/')):
            arcade.draw_text(
                line.strip(),
                panel_x,
                panel_y + 24 - i * 20,
                arcade.color.LIGHT_GRAY,
                16,
                anchor_x="center",
                anchor_y="center",
                width=panel_width - 40
            )

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        # Проверяем кнопки карт
        for card_button in self.card_buttons:
            card_button.check_hover(x, y)

        # Проверяем другие кнопки
        self.confirm_button.check_hover(x, y)
        self.cancel_button.check_hover(x, y)
        self.clear_button.check_hover(x, y)
        self.prev_page_button.check_hover(x, y)
        self.next_page_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            # Проверяем кнопки карт
            for card_button in self.card_buttons:
                if card_button.check_hover(x, y):
                    self.toggle_card_selection(card_button.card_data['id'])

            # Проверяем другие кнопки
            if self.confirm_button.check_hover(x, y) and len(self.selected_cards) == 15:
                self.confirm_button.on_press()
            if self.cancel_button.check_hover(x, y):
                self.cancel_button.on_press()
            if self.clear_button.check_hover(x, y):
                self.clear_button.on_press()
            if self.prev_page_button.check_hover(x, y):
                self.prev_page_button.on_press()
            if self.next_page_button.check_hover(x, y):
                self.next_page_button.on_press()

        if button == arcade.MOUSE_BUTTON_RIGHT:
            for card_button in self.card_buttons:
                if card_button.check_hover(x, y):
                    # Показываем информацию о выбранной карте
                    for element_cards in self.all_cards:
                        for card in element_cards:
                            if card['id'] == card_button.card_data['id']:
                                self.selected_card_details = card
                                break

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.confirm_button.is_pressed and self.confirm_button.check_hover(x, y):
                self.confirm_button.on_release()
                if self.confirm_deck():
                    self.return_to_menu()

            if self.cancel_button.is_pressed and self.cancel_button.check_hover(x, y):
                self.cancel_button.on_release()
                self.return_to_menu()

            if self.clear_button.is_pressed and self.clear_button.check_hover(x, y):
                self.clear_button.on_release()
                self.clear_selection()

            if self.prev_page_button.is_pressed and self.prev_page_button.check_hover(x, y):
                self.prev_page_button.on_release()
                self.change_page('prev')

            if self.next_page_button.is_pressed and self.next_page_button.check_hover(x, y):
                self.next_page_button.on_release()
                self.change_page('next')

    def return_to_menu(self):
        """Возврат в главное меню"""
        try:
            background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
            menu_view = MenuView(background_texture)
        except:
            menu_view = MenuView()
        self.window.show_view(menu_view)


class CardButton:
    """Кнопка карты в редакторе колоды"""

    def __init__(self, x, y, width, height, card_data, is_selected=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.card_data = card_data
        self.is_selected = is_selected
        self.is_hovered = False
        if card_data['id'] in [i['id'] for i in CARDS_LIST]:
            self.is_opened = True
        else:
            self.is_opened = False

        element_colors = {
            0: arcade.color.LIGHT_SALMON,
            1: arcade.color.BLUE,
            2: arcade.color.LIGHT_GREEN,
            3: arcade.color.LIGHT_GRAY,
            4: arcade.color.ELECTRIC_PURPLE,
            5: (230, 226, 122),
            6: (92, 58, 126)
        }

        block_colors = {
            0: (145, 115, 115),
            1: (115, 124, 145),
            2: (105, 140, 106),
            3: (112, 112, 112),
            4: (131, 112, 137),
            5: (173, 169, 138),
            6: (99, 86, 113)
        }

        element_index = (card_data['id'] - 1) // 10
        self.color = element_colors.get(element_index, arcade.color.DARK_BLUE_GRAY)
        self.hover_color = arcade.color.WHITE
        self.selected_color = arcade.color.GOLD
        self.blocked_color = block_colors.get(element_index, arcade.color.GRAY)

        self.name_text = []
        for p, t in enumerate(card_data['name'].split('/')):
            self.name_text.append(arcade.Text(
                t,
                self.x,
                y + 30 - 14 * p,
                arcade.color.BLACK,
                12,
                anchor_x="center",
                anchor_y="center",
                bold=True
            ))

        self.mana_text = arcade.Text(
            f"Мана: {card_data['mana']}",
            x,
            y,
            arcade.color.BLACK,
            12,
            anchor_x="center",
            anchor_y="center"
        )

    def check_hover(self, x, y):
        """Проверяет, находится ли курсор над кнопкой"""
        left = self.x - self.width // 2
        right = self.x + self.width // 2
        bottom = self.y - self.height // 2
        top = self.y + self.height // 2

        self.is_hovered = (left <= x <= right and bottom <= y <= top)
        return self.is_hovered

    def draw(self):
        """Отрисовывает кнопку карты"""
        # Основной цвет
        if not self.is_opened:
            current_color = self.blocked_color
        elif self.is_selected:
            current_color = self.selected_color
        elif self.is_hovered:
            current_color = self.hover_color
        else:
            current_color = self.color

        # Рисуем прямоугольник с закругленными углами (эмулируем)
        arcade.draw_rect_filled(arcade.rect.XYWH(
            self.x,
            self.y,
            self.width,
            self.height),
            current_color
        )

        # Рисуем рамку
        border_color = arcade.color.BLACK
        border_width = 2
        if self.is_selected:
            border_color = arcade.color.RED
            border_width = 3
        elif self.is_hovered:
            border_color = arcade.color.GOLD
            border_width = 2

        arcade.draw_rect_outline(arcade.rect.XYWH(
            self.x,
            self.y,
            self.width,
            self.height),
            border_color,
            border_width
        )

        # Рисуем ID карты в левом нижнем углу
        arcade.draw_text(
            f"ID: {self.card_data['id']}",
            self.x - self.width // 2 + 5,
            self.y - self.height // 2 + 10,
            arcade.color.BLACK,
            10,
            anchor_x="left",
            anchor_y="center"
        )

        # Рисуем тексты
        for i in self.name_text:
            i.draw()
        self.mana_text.draw()

        # Если карта выбрана, рисуем индикатор
        if self.is_selected:
            arcade.draw_text(
                "✓",
                self.x + self.width // 2 - 15,
                self.y - self.height // 2 + 15,
                arcade.color.GREEN,
                16,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )


# --- Классы для меню ---
class Button:
    """Класс для представления кнопки"""

    def __init__(self, x, y, width, height, text,
                 color=arcade.color.GRAY,
                 hover_color=arcade.color.LIGHT_GRAY,
                 text_color=arcade.color.BLACK,
                 font_size=20,
                 bold=True):
        self.rect = arcade.LRBT(
            x - width // 2,
            x + width // 2,
            y - height // 2,
            y + height // 2
        )
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.bold = bold

        # Создаем текстовый объект
        self.text_obj = arcade.Text(
            text,
            self.x,
            self.y,
            text_color,
            font_size,
            anchor_x="center",
            anchor_y="center",
            bold=bold
        )

        self.is_hovered = False
        self.is_pressed = False

    def check_hover(self, x, y):
        """Проверяет, находится ли курсор над кнопкой"""
        self.is_hovered = (
                self.rect.left <= x <= self.rect.right and
                self.rect.bottom <= y <= self.rect.top
        )
        return self.is_hovered

    def draw(self):
        """Отрисовывает кнопку"""
        # Рисуем прямоугольник кнопки
        current_color = self.hover_color if self.is_hovered else self.color
        arcade.draw_lrbt_rectangle_filled(
            self.rect.left,
            self.rect.right,
            self.rect.bottom,
            self.rect.top,
            current_color
        )

        # Рисуем рамку кнопки
        border_color = arcade.color.BLACK
        if self.is_pressed:
            border_color = arcade.color.RED
        arcade.draw_lrbt_rectangle_outline(
            self.rect.left,
            self.rect.right,
            self.rect.bottom,
            self.rect.top,
            border_color,
            2
        )

        # Рисуем текст
        self.text_obj.draw()

    def on_press(self):
        """Вызывается при нажатии кнопки"""
        self.is_pressed = True

    def on_release(self):
        """Вызывается при отпускании кнопки"""
        self.is_pressed = False


# --- Классы для игры ---
class Player(arcade.Sprite):
    """Класс игрока как спрайта"""

    def __init__(self):
        super().__init__()
        self.width = TILE_SIZE * 1.2  # 120% от размера тайла
        self.height = TILE_SIZE * 1.2  # 120% от размера тайла

        self.flip = 0

        # Создаем текстуру для игрока
        try:
            self.texture = arcade.load_texture("images/Texture2D/mag_1.png")
            self.scale = 0.35
        except:
            # Используем стандартный синий квадрат
            self.texture = arcade.make_soft_square_texture(
                int(self.width),
                arcade.color.BLUE,
                outer_alpha=255
            )

        # Устанавливаем текстуру спрайту
        self.textures = [self.texture]
        self.set_texture(0)

        # Для квадратного спрайта хитбокс создается автоматически
        # по размерам текстуры, но мы можем явно задать его
        half_width = self.width / 2
        half_height = self.height / 2

        # Создаем хитбокс с помощью метода из arcade
        # Используем прямоугольный хитбокс
        self.hit_box = arcade.hitbox.HitBox(
            [
                (-half_width, -half_height),  # Нижний левый
                (half_width, -half_height),  # Нижний правый
                (half_width, half_height),  # Верхний правый
                (-half_width, half_height)  # Верхний левый
            ]
        )

        # Изменение позиции
        self.change_x = 0
        self.change_y = 0
        self.speed = PLAYER_SPEED
        self.is_blocked = False

    def draw_at_position(self, x, y):
        """Отрисовывает игрока в указанных координатах (с учетом смещения камеры)"""
        # Рисуем основной квадрат (синий спрайт)
        arcade.draw_texture_rect(self.texture,
                                 arcade.rect.XYWH(x, y,
                                                  self.width, self.height)
                                 )


class GameView(arcade.View):
    """Основной класс игры с оптимизацией для большой карты"""

    def __init__(self, x, y, element, level='первый'):
        super().__init__()
        self.x = x
        self.y = y
        self.element = element
        self.level = level

        # Списки спрайтов
        self.player_sprite = None
        self.block_sprites = None
        self.background_sprites = None  # Спрайт-лист для фоновых клеток
        self.room_sprites = None
        self.total_background_sprites = 0  # Общее количество фоновых клеток

        # Позиция камеры (как в вашем предыдущем коде)
        self.camera_offset_x = 0
        self.camera_offset_y = 0

        # Размеры мира
        self.world_width = TILE_SIZE * 250
        self.world_height = TILE_SIZE * 250

        # Ссылки на клавиши
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Для блокировки движения при комбинации клавиш
        self.block_movement = False
        self.block_direction = None

        # Статистика
        self.fps_text = ""
        self.visible_sprites = 0
        self.total_sprites = 0

        # Загружаем звуки
        self.collision_sound = None
        try:
            self.collision_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        except:
            pass

        # Загрузка текстуры для блоков
        self.block_texture = None
        self._load_textures()

        # Сетка комнат для проверки
        self.room_grid = None
        self.setup()

    def _load_textures(self):
        """Загружает текстуры для блоков и фона"""
        with open('elements.txt', 'r', encoding='utf-8') as f:
            a = f.read()
        a = [i.strip().split('\n') for i in a.split('|')]
        el = None
        for i in a:
            if i[0] == self.element:
                el = i[1:]
                break
        try:
            self.block_texture = arcade.load_texture(el[0])
            self.gorizontal_texture = arcade.load_texture(el[1])
            self.vertical_texture = arcade.load_texture(el[2])
            self.walls_1_texture = arcade.load_texture(el[3])
            self.walls_2_texture = arcade.load_texture(el[4])
            self.walls_3_texture = arcade.load_texture(el[5])
            self.walls_4_texture = arcade.load_texture(el[6])

            # Загружаем текстуру для фона (будет использоваться в BackgroundTile)
            # Это загрузка для внутреннего использования, если нужно
            self._background_texture = None
            try:
                self._background_texture = arcade.load_texture(el[7])
            except Exception as e:
                print(f"Ошибка предзагрузки фоновой текстуры: {e}")

            self._room_texture = None
            try:
                self._room_texture = arcade.load_texture(el[8])
            except Exception as e:
                print(f"Ошибка предзагрузки фоновой текстуры: {e}")

        except Exception as e:
            print(f"Ошибка загрузки текстур: {e}")
            # Создаем простые текстуры
            self.block_texture = arcade.make_soft_square_texture(
                TILE_SIZE,
                arcade.color.RED
            )

    def setup(self):
        """Инициализация игры"""
        # Создаем игрока
        self.player_sprite = Player()

        # Устанавливаем позицию игрока
        player_start = DUNGEON_MAP.get('player_start', [self.world_width / 2, self.world_height / 2])
        self.player_sprite.center_x = self.x
        self.player_sprite.center_y = self.y

        # Создаем список спрайтов для блоков
        self.block_sprites = arcade.SpriteList(
            use_spatial_hash=True)  # Используем пространственное хеширование для оптимизации
        self.total_sprites = 0

        # Создаем список спрайтов для фоновых клеток
        self.background_sprites = arcade.SpriteList(use_spatial_hash=True)
        self.total_background_sprites = 0

        self.room_sprites = arcade.SpriteList(use_spatial_hash=True)
        self.total_room_sprites = 0

        # Загружаем карту
        self._load_predefined_map()

        # Создаем сетку комнат для быстрой проверки
        self._create_room_grid()

        # Загружаем фоновые клетки
        self._load_background_tiles()
        self._load_room_tiles()

        print(f"Загружено спрайтов блоков: {self.total_sprites}")
        print(f"Загружено фоновых спрайтов: {self.total_background_sprites}")

        # Начальная позиция камеры
        self._center_camera_on_player(instant=True)

    def _create_room_grid(self):
        """Создает сетку для быстрой проверки комнат"""
        # Определяем размеры сетки
        grid_width = self.world_width // TILE_SIZE + 1
        grid_height = self.world_height // TILE_SIZE + 1

        # Создаем пустую сетку
        self.room_grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]

        # Заполняем сетку комнатами
        for y in range(len(dun)):
            for x in range(len(dun[y])):
                if dun[y][x] == '-' or dun[y][x] == '_':
                    # Конвертируем координаты
                    tile_grid_x = x
                    tile_grid_y = len(dun) - y - 1

                    # Проверяем границы
                    if 0 <= tile_grid_y < grid_height and 0 <= tile_grid_x < grid_width:
                        self.room_grid[tile_grid_y][tile_grid_x] = True

    def _check_room_collision(self):
        """Проверяет, находится ли игрок на клетке комнаты"""
        # Получаем координаты игрока в сетке
        grid_x = int(self.player_sprite.center_x // TILE_SIZE)
        grid_y = int(self.player_sprite.center_y // TILE_SIZE)

        # Проверяем границы массива
        if (0 <= grid_y < len(self.room_grid) and
                0 <= grid_x < len(self.room_grid[0])):
            return [self.room_grid[grid_y][grid_x], [grid_y, grid_x]]
        return False

    def _load_predefined_map(self):
        """Загружает предопределенную карту с оптимизацией"""
        print("Начало загрузки карты...")

        print(DUNGEON_MAP['gorizontal'])

        self.get_blocks('squares', self.block_texture)
        self.get_blocks('gorizontal', self.gorizontal_texture)
        self.get_blocks('vertical', self.vertical_texture)
        self.get_blocks('walls_1', self.walls_1_texture)
        self.get_blocks('walls_2', self.walls_2_texture)
        self.get_blocks('walls_3', self.walls_3_texture)
        self.get_blocks('walls_4', self.walls_4_texture)

        print(f"Загрузка карты завершена. Всего спрайтов: {self.total_sprites}")

    def get_blocks(self, name, texture):
        squares_data = DUNGEON_MAP.get(name, [])

        # Создаем спрайты партиями для производительности
        batch_size = 1000
        for i in range(0, len(squares_data), batch_size):
            batch = squares_data[i:i + batch_size]
            for x, y in batch:
                # Создаем спрайт блока
                block = arcade.Sprite()
                block.texture = texture
                block.width = TILE_SIZE
                block.height = TILE_SIZE
                block.center_x = x + TILE_SIZE / 2  # Центрируем
                block.center_y = y + TILE_SIZE / 2  # Центрируем

                self.block_sprites.append(block)
                self.total_sprites += 1

    def _load_background_tiles(self):
        """Загружает фоновые клетки для всех пустых мест на карте"""
        print("Начало загрузки фоновых клеток...")

        # Создаем набор координат стен для быстрой проверки
        wall_coords = set()
        squares_data = DUNGEON_MAP.get('squares', [])
        for x, y in squares_data:
            grid_x = x // TILE_SIZE
            grid_y = y // TILE_SIZE
            wall_coords.add((grid_x, grid_y))

        # Загружаем фоновые клетки партиями для производительности
        batch_size = 1000
        tiles_data = []

        # Собираем данные о пустых клетках
        for y in range(len(dun)):
            for x in range(len(dun[y])):
                # Проверяем, что это пустая клетка (пробел)
                if dun[y][x] == ' ':
                    tile_grid_x = x
                    tile_grid_y = len(dun) - y - 1  # Конвертируем координаты

                    # Проверяем, нет ли здесь стены
                    if (tile_grid_x, tile_grid_y) not in wall_coords:
                        tile_x = tile_grid_x * TILE_SIZE
                        tile_y = tile_grid_y * TILE_SIZE
                        tiles_data.append((tile_x, tile_y))

        print(f"Найдено пустых клеток: {len(tiles_data)}")

        # Создаем спрайты партиями
        for i in range(0, len(tiles_data), batch_size):
            batch = tiles_data[i:i + batch_size]
            for x, y in batch:
                # Создаем спрайт фоновой клетки
                tile = arcade.Sprite()
                tile.texture = self._background_texture
                tile.width = TILE_SIZE
                tile.height = TILE_SIZE
                tile.center_x = x + TILE_SIZE / 2
                tile.center_y = y + TILE_SIZE / 2

                self.background_sprites.append(tile)
                self.total_background_sprites += 1

            print(f"Загружено {self.total_background_sprites} фоновых спрайтов...")

        print(f"Загрузка фоновых клеток завершена. Всего: {self.total_background_sprites}")

    def _load_room_tiles(self):
        """Загружает фоновые клетки для всех пустых мест на карте"""
        print("Начало загрузки фоновых клеток...")

        # Создаем набор координат стен для быстрой проверки
        wall_coords = set()
        squares_data = DUNGEON_MAP.get('squares', [])
        for x, y in squares_data:
            grid_x = x // TILE_SIZE
            grid_y = y // TILE_SIZE
            wall_coords.add((grid_x, grid_y))

        # Загружаем фоновые клетки партиями для производительности
        batch_size = 1000
        tiles_data = []

        # Собираем данные о пустых клетках
        for y in range(len(dun)):
            for x in range(len(dun[y])):
                # Проверяем, что это -
                if dun[y][x] == '-' or dun[y][x] == '_':
                    tile_grid_x = x
                    tile_grid_y = len(dun) - y - 1  # Конвертируем координаты

                    # Проверяем, нет ли здесь стены
                    if (tile_grid_x, tile_grid_y) not in wall_coords:
                        tile_x = tile_grid_x * TILE_SIZE
                        tile_y = tile_grid_y * TILE_SIZE
                        tiles_data.append((tile_x, tile_y))

        print(f"Найдено room-клеток: {len(tiles_data)}")

        # Создаем спрайты партиями
        for i in range(0, len(tiles_data), batch_size):
            batch = tiles_data[i:i + batch_size]
            for x, y in batch:
                # Создаем спрайт фоновой клетки
                tile = arcade.Sprite()
                tile.texture = self._room_texture
                tile.width = TILE_SIZE
                tile.height = TILE_SIZE
                tile.center_x = x + TILE_SIZE / 2
                tile.center_y = y + TILE_SIZE / 2

                self.room_sprites.append(tile)
                self.total_room_sprites += 1

            print(f"Загружено {self.total_room_sprites} фоновых спрайтов...")

        print(f"Загрузка room-клеток завершена. Всего: {self.total_room_sprites}")

    def on_show(self):
        """Вызывается при показе этого вида"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        """Отрисовка игры"""
        self.clear()

        # Рисуем все с учетом смещения камеры

        # Сначала рисуем фоновые клетки (самый нижний слой)
        # Используем тот же подход, что и для блоков
        for tile in self.background_sprites:
            screen_x = tile.center_x - self.camera_offset_x
            screen_y = tile.center_y - self.camera_offset_y

            # Проверяем, находится ли клетка в видимой области
            if (-TILE_SIZE <= screen_x <= self.window.width + TILE_SIZE and
                    -TILE_SIZE <= screen_y <= self.window.height + TILE_SIZE):
                # Рисуем текстуру клетки
                if tile.texture:
                    arcade.draw_texture_rect(tile.texture,
                                             arcade.rect.XYWH(screen_x, screen_y,
                                                              tile.width, tile.height)
                                             )
                else:
                    # Если нет текстуры, рисуем цветной квадрат
                    arcade.draw_rectangle_filled(
                        screen_x, screen_y,
                        tile.width, tile.height,
                        arcade.color.DARK_GREEN
                    )

        for tile in self.room_sprites:
            screen_x = tile.center_x - self.camera_offset_x
            screen_y = tile.center_y - self.camera_offset_y

            # Проверяем, находится ли клетка в видимой области
            if (-TILE_SIZE <= screen_x <= self.window.width + TILE_SIZE and
                    -TILE_SIZE <= screen_y <= self.window.height + TILE_SIZE):
                # Рисуем текстуру клетки
                if tile.texture:
                    arcade.draw_texture_rect(tile.texture,
                                             arcade.rect.XYWH(screen_x, screen_y,
                                                              tile.width, tile.height)
                                             )
                else:
                    # Если нет текстуры, рисуем цветной квадрат
                    arcade.draw_rectangle_filled(
                        screen_x, screen_y,
                        tile.width, tile.height,
                        arcade.color.DARK_GREEN
                    )

        # Рисуем сетку (только видимую часть)
        self._draw_grid()

        # Рисуем блоки с учетом смещения камеры
        for block in self.block_sprites:
            screen_x = block.center_x - self.camera_offset_x
            screen_y = block.center_y - self.camera_offset_y

            # Проверяем, находится ли блок в видимой области
            if (-TILE_SIZE <= screen_x <= self.window.width + TILE_SIZE and
                    -TILE_SIZE <= screen_y <= self.window.height + TILE_SIZE):
                # Рисуем текстуру блока
                if block.texture:
                    arcade.draw_texture_rect(block.texture,
                                             arcade.rect.XYWH(screen_x, screen_y,
                                                              block.width, block.height)
                                             )
                else:
                    # Если нет текстуры, рисуем цветной квадрат
                    arcade.draw_rectangle_filled(
                        screen_x, screen_y,
                        block.width, block.height,
                        arcade.color.RED
                    )

        # Рисуем игрока с учетом смещения камеры
        player_screen_x = self.player_sprite.center_x - self.camera_offset_x
        player_screen_y = self.player_sprite.center_y - self.camera_offset_y

        # Рисуем игрока
        self.player_sprite.draw_at_position(player_screen_x, player_screen_y)

        # Рисуем HUD (без смещения камеры)
        self._draw_hud()

    def _draw_grid(self):
        """Рисуем клеточную сетку только для видимой область"""
        # Определяем видимую область
        left_bound = self.camera_offset_x
        right_bound = left_bound + self.window.width
        bottom_bound = self.camera_offset_y
        top_bound = bottom_bound + self.window.height

        # Определяем видимую область в координатах сетки
        start_x = max(0, int(left_bound // TILE_SIZE) - 1)
        end_x = min(self.world_width // TILE_SIZE,
                    int(right_bound // TILE_SIZE) + 2)

        start_y = max(0, int(bottom_bound // TILE_SIZE) - 1)
        end_y = min(self.world_height // TILE_SIZE,
                    int(top_bound // TILE_SIZE) + 2)

        # Рисуем только видимые линии сетки
        for x in range(start_x, end_x):
            draw_x = x * TILE_SIZE - self.camera_offset_x
            arcade.draw_line(draw_x, -self.camera_offset_y,
                             draw_x, self.world_height - self.camera_offset_y,
                             arcade.color.LIGHT_SLATE_GRAY, 1)

        for y in range(start_y, end_y):
            draw_y = y * TILE_SIZE - self.camera_offset_y
            arcade.draw_line(-self.camera_offset_x, draw_y,
                             self.world_width - self.camera_offset_x, draw_y,
                             arcade.color.LIGHT_SLATE_GRAY, 1)

    def _draw_hud(self):
        """Рисует интерфейс"""
        screen_width = self.window.width
        screen_height = self.window.height

        # Полупрозрачная панель для текста
        arcade.draw_lrbt_rectangle_filled(
            0, 400,
            screen_height - 200, screen_height,
            (0, 0, 0, 150)
        )

        arcade.draw_text(f"{self.level.upper()} УРОВЕНЬ",
                         screen_width // 2, screen_height - 40,
                         arcade.color.YELLOW, 24,
                         anchor_x="center", anchor_y="center")

        arcade.draw_text(f"Позиция: ({int(self.player_sprite.center_x)}, {int(self.player_sprite.center_y)})",
                         10, screen_height - 20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Скорость: {self.player_sprite.speed}",
                         10, screen_height - 45, arcade.color.WHITE, 14)
        arcade.draw_text(f"Блоков: {self.total_sprites}",
                         10, screen_height - 70, arcade.color.WHITE, 14)
        # Обновляем статистику для отображения фоновых клеток
        arcade.draw_text(f"Фоновых клеток: {self.total_background_sprites}",
                         10, screen_height - 95, arcade.color.WHITE, 14)
        arcade.draw_text(f"Видимых спрайтов: {self.visible_sprites}",
                         10, screen_height - 120, arcade.color.WHITE, 14)

        arcade.draw_text(f"element: {self.element}",
                         100, screen_height - 10, arcade.color.WHITE, 14)

        # Статус блокировки
        status_text = "Статус: Свободен"
        status_color = arcade.color.GREEN
        if self.player_sprite.is_blocked:
            status_text = "Статус: Заблокирован"
            status_color = arcade.color.RED
            if self.block_direction:
                status_text += f" ({self.block_direction})"

        arcade.draw_text(status_text,
                         10, screen_height - 145, status_color, 14)

        arcade.draw_text(f"FPS: {self.fps_text}",
                         screen_width - 100, screen_height - 30,
                         arcade.color.LIGHT_GREEN, 14,
                         anchor_x="right")

        arcade.draw_text("Управление: WASD/Стрелки",
                         10, screen_height - 170, arcade.color.LIGHT_GRAY, 12)
        arcade.draw_text("ESC - меню, +/- - скорость, SPACE - телепорт",
                         10, screen_height - 195, arcade.color.LIGHT_GRAY, 12)

    def on_update(self, delta_time):
        global LIST_POSESH
        """Обновление логики игры"""
        # Обновляем FPS
        self.fps_text = f"{int(1 / delta_time) if delta_time > 0 else 0}"

        # Сбрасываем флаг блокировки
        self.player_sprite.is_blocked = False
        self.block_movement = False
        self.block_direction = None

        # Обновляем движение игрока
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        # Сохраняем старую позицию для отката при столкновении
        old_x = self.player_sprite.center_x
        old_y = self.player_sprite.center_y

        # Применяем движение
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -self.player_sprite.speed
            if self.player_sprite.flip == 0:
                self.player_sprite.flip = 1
                self.player_sprite.texture = self.player_sprite.texture.flip_horizontally()
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = self.player_sprite.speed
            if self.player_sprite.flip == 1:
                self.player_sprite.flip = 0
                self.player_sprite.texture = self.player_sprite.texture.flip_horizontally()

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = self.player_sprite.speed
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -self.player_sprite.speed

        # Если нет движения - пропускаем проверку столкновений
        if self.player_sprite.change_x == 0 and self.player_sprite.change_y == 0:
            # Обновляем камеру и выходим
            self._center_camera_on_player()
            self._update_visible_sprites()
            return

        # Применяем движение к спрайту
        self.player_sprite.center_x += self.player_sprite.change_x
        self.player_sprite.center_y += self.player_sprite.change_y

        # Проверяем столкновения после движения
        colliding_sprites = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.block_sprites
        )

        if colliding_sprites:
            # Есть столкновение - откатываем движение
            self.player_sprite.center_x = old_x
            self.player_sprite.center_y = old_y
            self.player_sprite.is_blocked = True

            # Пробуем двигаться только по X
            if self.player_sprite.change_x != 0:
                self.player_sprite.center_x = old_x + self.player_sprite.change_x
                if arcade.check_for_collision_with_list(self.player_sprite, self.block_sprites):
                    self.player_sprite.center_x = old_x  # Откат по X
                    self.block_direction = 'horizontal'
                else:
                    # Движение по X возможно
                    self.player_sprite.center_x = old_x + self.player_sprite.change_x
                    self.player_sprite.is_blocked = False
                    self.block_direction = None
            else:
                self.block_direction = 'horizontal'

            # Пробуем двигаться только по Y
            if self.player_sprite.change_y != 0:
                self.player_sprite.center_y = old_y + self.player_sprite.change_y
                if arcade.check_for_collision_with_list(self.player_sprite, self.block_sprites):
                    self.player_sprite.center_y = old_y  # Откат по Y
                    self.block_direction = 'vertical' if not self.block_direction else 'both'
                else:
                    # Движение по Y возможно
                    self.player_sprite.center_y = old_y + self.player_sprite.change_y
                    self.player_sprite.is_blocked = False
                    if self.block_direction == 'horizontal':
                        self.block_direction = None
            else:
                if not self.block_direction:
                    self.block_direction = 'vertical'

            # Если оба направления заблокированы
            if self.block_direction == 'both':
                self.player_sprite.is_blocked = True
                self.block_movement = True
            else:
                self.block_movement = self.player_sprite.change_x != 0 and self.player_sprite.change_y != 0

            # Воспроизводим звук столкновения
            if self.collision_sound and self.player_sprite.is_blocked:
                arcade.play_sound(self.collision_sound, volume=0.3)

        # Проверка границ мира
        margin = TILE_SIZE * 0.5
        if self.player_sprite.center_x < margin:
            self.player_sprite.center_x = margin
            self.player_sprite.is_blocked = True
            self.block_direction = 'left'
        elif self.player_sprite.center_x > self.world_width - margin:
            self.player_sprite.center_x = self.world_width - margin
            self.player_sprite.is_blocked = True
            self.block_direction = 'right'

        if self.player_sprite.center_y < margin:
            self.player_sprite.center_y = margin
            self.player_sprite.is_blocked = True
            self.block_direction = 'bottom'
        elif self.player_sprite.center_y > self.world_height - margin:
            self.player_sprite.center_y = self.world_height - margin
            self.player_sprite.is_blocked = True
            self.block_direction = 'top'

        # Проверяем, находится ли игрок на клетке комнаты
        if self._check_room_collision()[0] and self._check_room_collision()[1] not in LIST_POSESH:
            print("Игрок вошел в комнату! Запуск карточной игры...")
            for dx in range(-8, 9):
                for dy in range(-8, 9):
                    a = self._check_room_collision()[1]
                    a[0] += dy
                    a[1] += dx
                    LIST_POSESH.append(a)
            self.start_card_game(self.player_sprite.center_x, self.player_sprite.center_y)

        # Обновляем камеру
        self._center_camera_on_player()

        # Подсчитываем видимые спрайты (для статистики)
        self._update_visible_sprites()

    def start_card_game(self, x, y):
        """Запускает карточную игру"""
        grid_x = int(self.player_sprite.center_x // TILE_SIZE)
        grid_y = 250 - int(self.player_sprite.center_y // TILE_SIZE) - 1
        print(grid_y, grid_x, dun[grid_y][grid_x])
        card_game_view = CardGameView(x, y, self.element, self.level, dun[grid_y][grid_x])
        self.window.show_view(card_game_view)

    def _center_camera_on_player(self, instant=False):
        """Центрирует камеру на игроке (как в вашем предыдущем коде)"""
        target_offset_x = self.player_sprite.center_x - self.window.width / 2
        target_offset_y = self.player_sprite.center_y - self.window.height / 2

        target_offset_x = max(0, min(target_offset_x, self.world_width - self.window.width))
        target_offset_y = max(0, min(target_offset_y, self.world_height - self.window.height))

        if instant:
            self.camera_offset_x = target_offset_x
            self.camera_offset_y = target_offset_y
        else:
            smooth_speed = 0.15
            self.camera_offset_x += (target_offset_x - self.camera_offset_x) * smooth_speed
            self.camera_offset_y += (target_offset_y - self.camera_offset_y) * smooth_speed

    def _update_visible_sprites(self):
        """Подсчитывает количество видимых спрайтов"""
        # Получаем границы камеры с небольным запасом
        left_bound = self.camera_offset_x - TILE_SIZE * 2
        right_bound = self.camera_offset_x + self.window.width + TILE_SIZE * 2
        bottom_bound = self.camera_offset_y - TILE_SIZE * 2
        top_bound = self.camera_offset_y + self.window.height + TILE_SIZE * 2

        # Простой подсчет - проверяем каждый спрайт
        visible_count = 0

        # Подсчитываем видимые блоки
        if self.total_sprites > 10000:
            # Для очень больших карт используем приблизительный расчет
            visible_area = (right_bound - left_bound) * (top_bound - bottom_bound)
            world_area = self.world_width * self.world_height
            if world_area > 0:
                visible_fraction = visible_area / world_area
                visible_count = int(self.total_sprites * visible_fraction)
        else:
            # Для меньшего количества спрайтов проверяем каждый блок
            for sprite in self.block_sprites:
                if (left_bound <= sprite.center_x <= right_bound and
                        bottom_bound <= sprite.center_y <= top_bound):
                    visible_count += 1

        self.visible_sprites = visible_count

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.ESCAPE:
            self.show_pause_screen()
        elif key == arcade.key.PLUS or key == arcade.key.EQUAL:
            self.player_sprite.speed = min(self.player_sprite.speed + 1, 15)
        elif key == arcade.key.MINUS:
            self.player_sprite.speed = max(self.player_sprite.speed - 1, 1)
        elif key == arcade.key.R:
            self.setup()
        elif key == arcade.key.C:
            # Мгновенное центрирование камеры
            self._center_camera_on_player(instant=True)
        elif key == arcade.key.T:
            self._teleport_player()

    def _teleport_player(self):
        """Телепортирует игрока в случайную свободную позицию"""
        attempts = 0
        while attempts < 100:
            new_x = random.randint(TILE_SIZE * 2, self.world_width - TILE_SIZE * 2)
            new_y = random.randint(TILE_SIZE * 2, self.world_height - TILE_SIZE * 2)

            # Временный спрайт для проверки столкновений
            temp_sprite = arcade.Sprite()
            temp_sprite.width = self.player_sprite.width
            temp_sprite.height = self.player_sprite.height
            temp_sprite.center_x = new_x
            temp_sprite.center_y = new_y

            # Проверяем столкновения
            if not arcade.check_for_collision_with_list(temp_sprite, self.block_sprites):
                self.player_sprite.center_x = new_x
                self.player_sprite.center_y = new_y
                self.player_sprite.center_x = 8000
                self.player_sprite.center_y = 14600
                try:
                    teleport_sound = arcade.load_sound(":resources:sounds/coin5.wav")
                    arcade.play_sound(teleport_sound)
                except:
                    pass
                break

            attempts += 1

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False

    def back_to_menu(self):
        global LIST_POSESH
        """Возврат в главное меню"""
        try:
            background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
            menu_view = MenuView(background_texture)
            LIST_POSESH = []
        except:
            menu_view = MenuView()
            LIST_POSESH = []
        self.window.show_view(menu_view)

    def show_pause_screen(self):
        pause_view = PauseScreenView(self)
        self.window.show_view(pause_view)


# --- Класс карточной игры ---
class CardGameView(arcade.View):
    def __init__(self, x, y, element, level, room):
        super().__init__()
        self.coords = (x, y)
        self.element = element
        self.level = level
        self.room = room
        self.SCREEN_WIDTH = int(800 * 1.28)  # 1024
        self.SCREEN_HEIGHT = int(600 * 1.28)  # 768
        self.TITLE = "Карточная игра"

        self.cards = []
        self.deck = []
        self.defence = []
        self.defence_amount = 0
        self.player = None
        self.mobs = []
        self.background_texture = None
        self.midground_texture = None
        self.current_slime = None
        self.window.set_size(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.end_turn_button = None
        self.turn_number = 1
        self.is_player_turn = True
        self.deaded = []

        # Добавляем эмиттер урона
        self.damage_emitter = DamageEmitter()
        self.heal_emitter = DamageEmitter()  # Для исцеления

        self.setup()

    def setup(self):
        """Настройка игры"""
        # Создаем игрока с указанными параметрами
        player_image_path = "images/Texture2D/mag_1.png"
        self.player = Fight_player("Игрок", player_image_path, max_hp=100, max_mana=50)

        # Создаем случайного слизня при запуске
        self.create_random_slime()

        # Загрузка фоновых текстур
        try:
            self.background_texture = arcade.load_texture("images/Texture2D/Unfinished Meal Far Backgroundl.png")
            self.midground_texture = arcade.load_texture("images/Texture2D/Warrior Statue Mid Background.png")
        except:
            print("Не удалось загрузить фоновые текстуры")

        self.end_turn_button = EndTurnButton(int(700 * 1.28), int(550 * 1.28))  # 896, 704

        # Создаем 5 карт на игровом столе
        self.create_coloda()
        self.create_cards_on_table()

    def create_random_slime(self):
        """Создание случайного слизня"""
        # Очищаем список мобов
        self.mobs.clear()
        level = ['первый', "второй", "третий"].index(self.level)
        with open('enemies.txt', 'r', encoding='utf-8') as f:
            a = f.read()
        mobs_list = a.split('|')[level].split('-')[1:]
        mobs = random.choice(mobs_list)
        mobs_pos = [i.split(', ') for i in mobs.split('\n')[1].split('/')]
        enemies_pos = [(int(int(i[0]) * 1.28), int(int(i[1]) * 1.28)) for i in mobs_pos]
        enemies_types = mobs.split('\n')[2].split(', ')

        # Создаем слизня
        for i in range(len(enemies_pos)):
            new_slime = Slime(enemies_types[i], enemies_pos[i][0], enemies_pos[i][1])
            self.mobs.append(new_slime)

            print(f"Создан новый слизень: {new_slime.name}")
            print(f"Размер: {new_slime.width}x{new_slime.height} пикселей")
            print(f"Здоровье: {new_slime.current_hp}/{new_slime.max_hp}")
            print(f"Урон: {new_slime.damage}")

    def create_coloda(self):
        self.coloda = [i for i in CURRENT_COLODA]

    def create_cards_on_table(self):
        """Создает 5 карт на игровом столе"""
        # Параметры стола
        table_height = int(150 * 1.28)  # 192

        # Параметры карт (увеличенные размеры)
        card_width = int(130 * 1.28)  # 166
        card_height = int(220 * 1.28)  # 282
        card_spacing = int(5 * 1.28)  # 6

        # Позиционируем карты внизу экрана
        bottom_margin = int(20 * 1.28)  # 26
        cards_y = bottom_margin + table_height / 2 - int(80 * 1.28)  # Позиция карт

        # Вычисляем начальную позицию для первой карты
        total_cards_width = 5 * card_width + 4 * card_spacing
        start_x = self.width // 2 - total_cards_width // 2 + card_width // 2

        self.arm = []
        for i in range(5):
            if len(self.coloda) == 0:
                for c in self.deck:
                    self.coloda.append(c)
                self.deck = []
            card = random.choice(self.coloda)
            self.arm.append(card)
            self.coloda.remove(card)

        colors = [
            arcade.color.LIGHT_SALMON,
            arcade.color.BLUE,
            arcade.color.LIGHT_GREEN,
            arcade.color.LIGHT_GRAY,
            arcade.color.LIGHT_PINK,
            (230, 226, 122),
            (92, 58, 126)

        ]

        for i in range(5):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = cards_y  # Карты внизу экрана

            color = (self.arm[i]['id'] - 1) // 10

            # Создаем карту с увеличенными размерами
            card = Card(
                x=card_x,
                y=card_y,
                width=card_width,
                height=card_height,
                text=self.arm[i]['name'],
                image_path=None,  # Пустая карта
                description=self.arm[i]['description'],
                card_color=colors[color],
                hover_color=colors[color],
                text_color=arcade.color.BLACK,
                description_color=arcade.color.DARK_BROWN,
                font_size=int(12 * 1.28),  # 15
                description_font_size=int(9 * 1.28),  # 12
                dict=self.arm[i]
            )

            self.cards.append(card)

    def on_draw(self):
        """Отрисовка игры"""
        self.clear()

        # Рисуем фон если текстуры загружены
        if self.background_texture:
            background_rect = arcade.rect.XYWH(
                self.width // 2,
                self.height // 2,
                self.width,
                self.height
            )
            arcade.draw_texture_rect(self.background_texture, background_rect)

        if self.midground_texture:
            midground_rect = arcade.rect.XYWH(
                self.width // 2,
                self.height // 2,
                self.width,
                self.height
            )
            arcade.draw_texture_rect(self.midground_texture, midground_rect)

        # Рисуем игровой стол
        table_width = self.width * 0.9
        table_height = int(150 * 1.28)  # 192
        table_x = self.width // 2
        table_y = table_height // 2

        table_rect = arcade.rect.XYWH(table_x, table_y, table_width, table_height)
        arcade.draw_rect_filled(table_rect, arcade.color.DARK_BROWN)
        arcade.draw_rect_outline(table_rect, arcade.color.BLACK, border_width=int(3 * 1.28))  # 4

        # Рисуем игрока
        if self.player:
            self.player.draw()

        # Рисуем всех мобов
        for mob in self.mobs:
            mob.draw()

        # Рисуем частицы урона и исцеления ПОВЕРХ всех объектов
        self.damage_emitter.draw()
        self.heal_emitter.draw()

        # Рисуем все карты
        for card in self.cards:
            card.draw()

        if self.end_turn_button:
            self.end_turn_button.draw()

        arcade.draw_text(
            f"ХОД: {self.turn_number}",
            int(700 * 1.28),  # 896
            int(500 * 1.28),  # 640
            arcade.color.GOLD,
            int(16 * 1.28),  # 20
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"Колода: {len(self.coloda)} | Сброс: {len(self.deck)}",
            int(400 * 1.28),  # 512
            int(560 * 1.28),  # 717
            arcade.color.LIGHT_GRAY,
            int(12 * 1.28),  # 15
            anchor_x="center",
            anchor_y="center"
        )

        arcade.draw_text(
            f"Защита: {self.defence_amount}",
            int(400 * 1.28),  # 512
            int(530 * 1.28),  # 678
            arcade.color.LIGHT_GRAY,
            int(12 * 1.28),  # 15
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        """Обновление логики игры"""
        for card in self.cards:
            card.update()
        for mob in self.mobs:
            mob.update()
        if all(mob.end_animation for mob in self.mobs) and self.mobs:
            for mob in self.mobs:
                mob.end_animation = False
            self.continue_enemy_turn()

        # Обновляем эмиттеры урона и исцеления
        self.damage_emitter.update(delta_time)
        self.heal_emitter.update(delta_time)

        if self.end_turn_button:
            self.end_turn_button.is_enabled = (
                    self.is_player_turn and
                    self.player.current_mana < 50)

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.P:  # P или русская П
            self.create_random_slime()
            print("Нажата клавиша P - создан новый случайный слизень!")
        elif key == arcade.key.ESCAPE:
            self.show_pause_screen()

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for card in self.cards:
            card.check_mouse_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        for card in self.cards:
            if card.check_mouse_hover(x, y):
                card.on_press()
        for mob in self.mobs:
            if mob.check_mouse_hover(x, y):
                fake_mobs = [m for m in self.mobs]
                fake_mobs.remove(mob)
                mob.on_press()
                for m in fake_mobs:
                    m.current = 0

        if self.end_turn_button and self.end_turn_button.check_hover(x, y):
            self.end_turn_button.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        for card in self.cards:
            if card.on_release():
                print(f"Нажата карта: {card.text}")
                print(f"Описание: {card.description}")

                for i in self.mobs:
                    if i.current == 1:
                        self.current_slime = i

                flag = 0

                for c in card.dict['colvo']:
                    if c == '0':
                        if "Исцеление" in card.dict['effects'] and self.player and card.is_playable:
                            if not card.is_mana and card.dict['colvo'].index(c) == 0:
                                if self.player.use_mana(card.dict['mana']):
                                    card.is_mana = True
                                    print(f"Тратится {card.dict['mana']} маны на исцеление!")
                                else:
                                    print("Недостаточно маны!")
                                    flag = 1
                            if card.is_mana:
                                a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                heal_amount = random.randrange(a1, a2 + 1)
                                print(f"Игрок получает {heal_amount} здоровья!")

                                # Добавляем частицу исцеления (зеленый цвет)
                                if heal_amount >= 0:
                                    heal_pos = self.player.get_damage_position()
                                    self.heal_emitter.add_damage(
                                        heal_pos[0],
                                        heal_pos[1],
                                        f"+{heal_amount}",
                                        False  # Можно сделать отдельный цвет для исцеления
                                    )
                                    # Меняем цвет на зеленый для исцеления
                                    self.heal_emitter.particles[-1].color = arcade.color.LIGHT_GREEN
                                else:
                                    heal_pos = self.player.get_damage_position()
                                    self.heal_emitter.add_damage(
                                        heal_pos[0],
                                        heal_pos[1],
                                        f"{heal_amount}",
                                        False  # Можно сделать отдельный цвет для исцеления
                                    )
                                    # Меняем цвет на красный для исцеления
                                    self.heal_emitter.particles[-1].color = arcade.color.RED

                                self.player.heal(heal_amount)
                                card.is_mana = True
                        elif "Защита" in card.dict['effects'] and self.player and card.is_playable:
                            if not card.is_mana and card.dict['colvo'].index(c) == 0:
                                if self.player.use_mana(card.dict['mana']):
                                    card.is_mana = True
                                    print(f"Тратится {card.dict['mana']} маны на защиту!")
                                else:
                                    print("Недостаточно маны!")
                                    flag = 1
                            if card.is_mana:
                                self.defence.append([card.text, card.dict['damage'][0][0]])
                                print(self.defence)
                                self.defence_amount = sum([i[1] for i in self.defence])
                        else:
                            flag = 1
                            break
                    elif c == '1':
                        if self.player and (self.current_slime is not None) and card.is_playable:
                            if not card.is_mana and card.dict['colvo'].index(c) == 0:
                                if self.player.use_mana(card.dict['mana']):
                                    card.is_mana = True
                                    print(f"Тратится {card.dict['mana']} маны на магию!")
                                else:
                                    print("Недостаточно маны!")
                                    flag = 1
                            if card.is_mana:
                                if self.player and self.current_slime and self.current_slime.is_alive:
                                    a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                    damage = random.randrange(a1, a2 + 1)
                                    self.attack_mob(damage, self.current_slime)
                                    card.is_mana = True
                        else:
                            flag = 1
                            break
                    elif "рандом" in c:
                        if self.player and card.is_playable and "рандом" in c:
                            if not card.is_mana and card.dict['colvo'].index(c) == 0:
                                if self.player.use_mana(card.dict['mana']):
                                    card.is_mana = True
                                    print(f"Тратится {card.dict['mana']} маны на магию!")
                                else:
                                    print("Недостаточно маны!")
                                    flag = 1
                            if card.is_mana:
                                print("Мана успешно потрачена!")
                                count = int(c.split()[-1])
                                fake_mobs = [m for m in self.mobs]
                                if card.dict['colvo'][0] == '1' and self.current_slime:
                                    fake_mobs.remove(self.current_slime)
                                for i in range(count):
                                    if len(fake_mobs) == 0:
                                        break
                                    mob = random.choice(fake_mobs)
                                    a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                    damage = random.randrange(a1, a2 + 1)
                                    self.attack_mob(damage, mob)
                                    fake_mobs.remove(mob)
                                card.is_mana = True
                        else:
                            flag = 1
                            break
                    elif c == 'все':
                        if self.player and card.is_playable and c == 'все' and len(self.mobs) != 0:
                            if not card.is_mana and card.dict['colvo'].index(c) == 0:
                                if self.player.use_mana(card.dict['mana']):
                                    card.is_mana = True
                                    print(f"Тратится {card.dict['mana']} маны на магию!")
                                else:
                                    print("Недостаточно маны!")
                                    flag = 1
                            if card.is_mana:
                                print("Мана успешно потрачена!")
                                a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                damage = random.randrange(a1, a2 + 1)
                                fake_mobs = [m for m in self.mobs]
                                if card.dict['colvo'][0] == '1' and self.current_slime:
                                    fake_mobs.remove(self.current_slime)
                                for mob in fake_mobs:
                                    self.attack_mob(damage, mob)
                                card.is_mana = True
                        else:
                            flag = 1
                            break
                if len(self.deaded) > 0:
                    for mob in self.deaded:
                        self.mobs.remove(mob)
                    self.deaded = []
                if flag == 0:
                    card.is_playable = False
                    card.is_mana = False

        if self.player.current_hp <= 0:
            print("Игрок повержен! Показываем экран смерти.")

            # Создаем и показываем экран смерти
            death_screen = DeathScreenView(self.element, self.level)
            # Восстанавливаем размер окна
            self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.window.show_view(death_screen)
            return

        if self.end_turn_button and self.end_turn_button.on_release():
            print("Кнопка 'Конец хода' нажата!")
            self.end_player_turn()

    def attack_current_slime(self, damage):
        """Атака текущего слизня с визуальным эффектом"""
        if not self.current_slime or not self.current_slime.is_alive:
            print("Нет живого слизня для атаки!")
            return

        # Наносим урон
        print(f"Атакуем {self.current_slime.name} на {damage} урона!")

        # Добавляем частицу урона
        damage_pos = self.current_slime.get_damage_position()
        self.damage_emitter.add_damage(
            damage_pos[0],
            damage_pos[1],
            damage
        )

        survived = self.current_slime.take_damage(damage)

        if not survived:
            print(f"{self.current_slime.name} повержен!")
            self.mobs.remove(self.current_slime)
            self.current_slime = None
        else:
            print(f"{self.current_slime.name} осталось {self.current_slime.current_hp} HP")

    def attack_mob(self, damage, mob):
        if not mob or not mob.is_alive:
            return

        # Добавляем частицу урона
        damage_pos = mob.get_damage_position()
        self.damage_emitter.add_damage(
            damage_pos[0],
            damage_pos[1],
            damage
        )

        survived = mob.take_damage(damage)

        if not survived:
            print(f"{mob} повержен!")
            self.deaded.append(mob)
            if self.current_slime in self.deaded:
                self.current_slime = None
        else:
            print(f"{mob.name} осталось {mob.current_hp} HP")

    def end_player_turn(self):
        if not self.is_player_turn:
            return
        print(f"\n=== Завершение хода {self.turn_number} ===")
        # Восстанавливаем всю ману
        self.player.current_mana = self.player.max_mana
        for card in self.arm:
            self.deck.append(card)
        self.arm = []
        self.cards = []
        self.is_player_turn = False
        self.enemy_turn()

    def new_turn(self):
        print(len(self.coloda), len(self.deck))
        self.turn_number += 1
        self.cards = []
        self.create_cards_on_table()

    def enemy_turn(self):
        """Ход врагов с визуальным эффектом"""
        enemies = [mob for mob in self.mobs if mob.is_alive]
        if enemies:
            for enemy in enemies:
                enemy.start_animation()
        else:
            # Создаем и показываем экран смерти
            win_screen = WinScreenView(self.coords[0], self.coords[1], self.element, self.level, self.room)
            # Восстанавливаем размер окна
            self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.window.show_view(win_screen)
            return

    def continue_enemy_turn(self):
        enemies = [mob for mob in self.mobs if mob.is_alive]
        for enemy in enemies:
            damage = enemy.attack()
            print(f"{enemy.name} атакует игрока на {damage} урона!")
            # Добавляем частицу урона игроку
            damage_pos = self.player.get_damage_position()
            self.damage_emitter.add_damage(
                damage_pos[0],
                damage_pos[1],
                damage,
                False
            )
            if self.defence:
                self.defence[0][1] -= damage
                self.damage_emitter.particles[-1].color = arcade.color.LIGHT_GRAY
                if self.defence[0][1] <= 0:
                    self.defence.remove(self.defence[0])
                if self.defence:
                    self.defence_amount = sum([i[1] for i in self.defence])
                else:
                    self.defence_amount = 0
            else:
                self.player.take_damage(damage)
            if self.player.current_hp <= 0:
                print("Игрок повержен! Показываем экран смерти.")

                # Создаем и показываем экран смерти
                death_screen = DeathScreenView(self.element, self.level)
                # Восстанавливаем размер окна
                self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
                self.window.show_view(death_screen)
                return

        if all(enemy.end_animation is False for enemy in self.mobs if enemy.is_alive):
            self.is_player_turn = True
            self.defence = []
            self.defence_amount = 0
            self.new_turn()

    def show_pause_screen(self):
        pause_view = PauseScreenView(self)
        self.window.show_view(pause_view)


# --- Класс меню ---
class MenuView(arcade.View):
    """Класс для экрана меню"""

    def __init__(self, background_texture=None):
        global DUNGEON_MAP
        global dun
        super().__init__()

        dung = random_dun()
        self.element = random.choice(['fire', 'water', 'stone', 'wind', 'lightning', 'light', 'dark'])
        self.level = 'первый'
        dun = dung['dungeon']
        DUNGEON_MAP = {
            "name": dung['name'],
            "world_width": TILE_SIZE * 250,  # 16000
            "world_height": TILE_SIZE * 250,  # 16000
            "player_start": [TILE_SIZE * dung['start'][0], TILE_SIZE * dung['start'][1]],  # Центр
            "squares": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '*'],
            "gorizontal": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '#'],
            "vertical": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '$'],
            "walls_1": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '1'],
            "walls_2": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '2'],
            "walls_3": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '3'],
            "walls_4": [
                [x * TILE_SIZE, (len(dun) - y - 1) * TILE_SIZE] for y in range(len(dun)) for x
                in range(len(dun[y])) if dun[y][x] == '4']
        }

        self.background_texture = background_texture
        self.buttons = []
        self.status_text = ""
        self.setup()

    def setup(self):
        """Настройка меню"""
        # Создаем кнопки
        button1 = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.7,
            width=300,
            height=60,
            text="Начать игру",
            color=arcade.color.DARK_GREEN,
            hover_color=arcade.color.GREEN
        )

        button2 = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.55,
            width=300,
            height=60,
            text="Колода",
            color=arcade.color.PURPLE,
            hover_color=arcade.color.VIOLET
        )

        button3 = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.4,
            width=300,
            height=60,
            text="Настройки",
            color=arcade.color.DARK_BLUE_GRAY,
            hover_color=arcade.color.LIGHT_BLUE
        )

        button4 = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.25,
            width=300,
            height=60,
            text="Выход",
            color=arcade.color.DARK_RED,
            hover_color=arcade.color.RED
        )

        self.buttons = [button1, button2, button3, button4]

    def on_show(self):
        """Вызывается при показе этого вида"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        """Отрисовка меню"""
        self.clear()
        arcade.draw_texture_rect(self.background_texture,
                                     arcade.rect.XYWH(self.window.width // 2,
                                                      self.window.height // 2,
                                                      self.window.width,
                                                      self.window.height)
                                     )

        # Рисуем заголовок
        arcade.draw_text(
            "Cards and Dungeons",
            self.window.width // 2,
            self.window.height * 0.85,
            arcade.color.WHITE,
            45,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            "v1.5 - Коллекционная карточная RPG",
            self.window.width // 2,
            self.window.height * 0.8,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            anchor_y="center"
        )

        # Рисуем все кнопки
        for button in self.buttons:
            button.draw()

        # Рисуем статусный текст
        if self.status_text:
            arcade.draw_text(
                self.status_text,
                self.window.width // 2,
                self.window.height * 0.2,
                arcade.color.WHITE,
                24,
                anchor_x="center",
                anchor_y="center"
            )

        # Инструкция внизу
        arcade.draw_text(
            "Нажмите на кнопку для выбора действия",
            self.window.width // 2,
            self.window.height * 0.1,
            arcade.color.LIGHT_GRAY,
            16,
            anchor_x="center",
            anchor_y="center"
        )

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for button in self.buttons:
            button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons:
                if btn.is_hovered:
                    btn.on_press()

                    # Выполняем действие в зависимости от кнопки
                    if btn.text == "Начать игру":
                        self.status_text = "Загрузка игры..."
                        # Создаем и показываем игровой экран с предопределенной картой
                        x, y = DUNGEON_MAP['player_start']
                        game_view = GameView(x, y, self.element, self.level)
                        self.window.show_view(game_view)

                    elif btn.text == "Колода":
                        self.status_text = "Редактор колоды..."
                        deck_builder_view = DeckBuilderView(self.background_texture)
                        self.window.show_view(deck_builder_view)

                    elif btn.text == "Настройки":
                        self.status_text = "Настройки открыты"
                        # Здесь можно добавить переход к экрану настроек

                    elif btn.text == "Выход":
                        self.status_text = "Выход из игры..."
                        arcade.schedule(self.exit_game, 1.0)

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.buttons:
                if btn.is_pressed:
                    btn.on_release()

    def exit_game(self, delta_time):
        """Завершает игру"""
        arcade.close_window()


# --- Главная функция ---
def main():
    """Главная функция"""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)

    background_texture = None
    try:
        background_texture = arcade.load_texture("images/backgrounds/Меню.jpg")
    except:
        pass

    menu_view = MenuView(background_texture)
    window.show_view(menu_view)

    arcade.run()


if __name__ == "__main__":
    main()
