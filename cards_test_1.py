import sqlite3
import random
import os


def init_database():
    """Инициализация базы данных, создание таблицы CurrentColoda если её нет"""
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    # Создаем таблицу CurrentColoda, если она не существует
    cur.execute('''
        CREATE TABLE IF NOT EXISTS CurrentColoda (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')

    con.commit()
    con.close()


def create_card(id):
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    result = cur.execute('''SELECT * FROM Cards WHERE id = ?''', (id,)).fetchone()

    if not result:
        con.close()
        return None

    dict = {
        'id': result[0],
        'name': result[1],
        'mana': result[2],
        'description': result[3],
        'image': result[4],
        'damage': [[int(j) for j in i.split(', ')] for i in result[5].split('/')],
        'colvo': result[6].split('/'),
        'effects': result[7],
        'chance': result[8]
    }
    con.close()
    return dict


def get_all_cards():
    """Получить все карты из базы данных"""
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    results = cur.execute('''SELECT * FROM Cards''').fetchall()
    con.close()

    cards = []
    for result in results:
        card = {
            'id': result[0],
            'name': result[1],
            'mana': result[2],
            'description': result[3],
            'image': result[4],
            'damage': [[int(j) for j in i.split(', ')] for i in result[5].split('/')],
            'colvo': result[6].split('/'),
            'effects': result[7],
            'chance': result[8]
        }
        cards.append(card)

    return cards


def update_current_coloda(card_ids):
    """Обновить текущую колоду заданными картами"""
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    # Очищаем текущую колоду
    cur.execute('''DELETE FROM CurrentColoda''')

    # Добавляем новые карты
    for card_id in card_ids:
        card_data = cur.execute('''SELECT name FROM Cards WHERE id = ?''', (card_id,)).fetchone()
        if card_data:
            cur.execute('''INSERT INTO CurrentColoda (id, name) VALUES (?, ?)''',
                        (card_id, card_data[0]))

    con.commit()
    con.close()
    print(f"Колода обновлена. Добавлено {len(card_ids)} карт.")


def CurrentColoda():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    # Проверяем, есть ли карты в CurrentColoda
    card_ids = [i[0] for i in cur.execute('''SELECT id FROM CurrentColoda''').fetchall()]
    con.close()

    # Создаем объекты карт
    coloda = []
    for card_id in card_ids:
        card = create_card(card_id)
        if card:
            coloda.append(card)

    return coloda


def get_current_coloda_count():
    """Получить количество карт в текущей колоде"""
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    count = cur.execute('''SELECT COUNT(*) FROM CurrentColoda''').fetchone()[0]
    con.close()

    return count


def get_cards_by_element(element_type):
    """Получить карты определенного типа (стихии)"""
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()

    # Определяем диапазон ID для каждой стихии (по 10 карт на стихию)
    element_ranges = {
        'fire': (1, 10),
        'water': (11, 20),
        'stone': (21, 30),
        'wind': (31, 40),
        'lightning': (41, 50),
        'light': (51, 60),
        'dark': (61, 70)
    }

    if element_type in element_ranges:
        start_id, end_id = element_ranges[element_type]
        results = cur.execute('''SELECT * FROM Cards WHERE id BETWEEN ? AND ? ORDER BY id''',
                              (start_id, end_id)).fetchall()
    else:
        # Если стихия не указана, возвращаем все карты
        results = cur.execute('''SELECT * FROM Cards ORDER BY id''').fetchall()

    con.close()

    cards = []
    for result in results:
        card = {
            'id': result[0],
            'name': result[1],
            'mana': result[2],
            'description': result[3],
            'image': result[4],
            'damage': [[int(j) for j in i.split(', ')] for i in result[5].split('/')],
            'colvo': result[6].split('/'),
            'effects': result[7],
            'chance': result[8]
        }
        cards.append(card)

    return cards


def get_element_name(element_id):
    elements = {
        0: 'fire',
        1: 'water',
        2: 'stone',
        3: 'wind',
        4: 'lightning',
        5: 'light',
        6: 'dark'
    }
    return elements.get(element_id, 'unknown')


def get_element_display_name(element_id):
    """Получить отображаемое название стихии"""
    display_names = {
        0: 'ОГОНЬ',
        1: 'ВОДА',
        2: 'КАМЕНЬ',
        3: 'ВЕТЕР',
        4: 'МОЛНИЯ',
        5: "СВЕТ",
        6: "ТЬМА"
    }
    return display_names.get(element_id, 'НЕИЗВЕСТНО')


def start_coloda():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    coloda_list = [i[0] for i in cur.execute('''SELECT name FROM CardsList''').fetchall()]
    card = 'Снаряд пламени'
    card_id = None
    while card in coloda_list:
        id = random.randint(0, 69)
        card_id, card = cur.execute('''SELECT id, name FROM Cards WHERE id = ?''', (id,)).fetchone()
    cur.execute('''INSERT INTO CardsList (id, name) VALUES (?, ?)''', (card_id, card))
    con.commit()


def init_current_coloda():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    coloda_list = [i for i in cur.execute('''SELECT id, name FROM CardsList''').fetchall()]
    cur.execute('''DELETE FROM CurrentColoda''')
    for i in coloda_list:
        cur.execute('''INSERT INTO CurrentColoda (id, name) VALUES (?, ?)''', (i[0], i[1]))
    con.commit()


def cards_list():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    card_ids = [i[0] for i in cur.execute('''SELECT id FROM CardsList''').fetchall()]
    con.close()
    coloda = []
    for card_id in card_ids:
        card = create_card(card_id)
        if card:
            coloda.append(card)

    return coloda


def get_new_card():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    all_cards = get_all_cards()
    cards = cards_list()
    result = [i for i in all_cards if i not in cards]
    card = random.choice(result)
    cur.execute('''INSERT INTO CardsList (id, name) VALUES (?, ?)''', (card['id'], card['name']))
    con.commit()
    return card


def save_result(time, win):
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    cur.execute('''INSERT INTO History (time, result) VALUES (?, ?)''', (time, win))
    con.commit()


def history_info():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    all_battles = len(cur.execute('''SELECT id FROM History''').fetchall())
    top = cur.execute('''SELECT * FROM History WHERE result = ?''', (1, )).fetchall()
    return all_battles, top
