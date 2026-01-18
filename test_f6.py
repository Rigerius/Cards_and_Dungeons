import arcade
import random
from my_class import Card, Slime, F_Player
from database import CardDatabase, get_card_data_from_db, get_slime_data_from_db, get_player_data_from_db

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TITLE = "Карточная игра"


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.cards = []
        self.player = None  # Объект игрока
        self.mobs = []  # Список мобов
        self.background_texture = None
        self.midground_texture = None
        self.current_slime = None  # Текущий отображаемый слизень
        self.db = CardDatabase()  # База данных
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def setup(self):
        """Настройка игры"""
        # Подключаемся к базе данных
        self.db.connect()

        # Создаем игрока с данными из базы данных
        player_data = get_player_data_from_db()
        if player_data:
            # player_data: (id, name, max_hp, max_mana, image_path, heart_x, heart_y, heart_size)
            self.player = F_Player(
                name=player_data[1],
                image_path=player_data[4] if player_data[
                    4] else "images\\Texture2D\\mag_1.png",
                max_hp=player_data[2],
                max_mana=player_data[3]
            )
        else:
            # Запасной вариант если нет данных в БД
            player_image_path = "images\\Texture2D\\mag_1.png"
            self.player = F_Player("Игрок", player_image_path, max_hp=100, max_mana=10)

        # Создаем случайного слизня при запуске
        self.create_random_slime()

        # Загрузка фоновых текстур
        try:
            self.background_texture = arcade.load_texture("images/Texture2D/Unfinished Meal Far Backgroundl.png")
            self.midground_texture = arcade.load_texture("images/Texture2D/Warrior Statue Mid Background.png")
        except:
            print("Не удалось загрузить фоновые текстуры")

        # Создаем карты на игровом столе из базы данных
        self.create_cards_from_database()

    def create_random_slime(self):
        """Создание случайного слизня"""
        # Очищаем список мобов
        self.mobs.clear()

        # Получаем данные о слизнях из базы данных
        slime_types = get_slime_data_from_db()

        if not slime_types:
            # Если нет данных в БД, используем стандартные типы
            slime_type_names = ["small", "medium", "large"]
        else:
            # Берем типы из базы данных
            slime_type_names = [slime[1] for slime in slime_types]

        # Выбираем случайный тип слизня
        random_type = random.choice(slime_type_names)

        # Создаем слизня в центре правой части экрана
        slime_x = SCREEN_WIDTH - 150
        slime_y = SCREEN_HEIGHT // 2 + 50

        # Создаем слизня
        new_slime = Slime(random_type, slime_x, slime_y)
        self.mobs.append(new_slime)
        self.current_slime = new_slime

        print(f"Создан новый слизень: {new_slime.name}")
        print(f"Размер: {new_slime.width}x{new_slime.height} пикселей")
        print(f"Здоровье: {new_slime.current_hp}/{new_slime.max_hp}")
        print(f"Урон: {new_slime.damage}")

    def create_cards_from_database(self):
        """Создает карты на игровом столе из базы данных"""
        # Параметры стола
        table_height = 150  # Высота стола

        # Параметры карт (увеличенные размеры)
        card_width = 130  # Увеличенная ширина
        card_height = 220  # Увеличенная высота
        card_spacing = 5  # Увеличенное расстояние между картами

        # Позиционируем карты внизу экрана
        bottom_margin = 20  # Отступ от нижнего края
        cards_y = bottom_margin + table_height / 2 - 80  # Позиция карт

        # Получаем карты из базы данных
        db_cards = get_card_data_from_db()

        if not db_cards:
            print("Нет карт в базе данных, создаем стандартные карты")
            self.create_default_cards()
            return

        # Вычисляем начальную позицию для первой карты
        total_cards_width = len(db_cards) * card_width + (len(db_cards) - 1) * card_spacing
        start_x = self.width // 2 - total_cards_width // 2 + card_width // 2

        # Маппинг цветов из строк в объекты arcade.color
        color_map = {
            "LIGHT_GRAY": arcade.color.LIGHT_GRAY,
            "LAVENDER": arcade.color.LAVENDER,
            "LIGHT_SALMON": arcade.color.LIGHT_SALMON,
            "LIGHT_BLUE": arcade.color.LIGHT_BLUE,
            "LIGHT_GREEN": arcade.color.LIGHT_GREEN,
            "WHITE": arcade.color.WHITE
        }

        text_color_map = {
            "BLACK": arcade.color.BLACK,
            "WHITE": arcade.color.WHITE
        }

        for i, card_data in enumerate(db_cards):
            # card_data: (id, name, description, image_path, card_color, hover_color,
            #             text_color, damage, healing, mana_cost, card_type, is_active)
            card_x = start_x + i * (card_width + card_spacing)
            card_y = cards_y

            # Получаем цвета из базы данных или используем значения по умолчанию
            card_color = color_map.get(card_data[4], arcade.color.WHITE)
            hover_color = color_map.get(card_data[5], arcade.color.LIGHT_GRAY)
            text_color = text_color_map.get(card_data[6], arcade.color.BLACK)

            # Создаем карту с данными из базы данных
            card = Card(
                x=card_x,
                y=card_y,
                width=card_width,
                height=card_height,
                text=card_data[1],  # name
                image_path=card_data[3],  # image_path
                description=card_data[2],  # description
                card_color=card_color,
                hover_color=hover_color,
                text_color=text_color,
                description_color=arcade.color.DARK_BROWN,
                font_size=14,
                description_font_size=9
            )

            # Сохраняем дополнительные данные из БД
            card.db_id = card_data[0]
            card.damage = card_data[7]
            card.healing = card_data[8]
            card.mana_cost = card_data[9]
            card.card_type = card_data[10]

            # Сделаем одну карту недоступной для демонстрации
            if i == 2:  # Третья карта будет недоступной
                card.set_playable(False)

            self.cards.append(card)

    def create_default_cards(self):
        """Создание стандартных карт если нет данных в БД"""
        # Параметры стола
        table_height = 150

        # Параметры карт
        card_width = 130
        card_height = 220
        card_spacing = 5

        # Позиционируем карты
        bottom_margin = 20
        cards_y = bottom_margin + table_height / 2 - 80

        # Стандартные карты
        descriptions = [
            "Стандартная карта /для обычных действий",
            "Магическая карта с /волшебным эффектом",
            "Боевая карта для /атаки врагов",
            "Защитная карта для /усиления обороны",
            "Особая карта с /уникальным эффектом"
        ]

        card_names = [
            "Атака",
            "Магия",
            "Защита",
            "Исцеление",
            "Особое"
        ]

        colors = [
            arcade.color.LIGHT_GRAY,
            arcade.color.LAVENDER,
            arcade.color.LIGHT_SALMON,
            arcade.color.LIGHT_BLUE,
            arcade.color.LIGHT_GREEN
        ]

        total_cards_width = 5 * card_width + 4 * card_spacing
        start_x = self.width // 2 - total_cards_width // 2 + card_width // 2

        for i in range(5):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = cards_y

            card = Card(
                x=card_x,
                y=card_y,
                width=card_width,
                height=card_height,
                text=card_names[i],
                image_path=None,
                description=descriptions[i],
                card_color=colors[i],
                hover_color=arcade.color.LIGHT_YELLOW,
                text_color=arcade.color.BLACK,
                description_color=arcade.color.DARK_BROWN,
                font_size=14,
                description_font_size=9
            )

            # Добавляем стандартные значения
            card.damage = 10 if card_names[i] == "Атака" else 0
            card.healing = 20 if card_names[i] == "Исцеление" else 0
            card.mana_cost = 2 if card_names[i] == "Магия" else 0

            if i == 2:
                card.set_playable(False)

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

        # Рисуем игровой стол (коричневый прямоугольник внизу)
        table_width = self.width * 0.9
        table_height = 150
        table_x = self.width // 2
        table_y = table_height // 2

        # Создаем прямоугольник для стола
        table_rect = arcade.rect.XYWH(table_x, table_y, table_width, table_height)

        # Основной цвет стола
        arcade.draw_rect_filled(table_rect, arcade.color.DARK_BROWN)

        # Рамка стола
        arcade.draw_rect_outline(table_rect, arcade.color.BLACK, border_width=3)

        # Рисуем игрока (в левом центре экрана)
        if self.player:
            self.player.draw()

        # Рисуем всех мобов
        for mob in self.mobs:
            mob.draw()

        # Рисуем все карты
        for card in self.cards:
            card.draw()

        # Рисуем пояснительный текст
        arcade.draw_text(
            "Наведите курсор на карту, чтобы увидеть ее полностью",
            self.width // 2,
            table_y + table_height + 15,
            arcade.color.WHITE,
            16,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Информация о мобах
        arcade.draw_text(
            "Нажмите P для создания случайного слизня",
            self.width // 2,
            SCREEN_HEIGHT - 40,
            arcade.color.LIGHT_GREEN,
            14,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )

        # Отображаем информацию о текущем слизне
        if self.current_slime:
            slime_info = f"Текущий слизень: {self.current_slime.name} ({self.current_slime.width}x{self.current_slime.height}px)"
            arcade.draw_text(
                slime_info,
                self.width // 2,
                SCREEN_HEIGHT - 70,
                arcade.color.LIGHT_BLUE,
                12,
                anchor_x="center",
                anchor_y="center"
            )

        # Информация о картах
        arcade.draw_text(
            "В сложенном виде видны только верхушки карт с названиями",
            self.width // 2,
            table_y + table_height + 40,
            arcade.color.LIGHT_GRAY,
            12,
            anchor_x="center",
            anchor_y="center"
        )

    def on_update(self, delta_time):
        """Обновление логики игры"""
        for card in self.cards:
            card.update()

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.P:
            self.create_random_slime()
            print("Нажата клавиша P - создан новый случайный слизень!")

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        for card in self.cards:
            card.check_mouse_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        for card in self.cards:
            if card.check_mouse_hover(x, y):
                card.on_press()

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания мыши"""
        for card in self.cards:
            if card.on_release():
                print(f"Нажата карта: {card.text}")
                print(f"Описание: {card.description}")
                print(f"Тип карты: {getattr(card, 'card_type', 'неизвестно')}")

                # Обработка карты в зависимости от ее типа и данных из БД
                self.handle_card_effect(card)

    def handle_card_effect(self, card):
        """Обработка эффекта карты"""
        # Проверяем, есть ли у игрока достаточно маны
        if hasattr(card, 'mana_cost') and card.mana_cost > 0:
            if not self.player.use_mana(card.mana_cost):
                print(f"Недостаточно маны! Нужно {card.mana_cost}, есть {self.player.current_mana}")
                return

        # Обработка карты "Атака"
        if card.text == "Атака" and self.player and self.current_slime and self.current_slime.is_alive:
            damage = getattr(card, 'damage', 10)
            self.attack_current_slime(damage)

        # Обработка карты "Магия"
        elif card.text == "Магия" and self.player:
            print(f"Тратится {getattr(card, 'mana_cost', 2)} маны на магию!")
            # Дополнительные эффекты магии могут быть добавлены здесь

        # Обработка карты "Исцеление"
        elif card.text == "Исцеление" and self.player:
            healing = getattr(card, 'healing', 20)
            print(f"Игрок получает {healing} здоровья!")
            self.player.heal(healing)

        # Обработка карты "Защита"
        elif card.text == "Защита" and self.player:
            print("Активирована защита!")
            # Эффекты защиты могут быть добавлены здесь

        # Обработка карты "Особое"
        elif card.text == "Особое" and self.player:
            damage = getattr(card, 'damage', 5)
            healing = getattr(card, 'healing', 5)
            print(f"Особый эффект! Наносит {damage} урона и лечит на {healing}")
            if self.current_slime and self.current_slime.is_alive:
                self.attack_current_slime(damage)
            self.player.heal(healing)

    def attack_current_slime(self, damage):
        """Атака текущего слизня"""
        if not self.current_slime or not self.current_slime.is_alive:
            print("Нет живого слизня для атаки!")
            return

        # Наносим урон
        print(f"Атакуем {self.current_slime.name} на {damage} урона!")
        survived = self.current_slime.take_damage(damage)

        if not survived:
            print(f"{self.current_slime.name} повержен!")
        else:
            print(f"{self.current_slime.name} осталось {self.current_slime.current_hp} HP")

    def __del__(self):
        """Деструктор для закрытия соединения с БД"""
        if hasattr(self, 'db'):
            self.db.disconnect()


def main():
    """Основная функция игры"""
    # Инициализируем базу данных (если нужно)
    # from database import init_database
    # init_database()

    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()