import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Проверяем всех котов
c.execute('SELECT name, personality, story, activity_level FROM cats ORDER BY name')
rows = c.fetchall()

print('='*70)
print('ПРОВЕРКА ВСЕХ КОТОВ')
print('='*70)

for row in rows:
    name = row[0]
    personality = row[1] if row[1] else '❌ НЕТ ДАННЫХ'
    story = '✅ ЕСТЬ' if row[2] else '❌ НЕТ'
    activity = row[3] if row[3] else '❌ НЕТ'
    
    status = '✅' if row[1] and row[2] and row[3] else '⚠️'
    
    print(f'{status} {name}:')
    print(f'     Характер: {personality[:50]}...' if len(personality) > 50 else f'     Характер: {personality}')
    print(f'     История: {story}')
    print(f'     Активность: {activity[:50]}...' if len(str(activity)) > 50 else f'     Активность: {activity}')
    print()

conn.close()