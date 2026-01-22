from dungeon_1 import dun_250
from dungeon_2 import dun_2
import sqlite3
import random

def random_dun():
    con = sqlite3.connect('database/database.db')
    cur = con.cursor()
    rand = random.choice([i[0] for i in cur.execute('''SELECT id FROM Dungeons''').fetchall()])
    dun = [i.split('/') for i in cur.execute('''SELECT list FROM Dungeons WHERE id = ?''', (rand,)).fetchone()[0].split('|')]
    start = tuple([int(i) for i in cur.execute('''SELECT start FROM Dungeons WHERE id = ?''', (rand,)).fetchone()[0].split(', ')])
    name = cur.execute('''SELECT name FROM Dungeons WHERE id = ?''', (rand,)).fetchone()[0]
    return {
        'name': name,
        'dungeon': dun,
        'start': start
    }