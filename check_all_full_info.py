import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Проверяем всех котов
c.execute('SELECT name, kids_friendly, cats_friendly, dogs_friendly, favorite_place FROM cats ORDER BY name')
rows = c.fetchall()

print('='*70)
print('ПОЛНАЯ ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ДЛЯ ВСЕХ КОТОВ')
print('='*70)

for row in rows:
    name = row[0]
    kids = '✅ Да' if row[1] else '❌ Нет'
    cats = '✅ Да' if row[2] else '❌ Нет'
    dogs = '✅ Да' if row[3] else '❌ Нет'
    place = row[4] if row[4] else '❌ Нет данных'
    
    print(f'\n🐱 {name}:')
    print(f'   👶 Дети: {kids}')
    print(f'   🐱 Другие кошки: {cats}')
    print(f'   🐕 Собаки: {dogs}')
    print(f'   📍 Любимое место: {place}')

conn.close()