import sqlite3
import os


class CardDatabase:
    """Класс для работы с базой данных карт"""

    def __init__(self, db_name="card_game.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print(f"Подключено к базе данных: {self.db_name}")

    def disconnect(self):
        """Отключение от базы данных"""
        if self.conn:
            self.conn.close()
            print("Отключено от базы данных")

    def create_tables(self):
        """Создание таблиц в базе данных"""
        if not self.conn:
            self.connect()

        # Таблица карт
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                card_color TEXT,
                hover_color TEXT,
                text_color TEXT,
                damage INTEGER DEFAULT 0,
                healing INTEGER DEFAULT 0,
                mana_cost INTEGER DEFAULT 0,
                card_type TEXT CHECK(card_type IN ('attack', 'magic', 'defense', 'heal', 'special')),
                is_active BOOLEAN DEFAULT 1
            )
        ''')

        # Таблица мобов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mob_type TEXT CHECK(mob_type IN ('slime', 'goblin', 'skeleton', 'boss')),
                max_hp INTEGER DEFAULT 100,
                damage INTEGER DEFAULT 5,
                image_path TEXT,
                color TEXT,
                width INTEGER DEFAULT 150,
                height INTEGER DEFAULT 150
            )
        ''')

        # Таблица типов слизней
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS slime_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL,
                display_name TEXT NOT NULL,
                max_hp INTEGER DEFAULT 100,
                damage INTEGER DEFAULT 5,
                width INTEGER DEFAULT 20,
                height INTEGER DEFAULT 20,
                color TEXT,
                image_path TEXT
            )
        ''')

        # Таблица игроков
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                max_hp INTEGER DEFAULT 100,
                max_mana INTEGER DEFAULT 10,
                image_path TEXT,
                heart_x INTEGER DEFAULT 80,
                heart_y INTEGER DEFAULT 520,
                heart_size INTEGER DEFAULT 90
            )
        ''')

        self.conn.commit()
        print("Таблицы созданы успешно")

    def insert_default_data(self):
        """Вставка стандартных данных в таблицы"""

        # Вставляем данные о типах слизней
        slime_types = [
            ("small", "Маленький Слизень", 100, 5, 40 * 1.5, 40 * 1.5, "LIGHT_GREEN",
             "C:\\Users\\Nick\\PycharmProjects\\Arcade\\images\\Texture2D\\d698f9a99f259aab12272f50fde01438-no-bg-preview (carve.photos).png"),
            ("medium", "Средний Слизень", 150, 6, 35 * 3, 35 * 3, "GREEN",
             "C:\\Users\\Nick\\PycharmProjects\\Arcade\\images\\Texture2D\\d698f9a99f259aab12272f50fde01438-no-bg-preview (carve.photos).png"),
            ("large", "Большой Слизень", 200, 7, 50 * 2 * 1.5, 50 * 2 * 1.5, "DARK_GREEN",
             "C:\\Users\\Nick\\PycharmProjects\\Arcade\\images\\Texture2D\\d698f9a99f259aab12272f50fde01438-no-bg-preview (carve.photos).png")
        ]

        for slime_type in slime_types:
            self.cursor.execute('''
                INSERT OR IGNORE INTO slime_types 
                (type_name, display_name, max_hp, damage, width, height, color, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', slime_type)

        # Вставляем данные о картах
        cards = [
            ("Атака", "Стандартная карта /для обычных действий", None, "LIGHT_GRAY", "LIGHT_YELLOW", "BLACK",
             10, 0, 0, "attack"),
            ("Магия", "Магическая карта с /волшебным эффектом", None, "LAVENDER", "LIGHT_YELLOW", "BLACK",
             0, 0, 2, "magic"),
            ("Защита", "Боевая карта для /атаки врагов", None, "LIGHT_SALMON", "LIGHT_YELLOW", "BLACK",
             8, 0, 0, "defense"),
            ("Исцеление", "Защитная карта для /усиления обороны", None, "LIGHT_BLUE", "LIGHT_YELLOW", "BLACK",
             0, 20, 1, "heal"),
            ("Особое", "Особая карта с /уникальным эффектом", None, "LIGHT_GREEN", "LIGHT_YELLOW", "BLACK",
             5, 5, 1, "special")
        ]

        for card in cards:
            self.cursor.execute('''
                INSERT OR IGNORE INTO cards 
                (name, description, image_path, card_color, hover_color, text_color, damage, healing, mana_cost, card_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', card)

        # Вставляем данные об игроке
        player_data = (
            "Игрок",
            100,
            10,
            "C:\\Users\\Nick\\PycharmProjects\\Arcade\\images\\Texture2D\\2bf5c84fa9cb086c5535bba6d3aa5b7a.png",
            80,
            520,
            90
        )

        self.cursor.execute('''
            INSERT OR IGNORE INTO players 
            (name, max_hp, max_mana, image_path, heart_x, heart_y, heart_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', player_data)

        self.conn.commit()
        print("Стандартные данные добавлены")

    def get_all_cards(self):
        """Получение всех карт из базы данных"""
        self.cursor.execute('SELECT * FROM cards WHERE is_active = 1')
        return self.cursor.fetchall()

    def get_card_by_name(self, name):
        """Получение карты по имени"""
        self.cursor.execute('SELECT * FROM cards WHERE name = ? AND is_active = 1', (name,))
        return self.cursor.fetchone()

    def get_slime_types(self):
        """Получение всех типов слизней"""
        self.cursor.execute('SELECT * FROM slime_types')
        return self.cursor.fetchall()

    def get_slime_by_type(self, type_name):
        """Получение типа слизня по названию типа"""
        self.cursor.execute('SELECT * FROM slime_types WHERE type_name = ?', (type_name,))
        return self.cursor.fetchone()

    def get_player_data(self):
        """Получение данных игрока"""
        self.cursor.execute('SELECT * FROM players LIMIT 1')
        return self.cursor.fetchone()

    def add_card(self, name, description, image_path=None, card_color="WHITE",
                 hover_color="LIGHT_GRAY", text_color="BLACK", damage=0,
                 healing=0, mana_cost=0, card_type="attack"):
        """Добавление новой карты в базу данных"""
        self.cursor.execute('''
            INSERT INTO cards 
            (name, description, image_path, card_color, hover_color, text_color, 
             damage, healing, mana_cost, card_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, image_path, card_color, hover_color, text_color,
              damage, healing, mana_cost, card_type))
        self.conn.commit()
        print(f"Карта '{name}' добавлена в базу данных")
        return self.cursor.lastrowid

    def update_card(self, card_id, **kwargs):
        """Обновление карты в базе данных"""
        if not kwargs:
            return False

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(card_id)

        query = f"UPDATE cards SET {set_clause} WHERE id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
        print(f"Карта ID {card_id} обновлена")
        return True

    def delete_card(self, card_id):
        """Удаление карты из базы данных"""
        self.cursor.execute('UPDATE cards SET is_active = 0 WHERE id = ?', (card_id,))
        self.conn.commit()
        print(f"Карта ID {card_id} удалена (деактивирована)")
        return True

    def get_card_stats(self):
        """Получение статистики по картам"""
        self.cursor.execute('''
            SELECT card_type, COUNT(*) as count, 
                   SUM(damage) as total_damage, 
                   SUM(healing) as total_healing,
                   SUM(mana_cost) as total_mana_cost
            FROM cards 
            WHERE is_active = 1
            GROUP BY card_type
        ''')
        return self.cursor.fetchall()

    def __del__(self):
        """Деструктор для закрытия соединения"""
        self.disconnect()


# Функции для удобства работы с базой данных
def init_database():
    """Инициализация базы данных"""
    db = CardDatabase()
    db.connect()
    db.create_tables()
    db.insert_default_data()
    db.disconnect()
    return db


def get_card_data_from_db():
    """Получение данных карт из базы данных"""
    db = CardDatabase()
    db.connect()
    cards = db.get_all_cards()
    db.disconnect()
    return cards


def get_slime_data_from_db():
    """Получение данных о слизнях из базы данных"""
    db = CardDatabase()
    db.connect()
    slimes = db.get_slime_types()
    db.disconnect()
    return slimes


def get_player_data_from_db():
    """Получение данных игрока из базы данных"""
    db = CardDatabase()
    db.connect()
    player = db.get_player_data()
    db.disconnect()
    return player