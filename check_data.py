import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Проверяем данные в новых полях
c.execute('SELECT name, personality, story, activity_level FROM cats LIMIT 3')
rows = c.fetchall()

print('Данные в новых полях:')
print('='*60)

for row in rows:
    name = row[0]
    personality = row[1] if row[1] else 'Нет данных'
    story = row[2][:50] + '...' if row[2] and len(row[2]) > 50 else (row[2] if row[2] else 'Нет данных')
    activity = row[3] if row[3] else 'Нет данных'
    
    print(f'\n🐱 {name}:')
    print(f'   Характер: {personality}')
    print(f'   История: {story}')
    print(f'   Активность: {activity}')

conn.close()