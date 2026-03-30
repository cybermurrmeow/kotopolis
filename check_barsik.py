import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

c.execute('SELECT name, personality, activity_level, vocal FROM cats WHERE name="Барсик"')
row = c.fetchone()

if row:
    print(f'Барсик:')
    print(f'  personality: {row[1] if row[1] else "(пусто)"}')
    print(f'  activity_level: {row[2] if row[2] else "(пусто)"}')
    print(f'  vocal: {row[3] if row[3] else "(пусто)"}')
else:
    print('Кот не найден')

conn.close()