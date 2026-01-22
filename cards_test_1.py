import sqlite3

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