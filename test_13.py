import arcade
import random
import math
import sys
import os
from dungeons import *
from test_fight import *
from emitter_damage import *

# Константы для меню
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TITLE = "Игра с меню и спрайтами"
TILE_SIZE = 64
PLAYER_SPEED = 10

# Предопределенная карта (координаты квадратов)
DUNGEON_MAP = {}
dun = None
LIST_POSESH = []


class DeathScreenView(arcade.View):
    """Окно смерти с случайными фразами"""

    def __init__(self, background_texture=None):
        super().__init__()
        self.background_texture = background_texture
        self.death_phrases = []
        self.current_phrase = ""
        self.load_death_phrases()
        self.select_random_phrase()

        # Кнопки
        self.restart_button = Button(
            x=self.window.width // 2 - 150,
            y=self.window.height * 0.3,
            width=280,
            height=60,
            text="Начать заново",
            color=arcade.color.DARK_GREEN,
            hover_color=arcade.color.GREEN
        )

        self.menu_button = Button(
            x=self.window.width // 2 + 150,
            y=self.window.height * 0.3,
            width=280,
            height=60,
            text="В главное меню",
            color=arcade.color.DARK_BLUE,
            hover_color=arcade.color.LIGHT_BLUE
        )

        self.quit_button = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.2,
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

            # Подсказка
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
        game_view = GameView(x, y)
        self.window.show_view(game_view)

    def return_to_menu(self):
        """Возврат в главное меню"""
        print("Возврат в главное меню...")
        try:
            background_texture = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")
            menu_view = MenuView(background_texture)
        except:
            menu_view = MenuView()
        self.window.show_view(menu_view)

    def quit_game(self):
        """Выход из игры"""
        print("Выход из игры...")
        arcade.close_window()


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

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

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
        try:
            self.block_texture = arcade.load_texture("images/tiles/lava.jpg")
            self.gorizontal_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_г.jpg")
            self.vertical_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_в.jpg")
            self.walls_1_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_1.jpg")
            self.walls_2_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_2.jpg")
            self.walls_3_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_3.jpg")
            self.walls_4_texture = arcade.load_texture("images/tiles/Тьма/темная бездна_4.jpg")

            # Загружаем текстуру для фона (будет использоваться в BackgroundTile)
            # Это загрузка для внутреннего использования, если нужно
            self._background_texture = None
            try:
                if os.path.exists("images/tiles/fire_land.jpg"):
                    self._background_texture = arcade.load_texture("images/tiles/Тьма/темная земля_1.jpg")
            except Exception as e:
                print(f"Ошибка предзагрузки фоновой текстуры: {e}")

            self._room_texture = None
            try:
                if os.path.exists("images/tiles/magma_2.jpg"):
                    self._room_texture = arcade.load_texture("images/tiles/Тьма/темная земля_2.jpg")
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
                if dun[y][x] == '-':
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
                if dun[y][x] == '-':
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

        arcade.draw_text("ПЕРВЫЙ УРОВЕНЬ",
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
        """Запускает карточную игру"""  # Импортируем здесь, чтобы избежать циклического импорта
        card_game_view = CardGameView(x, y)
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
            self.back_to_menu()
        elif key == arcade.key.PLUS or key == arcade.key.EQUAL:
            self.player_sprite.speed = min(self.player_sprite.speed + 1, 15)
        elif key == arcade.key.MINUS:
            self.player_sprite.speed = max(self.player_sprite.speed - 1, 1)
        elif key == arcade.key.R:
            self.setup()
        elif key == arcade.key.C:
            # Мгновенное центрирование камеры
            self._center_camera_on_player(instant=True)
        elif key == arcade.key.SPACE:
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
            background_texture = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")
            menu_view = MenuView(background_texture)
            LIST_POSESH = []
        except:
            menu_view = MenuView()
            LIST_POSESH = []
        self.window.show_view(menu_view)


# --- Класс карточной игры ---
class CardGameView(arcade.View):
    def __init__(self, x, y):
        super().__init__()
        self.coords = (x, y)
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.TITLE = "Карточная игра"

        self.cards = []
        self.deck = []
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

        self.end_turn_button = EndTurnButton(700, 550)

        # Создаем 5 карт на игровом столе
        self.create_coloda()
        self.create_cards_on_table()

    def create_random_slime(self):
        """Создание случайного слизня"""
        # Очищаем список мобов
        self.mobs.clear()

        # Создаем слизня в центре правой части экрана
        enemies_pos = [(550, 400), (675, 325), (550, 250)]
        enemies_types = ["small", "large", "medium"]

        # Создаем слизня
        for i in range(3):
            new_slime = Slime(enemies_types[i], enemies_pos[i][0], enemies_pos[i][1])
            self.mobs.append(new_slime)

            print(f"Создан новый слизень: {new_slime.name}")
            print(f"Размер: {new_slime.width}x{new_slime.height} пикселей")
            print(f"Здоровье: {new_slime.current_hp}/{new_slime.max_hp}")
            print(f"Урон: {new_slime.damage}")

    def create_coloda(self):
        self.coloda = [None] * 50
        for i in range(50):
            self.coloda[i] = create_card(i + 1)

    def create_cards_on_table(self):
        """Создает 5 карт на игровом столе"""
        # Параметры стола
        table_height = 150  # Высота стола

        # Параметры карт (увеличенные размеры)
        card_width = 130  # Увеличенная ширина
        card_height = 220  # Увеличенная высота
        card_spacing = 5  # Увеличенное расстояние между картами

        # Позиционируем карты внизу экрана
        bottom_margin = 20  # Отступ от нижнего края
        cards_y = bottom_margin + table_height / 2 - 80  # Позиция карт

        # Вычисляем начальную позицию для первой карты
        total_cards_width = 5 * card_width + 4 * card_spacing
        start_x = self.width // 2 - total_cards_width // 2 + card_width // 2

        # Создаем 5 карт с разными свойствами
        fake_coloda = [i for i in self.coloda]
        self.arm = []
        for i in range(5):
            if len(fake_coloda) == 0:
                self.coloda = [c for c in self.deck]
                fake_coloda = [c for c in self.coloda]
                self.deck = []
            card = random.choice(fake_coloda)
            fake_coloda.remove(card)
            self.arm.append(card)

        colors = [
            arcade.color.LIGHT_SALMON,
            arcade.color.BLUE,
            arcade.color.LIGHT_GREEN,
            arcade.color.LIGHT_GRAY,
            arcade.color.LIGHT_PINK
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
                font_size=12,
                description_font_size=9,
                dict=self.arm[i]
            )

            self.cards.append(card)
        print(self.arm, self.cards)

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
        table_height = 150
        table_x = self.width // 2
        table_y = table_height // 2

        table_rect = arcade.rect.XYWH(table_x, table_y, table_width, table_height)
        arcade.draw_rect_filled(table_rect, arcade.color.DARK_BROWN)
        arcade.draw_rect_outline(table_rect, arcade.color.BLACK, border_width=3)

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
            700,
            500,
            arcade.color.GOLD,
            16,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        arcade.draw_text(
            f"Колода: {len(self.coloda)} | Сброс: {len(self.deck)}",
            400,
            560,
            arcade.color.LIGHT_GRAY,
            12,
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        """Обновление логики игры"""
        for card in self.cards:
            card.update()

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
            # Возвращаемся в основную игру
            x, y = self.coords
            game_view = GameView(x, y)
            # Восстанавливаем размер окна
            self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.window.show_view(game_view)

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
                            print(f"Тратится {card.dict['mana']} маны на исцеление!")
                            if self.player.use_mana(card.dict['mana']) or card.is_mana:
                                print("Мана успешно потрачена!")
                                a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                heal_amount = random.randrange(a1, a2 + 1)
                                print(f"Игрок получает {heal_amount} здоровья!")

                                # Добавляем частицу исцеления (зеленый цвет)
                                heal_pos = self.player.get_damage_position()
                                self.heal_emitter.add_damage(
                                    heal_pos[0],
                                    heal_pos[1],
                                    f"+{heal_amount}",
                                    False  # Можно сделать отдельный цвет для исцеления
                                )
                                # Меняем цвет на зеленый для исцеления
                                self.heal_emitter.particles[-1].color = arcade.color.LIGHT_GREEN

                                self.player.heal(heal_amount)
                                card.is_mana = True
                            else:
                                print("Недостаточно маны!")
                        else:
                            flag = 1
                            break
                    elif c == '1':
                        if self.player and self.current_slime and card.is_playable:
                            print(f"Тратится {card.dict['mana']} маны на магию!")
                            if self.player.use_mana(card.dict['mana']) or card.is_mana:
                                print("Мана успешно потрачена!")
                                if self.player and self.current_slime and self.current_slime.is_alive:
                                    a1, a2 = card.dict['damage'][card.dict['colvo'].index(c)]
                                    damage = random.randrange(a1, a2 + 1)
                                    self.attack_mob(damage, self.current_slime)
                                    card.is_mana = True
                            else:
                                print("Недостаточно маны!")
                        else:
                            flag = 1
                            break
                    elif "рандом" in c:
                        if self.player and self.current_slime and card.is_playable and "рандом" in c:
                            print(f"Тратится {card.dict['mana']} маны на магию!")
                            if self.player.use_mana(card.dict['mana']) or card.is_mana:
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
                                print("Недостаточно маны!")
                        else:
                            flag = 1
                            break
                    elif c == 'все':
                        if self.player and card.is_playable and c == 'все' and len(self.mobs) != 0:
                            print(f"Тратится {card.dict['mana']} маны на магию!")
                            if self.player.use_mana(card.dict['mana']) or card.is_mana:
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
                                print("Недостаточно маны!")
                        else:
                            flag = 1
                            break
                if len(self.deaded) > 0:
                    for mob in self.deaded:
                        self.mobs.remove(mob)
                if flag == 0:
                    card.is_playable = False
                    card.is_mana = False

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
            self.coloda.remove(card)
        self.cards = []
        self.is_player_turn = False
        self.enemy_turn()

    def new_turn(self):
        self.turn_number += 1
        self.create_cards_on_table()

    def enemy_turn(self):
        """Ход врагов с визуальным эффектом"""
        enemies = [mob for mob in self.mobs if mob.is_alive]
        if enemies:
            for enemy in enemies:
                damage = enemy.attack()
                print(f"{enemy.name} атакует игрока на {damage} урона!")

                # Добавляем частицу урона игроку
                damage_pos = self.player.get_damage_position()
                self.damage_emitter.add_damage(
                    damage_pos[0],
                    damage_pos[1],
                    damage
                )

                self.player.take_damage(damage)
                if self.player.current_hp <= 0:
                    print("Игрок повержен! Показываем экран смерти.")

                    # Создаем и показываем экран смерти
                    death_screen = DeathScreenView()
                    # Восстанавливаем размер окна
                    self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
                    self.window.show_view(death_screen)
                    return

            self.is_player_turn = True
            self.new_turn()
        else:
            print("Все противники повержены!")
            # Добавляем сообщение о победе
            victory_pos = (self.width // 2, self.height // 2)
            self.heal_emitter.add_damage(
                victory_pos[0],
                victory_pos[1],
                "ПОБЕДА!",
                True
            )
            # Меняем цвет на золотой для сообщения о победе
            self.heal_emitter.particles[-1].color = arcade.color.GOLD

            # Возвращаемся в основную игру
            x, y = self.coords
            game_view = GameView(x, y)
            self.window.set_size(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.window.show_view(game_view)


# --- Класс меню ---
class MenuView(arcade.View):
    """Класс для экрана меню"""

    def __init__(self, background_texture=None):
        global DUNGEON_MAP
        global dun
        super().__init__()

        dung = random_dun()
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
            text="Настройки",
            color=arcade.color.DARK_BLUE_GRAY,
            hover_color=arcade.color.LIGHT_BLUE
        )

        button3 = Button(
            x=self.window.width // 2,
            y=self.window.height * 0.4,
            width=300,
            height=60,
            text="Выход",
            color=arcade.color.DARK_RED,
            hover_color=arcade.color.RED
        )

        self.buttons = [button1, button2, button3]

    def on_show(self):
        """Вызывается при показе этого вида"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        """Отрисовка меню"""
        self.clear()

        # Рисуем фон
        if self.background_texture:
            arcade.draw_texture_rect(self.background_texture,
                                     arcade.rect.XYWH(self.window.width // 2,
                                                      self.window.height // 2,
                                                      self.window.width,
                                                      self.window.height)
                                     )
        else:
            # Градиентный фон, если нет текстуры
            pass
            '''arcade.draw_lrbt_rectangle_filled(
                0, self.window.width,
                0, self.window.height,
                [
                    (0, 50, 100, 255),  # Темно-синий сверху
                    (30, 30, 60, 255),  # Темно-фиолетовый снизу
                ]
            )'''

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
                        game_view = GameView(x, y)
                        self.window.show_view(game_view)

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
        background_texture = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")
    except:
        pass

    menu_view = MenuView(background_texture)
    window.show_view(menu_view)

    arcade.run()


if __name__ == "__main__":
    main()
