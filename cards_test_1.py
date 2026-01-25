import sqlite3
import random

def create_card(id):
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    result = cur.execute('''SELECT * FROM Cards WHERE id = ?''', (id,)).fetchone()
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
    return dict

def start_coloda():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    coloda_list = [i[0] for i in cur.execute('''SELECT name FROM CurrentColoda''').fetchall()]
    card = 'Снаряд пламени'
    card_id = None
    while card in coloda_list:
        id = random.randint(0, 49)
        card_id, card = cur.execute('''SELECT id, name FROM Cards WHERE id = ?''', (id,)).fetchone()
    print(card_id, card)
    cur.execute('''INSERT INTO CurrentColoda (id, name) VALUES (?, ?)''', (card_id, card))
    con.commit()

def CurrentColoda():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    return [create_card(id) for id in [i[0] for i in cur.execute('''SELECT id FROM CurrentColoda''').fetchall()]]