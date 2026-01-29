import arcade
import random
from cards_test_1 import *

SCREEN_WIDTH, SCREEN_HEIGHT = int(800 * 1.28), int(600 * 1.28)
TITLE = "Карточная игра"
const = 1.28

class Card:
    """Класс для представления игровой карты с выдвигающимся эффектом"""

    def __init__(self, x, y, width, height, text,
                 image_path=None,
                 description="",
                 card_color=arcade.color.WHITE,
                 hover_color=arcade.color.LIGHT_GRAY,
                 text_color=arcade.color.BLACK,
                 description_color=arcade.color.DARK_GRAY,
                 font_size=14,
                 description_font_size=7,
                 dict=None):

        # Координаты и размеры
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.image_path = image_path
        self.description = description
        self.card_color = card_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.description_color = description_color
        self.font_size = font_size
        self.description_font_size = description_font_size
        self.dict = dict

        # Параметры для анимации выдвижения
        self.normal_y = y  # Обычная позиция карты (внизу)
        self.hover_y = y + 50  # Позиция при наведении (выдвигается вверх)
        self.current_y = y  # Текущая позиция карты
        self.animation_speed = 15  # Скорость анимации

        # Высота видимой части в обычном состоянии (как верх карты)
        self.visible_height = height * 0.2  # 20% высоты карты - выглядит как верх карты

        # Загружаем изображение если путь указан
        self.image = None
        if image_path:
            try:
                self.image = arcade.load_texture(image_path)
            except Exception as e:
                print(f"Не удалось загрузить изображение {image_path}: {e}")
                self.image = None

        # Вычисляем позиции для элементов карты
        self.card_top = self.y + self.height / 2
        self.card_bottom = self.y - self.height / 2

        # Позиция для изображения (80x80 пикселей в центре карты)
        self.image_size = 80
        self.image_y = self.current_y  # Будет обновляться

        # Позиция для названия (вверху карты при раскрытии, в центре видимой части в сложенном состоянии)
        self.title_y_collapsed = self.current_y + 3  # Центр видимой части
        self.title_y_expanded = self.current_y + self.height / 2 + 30  # Верх карты
        self.current_title_y = self.title_y_collapsed

        # Позиция для описания (внизу карты)
        self.description_y = self.current_y + 30

        # Создаем текстовый объект для названия
        self.text_obj = []
        for p, t in enumerate(self.text.split('/')):
            self.text_obj.append(arcade.Text(
                t,
                self.x,
                self.current_title_y + 7 - 14 * p,
                text_color,
                font_size,
                anchor_x="center",
                anchor_y="center",
                bold=True
            ))

        # Создаем текстовый объект для описания
        self.desc = []
        for p, i in enumerate(description.split('/')):
            self.desc.append(arcade.Text(
                i, self.x - 60,
                self.description_y + 100 - p * 12,
                description_color, description_font_size,
                width * 0.8
            ))

        # Свойства карты
        self.is_active = True
        self.is_playable = True
        self.is_visible = True
        self.is_hovered = False
        self.is_pressed = False
        self.is_mana = False

        # Обновляем прямоугольник для коллизий (только для видимой части)
        self.rect = arcade.rect.XYWH(x, self.current_y, width, self.visible_height)

    def update(self):
        """Обновление анимации карты"""
        # Анимируем движение карты вверх/вниз
        if self.is_hovered:
            # Плавно двигаемся к hover_y
            if self.current_y < self.hover_y:
                self.current_y += self.animation_speed
                if self.current_y > self.hover_y:
                    self.current_y = self.hover_y
            # Плавно перемещаем название наверх
            if self.current_title_y < self.title_y_expanded:
                self.current_title_y += self.animation_speed
                if self.current_title_y > self.title_y_expanded:
                    self.current_title_y = self.title_y_expanded
        else:
            # Плавно возвращаемся к normal_y
            if self.current_y > self.normal_y:
                self.current_y -= self.animation_speed
                if self.current_y < self.normal_y:
                    self.current_y = self.normal_y
            # Плавно возвращаем название в центр
            if self.current_title_y > self.title_y_collapsed:
                self.current_title_y -= self.animation_speed
                if self.current_title_y < self.title_y_collapsed:
                    self.current_title_y = self.title_y_collapsed

        # Обновляем позицию прямоугольника для коллизий
        self.rect = arcade.rect.XYWH(self.x, self.current_y, self.width,
                                     self.visible_height if not self.is_hovered else self.height)

        # Обновляем позиции текстовых объектов
        for p, i in enumerate(self.text_obj):
            i.y = self.current_title_y + 7 - p * 14
        for p, i in enumerate(self.desc):
            i.y = self.current_y - 7 - p * 12

    def draw(self):
        """Отрисовывает карту с учетом состояния"""
        if not self.is_visible or not self.is_active:
            return

        # Определяем цвет фона карты
        if self.is_pressed:
            current_color = arcade.color.DARK_GRAY
        elif self.is_hovered and self.is_playable:
            current_color = self.hover_color
        else:
            current_color = self.card_color

        # Рисуем карту с учетом текущей высоты
        if self.is_hovered:
            # Создаем прямоугольник для карты
            card_rect = arcade.rect.XYWH(self.x, self.current_y, self.width, self.height)

            # Если наведено - рисуем полную карту
            arcade.draw_rect_filled(card_rect, current_color)

            # Рисуем рамку карты
            border_color = arcade.color.BLACK
            if not self.is_playable:
                border_color = arcade.color.DARK_GRAY
            arcade.draw_rect_outline(card_rect, border_color, border_width=3)

            # Рисуем изображение 80x80 если оно есть
            if self.image:
                try:
                    # Создаем прямоугольник для изображения с центром над картой
                    image_rect = arcade.rect.XYWH(
                        self.x - 20,
                        self.current_y + 40,
                        self.image_size,
                        self.image_size
                    )
                    arcade.draw_texture_rect(self.image, image_rect)

                except Exception as e:
                    # Обработка ошибки загрузки изображения
                    print(f"Ошибка при отрисовке изображения карты: {e}")
                except:
                    # Если не удалось отрисовать изображение, рисуем заполнитель
                    self._draw_placeholder_image(True)
            else:
                # Рисуем заполнитель для пустой карты
                self._draw_placeholder_image(True)

            try:
                mana_color = arcade.color.BLUE if not self.is_playable else arcade.color.DARK_BLUE
                arcade.draw_text(
                    f"⚡{self.dict['mana']}",
                    self.x + 30,
                    self.current_y + 40,
                    mana_color,
                    10,  # Уменьшенный размер
                    anchor_x="center",
                    anchor_y="center",
                    bold=True
                )
            except:
                print('Ошибка в мане карты')

            # Рисуем описание карты
            for i in self.desc:
                i.draw()

        else:
            # Если не наведено - рисуем только верхнюю часть (как верх карты)
            # Создаем прямоугольник для видимой части карты
            visible_rect = arcade.rect.XYWH(self.x, self.current_y, self.width, self.visible_height)

            # Рисуем заливку видимой части
            arcade.draw_rect_filled(visible_rect, current_color)

            # Рисуем рамку только для видимой части
            border_color = arcade.color.BLACK
            if not self.is_playable:
                border_color = arcade.color.DARK_GRAY
            arcade.draw_rect_outline(visible_rect, border_color, border_width=2)

        # Рисуем название карты (всегда видно, но позиция меняется)
        for i in self.text_obj:
            i.draw()

        # Показываем статус "неиграбельной" карты
        if not self.is_playable and self.is_hovered:
            arcade.draw_text(
                "НЕДОСТУПНО",
                self.x,
                self.current_y,
                arcade.color.RED,
                14,
                anchor_x="center",
                anchor_y="center",
                bold=True
            )

    def _draw_placeholder_image(self, is_hovered=False):
        """Рисует заполнитель для изображения карты"""
        if not is_hovered:
            return

        # Рисуем квадрат для изображения
        image_rect = arcade.rect.XYWH(self.x - 20, self.current_y + 40, self.image_size - 20, self.image_size - 20)

        # Рисуем заливку квадрата
        arcade.draw_rect_filled(image_rect, arcade.color.LIGHT_BLUE)

        # Рисуем рамку квадрата
        arcade.draw_rect_outline(image_rect, arcade.color.BLUE, border_width=2)

        # Рисуем текст "Изображение"
        arcade.draw_text(
            "Изобр.",
            self.x - 20,
            self.current_y + 30,
            arcade.color.BLACK,
            10,
            anchor_x="center",
            anchor_y="center"
        )

    def check_mouse_hover(self, x, y):
        """Проверяет, наведен ли курсор на карту"""
        self.is_hovered = (
                self.is_visible and
                self.rect.left <= x <= self.rect.right and
                self.rect.bottom <= y <= self.rect.top
        )
        return self.is_hovered

    def update_description(self, new_description):
        """Обновляет описание карты"""
        self.description = new_description
        # Обновляем список текстовых объектов
        self.desc = [
            arcade.Text(i, self.x - 60, self.description_y + 100 - p * 12, self.description_color, self.description_font_size,
                        self.width * 0.8)
            for p, i in enumerate(new_description.split('/'))]

    def set_playable(self, playable):
        """Устанавливает, можно ли играть эту карту"""
        self.is_playable = playable

    def on_press(self):
        """Вызывается при нажатии на кнопку"""
        if self.is_visible and self.is_hovered:
            self.is_pressed = True
            return True
        return False

    def on_release(self):
        """Вызывается при отпускании кнопки"""
        if self.is_pressed:
            self.is_pressed = False
            return True
        return False


class Mob:
    """Базовый класс для всех мобов"""

    def __init__(self, name, image_path, max_hp, damage, x, y, width=150, height=150):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.damage = damage
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.current = 0
        self.last_damage_position = (x, y)
        self.is_stunned = False
        self.is_blinded = False
        self.is_slowed = 0

        # Загрузка изображения моба
        self.image = None
        if image_path:
            try:
                self.image = arcade.load_texture(image_path)
            except Exception as e:
                print(f"Не удалось загрузить изображение моба {name}: {e}")
                self.image = None

        # Флаг живой/мертвый
        self.is_alive = True

        # Цвет для разных типов
        self.color = arcade.color.GREEN

    def draw(self):
        """Отрисовка моба"""
        if not self.is_alive:
            return

        # Рисуем изображение моба если оно есть
        if self.image:
            try:
                mob_rect = arcade.rect.XYWH(
                    self.x,
                    self.y,
                    self.width,
                    self.height
                )
                arcade.draw_texture_rect(self.image, mob_rect)
            except:
                # Если не удалось отрисовать изображение, рисуем цветной прямоугольник
                self.draw_placeholder()
        else:
            # Рисуем заполнитель
            self.draw_placeholder()

        # Рисуем полоску здоровья над мобом
        self.draw_health_bar()

        # Рисуем имя моба под ним
        self.draw_name()

    def draw_placeholder(self):
        """Запасное отображение если нет изображения"""
        # Основной прямоугольник
        mob_rect = arcade.rect.XYWH(
            self.x,
            self.y,
            self.width * 0.8,
            self.height * 0.8
        )
        arcade.draw_rect_filled(mob_rect, self.color)

        # Рамка
        arcade.draw_rect_outline(mob_rect, arcade.color.BLACK, border_width=2)

        # Текст с именем внутри
        arcade.draw_text(
            self.name[:3],  # Первые 3 буквы имени
            self.x,
            self.y,
            arcade.color.BLACK,
            16,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def draw_health_bar(self):
        """Отрисовка полоски здоровья над мобом"""
        bar_width = self.width * 1.5  # Увеличиваем ширину полоски для маленьких слизней
        bar_height = 6
        bar_x = self.x
        bar_y = self.y + self.height // 2 + 10  # Ближе к слизню

        # Фон полоски (красный)
        bg_rect = arcade.rect.XYWH(
            bar_x,
            bar_y,
            bar_width,
            bar_height
        )
        arcade.draw_rect_filled(bg_rect, arcade.color.DARK_RED)

        # Текущее здоровье (зеленое)
        hp_percent = self.current_hp / self.max_hp
        current_width = bar_width * hp_percent

        hp_rect = arcade.rect.XYWH(
            bar_x - (bar_width - current_width) / 2,  # Выравнивание слева
            bar_y,
            current_width,
            bar_height
        )

        # Выбираем цвет в зависимости от процента HP
        if hp_percent > 0.7:
            hp_color = arcade.color.GREEN
        elif hp_percent > 0.3:
            hp_color = arcade.color.YELLOW
        else:
            hp_color = arcade.color.RED

        arcade.draw_rect_filled(hp_rect, hp_color)

        # Рамка полоски
        arcade.draw_rect_outline(bg_rect, arcade.color.BLACK, border_width=1)

        # Текст с HP
        hp_text = f"{self.current_hp}/{self.max_hp}"
        arcade.draw_text(
            hp_text,
            bar_x,
            bar_y + bar_height + 4,
            arcade.color.WHITE,
            8,  # Уменьшенный шрифт
            anchor_x="center",
            anchor_y="center"
        )

    def draw_name(self):
        """Отрисовка имени моба"""
        color = arcade.color.WHITE if self.current == 0 else arcade.color.RED
        arcade.draw_text(
            self.name,
            self.x,
            self.y - self.height // 2 - 15,
            color,
            10,  # Уменьшенный шрифт
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def take_damage(self, damage):
        """Получение урона"""
        self.current_hp -= damage
        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False
            return False  # Моб умер
        return True  # Моб выжил

    def attack(self):
        """Атака моба - возвращает урон"""
        return self.damage

    def is_dead(self):
        """Проверка, жив ли моб"""
        return not self.is_alive

    def heal(self, amount):
        """Лечение моба"""
        if self.is_alive:
            self.current_hp += amount
            if self.current_hp > self.max_hp:
                self.current_hp = self.max_hp

    def check_mouse_hover(self, x, y):
        self.is_hovered = (
                self.x - self.width // 2 <= x <= self.x + self.width // 2 and
                self.y - self.height // 2 <= y <= self.y + self.height // 2
        )
        return self.is_hovered

    def on_press(self):
        self.current = 1


class Slime(Mob):
    """Класс Слизня - наследник Mob"""

    def __init__(self, slime_type, x, y):
        # Определяем параметры в зависимости от типа слизня
        if slime_type == "small":
            name = "Маленький Слизень"
            max_hp = 100
            damage = 5
            color = arcade.color.LIGHT_GREEN
            width = 40*1.5  # 20x20 пикселей
            height = 40*1.5
        elif slime_type == "medium":
            name = "Средний Слизень"
            max_hp = 150
            damage = 6
            color = arcade.color.GREEN
            width = 35*3  # 35x35 пикселей
            height = 35*3
        elif slime_type == "large":
            name = "Большой Слизень"
            max_hp = 200
            damage = 8
            color = arcade.color.DARK_GREEN
            width = 50*2*1.5 # 50x50 пикселей
            height = 50*2*1.5
        else:
            # По умолчанию средний слизень
            name = "Слизень"
            max_hp = 150
            damage = 6
            color = arcade.color.GREEN
            width = 35
            height = 35

        # Загружаем изображение слизня
        image_path = "images/Mobs/mini_slime_1.jpg"

        # Вызываем конструктор родительского класса
        super().__init__(name, image_path, max_hp, damage, x, y, width, height)

        # Устанавливаем цвет для этого типа слизня
        self.color = color

        # Сохраняем тип для внутреннего использования
        self.slime_type = slime_type

        # Добавляем детали для отрисовки (если изображение не загрузится)
        self.eye_color = arcade.color.WHITE
        self.pupil_color = arcade.color.BLACK
        self.is_animated = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.texture_change_delay = 0.2
        self.textures = []
        self.end_animation = False
        for i in range(1, 10):
            texture = arcade.load_texture(f"images/Mobs/mini_slime_{i}.jpg")
            self.textures.append(texture)

    def draw_placeholder(self):
        """Отрисовка слизня с деталями (если изображение не загрузилось)"""
        # Тело слизня (овал)
        body_width = self.width * 0.8
        body_height = self.height * 0.6

        # Рисуем тело (овал)
        arcade.draw_ellipse_filled(
            self.x,
            self.y,
            body_width,
            body_height,
            self.color
        )

        # Рисуем контур тела
        arcade.draw_ellipse_outline(
            self.x,
            self.y,
            body_width,
            body_height,
            arcade.color.BLACK,
            1  # Более тонкая рамка
        )

        # Рисуем глаза в зависимости от размера (уменьшенные)
        eye_size = body_width * 0.15
        if self.slime_type == "small":
            # Маленький слизень - 1 глаз
            self.draw_eye(self.x, self.y + body_height * 0.1, eye_size)
        elif self.slime_type == "medium":
            # Средний слизень - 2 глаза
            self.draw_eye(self.x - body_width * 0.15, self.y + body_height * 0.1, eye_size)
            self.draw_eye(self.x + body_width * 0.15, self.y + body_height * 0.1, eye_size)
        else:
            # Большой слизень - 3 глаза
            self.draw_eye(self.x, self.y + body_height * 0.1, eye_size)
            self.draw_eye(self.x - body_width * 0.2, self.y + body_height * 0.05, eye_size)
            self.draw_eye(self.x + body_width * 0.2, self.y + body_height * 0.05, eye_size)

        # Рисуем рот
        mouth_y = self.y - body_height * 0.1
        if self.slime_type == "small":
            # Маленькая улыбка
            arcade.draw_arc_outline(
                self.x, mouth_y,
                body_width * 0.2, body_height * 0.05,
                arcade.color.BLACK,
                0, 180, 1
            )
        elif self.slime_type == "medium":
            # Нейтральный рот
            arcade.draw_line(
                self.x - body_width * 0.1, mouth_y,
                self.x + body_width * 0.1, mouth_y,
                arcade.color.BLACK, 1
            )
        else:
            # Большой открытый рот
            arcade.draw_ellipse_outline(
                self.x, mouth_y,
                body_width * 0.25, body_height * 0.1,
                arcade.color.BLACK, 1
            )

    def draw_eye(self, x, y, size):
        """Отрисовка глаза слизня (уменьшенная версия)"""
        # Белок глаза
        arcade.draw_circle_filled(x, y, size, self.eye_color)
        arcade.draw_circle_outline(x, y, size, arcade.color.BLACK, 1)

        # Зрачок
        pupil_size = size * 0.5
        arcade.draw_circle_filled(x, y, pupil_size, self.pupil_color)

        # Блик в глазу (очень маленький)
        highlight_size = pupil_size * 0.3
        arcade.draw_circle_filled(
            x - pupil_size * 0.2,
            y + pupil_size * 0.2,
            highlight_size,
            arcade.color.WHITE
        )

    def update(self, delta_time: float = 1/60):
        if self.is_animated:
            self.animation_timer += delta_time
            if self.animation_timer > self.texture_change_delay:
                self.animation_timer = 0
                self.animation_frame += 1
                if self.animation_frame >= 9:
                    self.animation_frame = 0
                    self.is_animated = False
                    self.end_animation = True
                self.image = self.textures[self.animation_frame]
        else:
            self.image = self.textures[self.animation_frame]

    def get_info(self):
        """Возвращает информацию о слизне"""
        return {
            "type": self.slime_type,
            "name": self.name,
            "hp": self.current_hp,
            "max_hp": self.max_hp,
            "damage": self.damage,
            "alive": self.is_alive
        }

    def take_damage(self, damage):
        self.last_damage_position = (self.x + random.randrange(-10, 10), self.y + random.randrange(-10, 10))
        survived = super().take_damage(damage)
        return survived

    def get_damage_position(self):
        """Возвращает позицию для отображения урона"""
        return self.last_damage_position

    def start_animation(self):
        self.is_animated = True


class Fight_player:
    """Класс для представления игрока"""

    def __init__(self, name, image_path, max_hp=100, max_mana=50):
        self.name = name
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.max_mana = max_mana
        self.current_mana = max_mana

        # Загрузка изображения игрока
        self.image = None
        if image_path:
            try:
                self.image = arcade.load_texture(image_path)
            except Exception as e:
                print(f"Не удалось загрузить изображение игрока: {e}")
                self.image = None

        # Позиция и размер изображения игрока (левый центр экрана)
        self.image_x = int(120*1.28)  # Сдвинуто левее
        self.image_y = int(300*1.28)  # Выше центра
        self.image_width = int(125*1.28)  # Увеличенный размер
        self.image_height = int(165*1.28)  # Увеличенный размер
        self.last_damage_position = (self.image_x, self.image_y)

        # Параметры для отображения здоровья (левый верхний угол)
        self.heart_x = int(80*1.28)  # Позиция сердца в левом углу
        self.heart_y = int(520*1.28)  # Вверху экрана
        self.heart_size = int(90*1.28)  # Уменьшенный на 10% (было 100)

        # Параметры для отображения маны (под сердцем в левом углу)
        self.mana_diamonds_x = self.heart_x  # Под сердцем
        self.mana_diamonds_y = self.heart_y - 85  # Ближе к сердцу
        self.diamond_size = 25
        self.diamond_spacing = 30

        # Всегда 5 ромбиков для отображения
        self.diamond_count = 5

        # Звуки ходьбы
        self.walk_sounds = []
        self.load_walk_sounds()

        # Таймер для звуков шагов
        self.walk_timer = 0
        self.walk_sound_delay = 0.3  # Задержка между шагами (секунды)

    def load_walk_sounds(self):
        """Загружает звуки ходьбы"""
        try:
            # Пробуем загрузить кастомные звуки
            sound_files = ["music\шаг0.mp3", "music\шаг0.mp3", "music\шаг0.mp3"]
            for sound_file in sound_files:
                sound = arcade.load_sound(sound_file)
                self.walk_sounds.append(sound)
            print(f"Загружено {len(self.walk_sounds)} звуков ходьбы")
        except:
            # Используем звуки из ресурсов Arcade
            print("Используем стандартные звуки шагов")
            self.walk_sounds = [
                arcade.load_sound(":resources:music\шаг0.mp3"),
                arcade.load_sound(":resources:music\шаг1.mp3"),
                arcade.load_sound(":resources:music\шаг2.mp3")
            ]

    def update_walk_sound(self, delta_time, is_moving):
        """Обновляет таймер и воспроизводит звуки шагов"""
        if is_moving:
            self.walk_timer += delta_time
            if self.walk_timer >= self.walk_sound_delay:
                self.play_walk_sound()
                self.walk_timer = 0
        else:
            self.walk_timer = 0

    def play_walk_sound(self):
        """Воспроизводит случайный звук шага"""
        if self.walk_sounds:
            sound = random.choice(self.walk_sounds)
            # Воспроизводим с небольшим случайным изменением громкости для реалистичности
            volume = random.uniform(0.3, 0.5)
            arcade.play_sound(sound, volume=volume)

    def draw(self):
        """Отрисовка игрока и его характеристик"""
        # Рисуем изображение игрока в левом центре
        self.draw_player_image()

        # Рисуем большое сердце с текущим HP в левом верхнем углу
        self.draw_big_heart()

        # Рисуем ромбы маны под сердцем в левом углу
        self.draw_mana_diamonds()

        # Рисуем имя игрока под маной
        self.draw_player_name()

    def draw_player_image(self):
        """Отрисовка изображения игрока"""
        if self.image:
            try:
                # Изображение игрока без обводки
                image_rect = arcade.rect.XYWH(
                    self.image_x,
                    self.image_y,
                    self.image_width,
                    self.image_height
                )
                arcade.draw_texture_rect(self.image, image_rect)

            except:
                # Если не удалось отрисовать изображение
                self.draw_placeholder_image()
        else:
            # Запасной вариант если нет изображения
            self.draw_placeholder_image()

    def draw_placeholder_image(self):
        """Запасное изображение если основное не загрузилось"""
        placeholder_rect = arcade.rect.XYWH(
            self.image_x,
            self.image_y,
            self.image_width * 0.9,
            self.image_height * 0.9
        )
        arcade.draw_rect_filled(placeholder_rect, (100, 100, 100, 200))
        arcade.draw_text(
            "Игрок",
            self.image_x,
            self.image_y,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def draw_big_heart(self):
        """Отрисовка большого сердца с текущим HP в левом верхнем углу"""
        # Рисуем большое красное сердце
        heart_text = "❤"

        # Сердце с красным градиентом
        arcade.draw_text(
            heart_text,
            self.heart_x,
            self.heart_y,
            arcade.color.RED,
            self.heart_size,
            anchor_x="center",
            anchor_y="center"
        )

        # Добавляем небольшую тень для объема
        arcade.draw_text(
            heart_text,
            self.heart_x - 2,
            self.heart_y - 2,
            (150, 0, 0, 150),  # Темно-красный с прозрачностью
            self.heart_size,
            anchor_x="center",
            anchor_y="center"
        )

        # Текущее HP внутри сердца (белый текст)
        hp_text = f"{self.current_hp}"

        # Определяем цвет текста в зависимости от количества HP
        if self.current_hp < 30:
            text_color = arcade.color.RED
        elif self.current_hp < 70:
            text_color = arcade.color.YELLOW
        else:
            text_color = arcade.color.WHITE

        arcade.draw_text(
            hp_text,
            self.heart_x,
            self.heart_y - 3,  # Сдвиг вниз для центрирования в сердце
            text_color,
            24,  # Уменьшенный шрифт
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def draw_mana_diamonds(self):
        """Отрисовка ромбов для маны в левом верхнем углу"""
        # Всегда рисуем 5 ромбиков
        for i in range(self.diamond_count):
            x = self.mana_diamonds_x + (i - (self.diamond_count - 1) / 2) * self.diamond_spacing

            # Рассчитываем, сколько маны представляет один ромбик
            mana_per_diamond = self.max_mana / self.diamond_count
            mana_threshold = (i + 1) * mana_per_diamond

            if self.current_mana >= mana_threshold:
                # Полностью заполненный ромбик (синий)
                arcade.draw_text(
                    "◆",
                    x,
                    self.mana_diamonds_y,
                    arcade.color.BLUE,
                    self.diamond_size,
                    anchor_x="center",
                    anchor_y="center"
                )

                # Добавляем свечение для активной маны
                arcade.draw_text(
                    "◆",
                    x,
                    self.mana_diamonds_y,
                    (100, 100, 255, 100),  # Светло-синий с прозрачностью
                    self.diamond_size + 4,
                    anchor_x="center",
                    anchor_y="center"
                )

            elif self.current_mana > i * mana_per_diamond:
                # Частично заполненный ромбик (градиент от синего к темно-синему)
                fill_percent = (self.current_mana - i * mana_per_diamond) / mana_per_diamond

                if fill_percent > 0.7:
                    diamond_color = arcade.color.BLUE
                elif fill_percent > 0.4:
                    diamond_color = (100, 100, 200)  # Средне-синий
                else:
                    diamond_color = (80, 80, 180)  # Темно-синий

                arcade.draw_text(
                    "◆",
                    x,
                    self.mana_diamonds_y,
                    diamond_color,
                    self.diamond_size,
                    anchor_x="center",
                    anchor_y="center"
                )
            else:
                # Пустой ромбик (темно-синий)
                arcade.draw_text(
                    "◇",
                    x,
                    self.mana_diamonds_y,
                    arcade.color.DARK_BLUE,
                    self.diamond_size,
                    anchor_x="center",
                    anchor_y="center"
                )

        # Числовое значение маны под ромбами
        mana_text = f"{self.current_mana}/{self.max_mana}"
        arcade.draw_text(
            mana_text,
            self.mana_diamonds_x,
            self.mana_diamonds_y - 25,
            arcade.color.LIGHT_BLUE,
            16,  # Уменьшенный шрифт
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def draw_player_name(self):
        """Отрисовка имени игрока в левом верхнем углу над сердцем"""
        arcade.draw_text(
            self.name,
            self.heart_x,
            self.heart_y + 65,  # Над сердцем
            arcade.color.GOLD,
            20,  # Уменьшенный шрифт
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def take_damage(self, damage):
        """Получение урона"""
        self.last_damage_position = (self.image_x + random.randrange(-30, 30), self.image_y + random.randrange(-30, 30))
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
        return self.current_hp > 0

    def get_damage_position(self):
        """Возвращает позицию для отображения урона"""
        self.last_damage_position = (self.image_x + random.randrange(-30, 30), self.image_y + random.randrange(-30, 30))
        return self.last_damage_position

    def heal(self, amount):
        """Лечение"""
        self.last_damage_position = (self.image_x + random.randrange(-20, 20), self.image_y + random.randrange(-20, 20))
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp

    def use_mana(self, amount):
        """Использование маны"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False

    def restore_mana(self, amount):
        """Восстановление маны"""
        self.current_mana += amount
        if self.current_mana > self.max_mana:
            self.current_mana = self.max_mana

    def set_max_mana(self, new_max):
        """Установка нового максимума маны"""
        old_max = self.max_mana
        self.max_mana = new_max

        # Сохраняем пропорциональное количество текущей маны
        if old_max > 0:
            ratio = self.current_mana / old_max
            self.current_mana = int(self.max_mana * ratio)
        else:
            self.current_mana = self.max_mana


class EndTurnButton:
    """Кнопка завершения хода"""

    def __init__(self, x, y, width=150, height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.text = "КОНЕЦ ХОДА"
        self.is_hovered = False
        self.is_pressed = False
        self.is_enabled = True

        self.hitbox = arcade.rect.XYWH(x, y, width, height)

    def draw(self):
        """Отрисовка кнопки"""
        # Цвет кнопки
        if not self.is_enabled:
            color = arcade.color.DARK_GRAY
        elif self.is_pressed:
            color = arcade.color.DARK_GREEN
        elif self.is_hovered:
            color = arcade.color.RED
        else:
            color = arcade.color.DARK_RED

        # Фон кнопки
        arcade.draw_rect_filled(self.hitbox, color)

        # Рамка
        border_color = arcade.color.GOLD if self.is_enabled else arcade.color.DARK_GRAY
        arcade.draw_rect_outline(self.hitbox, border_color, 3)

        # Текст
        arcade.draw_text(
            self.text,
            self.x,
            self.y,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

    def check_hover(self, x, y):
        """Проверка наведения мыши"""
        self.is_hovered = (
                self.hitbox.left <= x <= self.hitbox.right and
                self.hitbox.bottom <= y <= self.hitbox.top
        )
        return self.is_hovered

    def on_press(self):
        """Обработка нажатия"""
        if self.is_hovered and self.is_enabled:
            self.is_pressed = True
            return True
        return False

    def on_release(self):
        """Обработка отпускания"""
        if self.is_pressed:
            self.is_pressed = False
            return True
        return False
