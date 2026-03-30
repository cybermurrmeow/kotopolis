import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Проверяем все дополнительные поля
c.execute('SELECT name, kids_friendly, cats_friendly, dogs_friendly, favorite_place, vocal, food_preferences, adoption_recommendation FROM cats LIMIT 5')
rows = c.fetchall()

print('='*70)
print('ПРОВЕРКА ДОПОЛНИТЕЛЬНОЙ ИНФОРМАЦИИ')
print('='*70)

for row in rows:
    name = row[0]
    kids = row[1] if row[1] is not None else 'НЕТ'
    cats = row[2] if row[2] is not None else 'НЕТ'
    dogs = row[3] if row[3] is not None else 'НЕТ'
    place = row[4] if row[4] else 'НЕТ'
    vocal = row[5] if row[5] else 'НЕТ'
    food = row[6] if row[6] else 'НЕТ'
    rec = row[7][:50] + '...' if row[7] and len(row[7]) > 50 else (row[7] if row[7] else 'НЕТ')
    
    print(f'\n🐱 {name}:')
    print(f'   kids_friendly: {kids}')
    print(f'   cats_friendly: {cats}')
    print(f'   dogs_friendly: {dogs}')
    print(f'   favorite_place: {place}')
    print(f'   vocal: {vocal}')
    print(f'   food_preferences: {food}')
    print(f'   adoption_recommendation: {rec}')

conn.close()