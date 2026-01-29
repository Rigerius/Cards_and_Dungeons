import sqlite3
from dungeon_1 import dun_250

for i in range(len(dun_250)):
    dun_250[i] = '/'.join(dun_250[i])
dun = '|'.join(dun_250)

con = sqlite3.connect('database/database.db')
cur = con.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS Dungeons('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'name TEXT NOT NULL,'
            'list TEXT NOT NULL,'
            'start TEXT NOT NULL)')
"""cur.execute('INSERT INTO Dungeons(name, list, start) VALUES (?, ?, ?)', ('dungeon_1', dun, '125, 1'))"""
cur.execute('CREATE TABLE IF NOT EXISTS Cards('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'name TEXT NOT NULL,'
            'desc TEXT NOT NULL,'
            'image TEXT NOT NULL,'
            'damage TEXT NOT NULL,'
            'colvo TEXT NOT NULL,'
            'effects TEXT NOT NULL,'
            'chance TEXT NOT NULL)')
cur.execute('CREATE TABLE IF NOT EXISTS CurrentColoda('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'name TEXT NOT NULL)')
cur.execute('CREATE TABLE IF NOT EXISTS CardsList('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'name TEXT NOT NULL)')
cur.execute('CREATE TABLE IF NOT EXISTS History('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'time TEXT NOT NULL,'
            'result INTEGER NOT NULL)')
con.commit()
