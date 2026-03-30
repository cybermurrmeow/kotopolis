import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

c.execute('''
    SELECT name, 
           personality, 
           activity_level, 
           kids_friendly, 
           cats_friendly, 
           dogs_friendly, 
           favorite_place, 
           vocal, 
           food_preferences,
           CASE WHEN story IS NOT NULL AND story != '' THEN '✅' ELSE '❌' END as story_status,
           CASE WHEN adoption_recommendation IS NOT NULL AND adoption_recommendation != '' THEN '✅' ELSE '❌' END as rec_status
    FROM cats 
    ORDER BY name
''')

rows = c.fetchall()

print('='*80)
print('ПОЛНАЯ ПРОВЕРКА ВСЕХ 20 КОТОВ')
print('='*80)
print(f"{'Имя':<12} {'Характер':<8} {'Активность':<8} {'Дети':<5} {'Кошки':<5} {'Собаки':<5} {'История':<5} {'Рекоменд':<5}")
print('-'*80)

for row in rows:
    name = row[0]
    pers = '✅' if row[1] else '❌'
    act = '✅' if row[2] else '❌'
    kids = '✅' if row[3] else '❌'
    cats = '✅' if row[4] else '❌'
    dogs = '✅' if row[5] else '❌'
    story = row[9]
    rec = row[10]
    
    print(f"{name:<12} {pers:<8} {act:<8} {kids:<5} {cats:<5} {dogs:<5} {story:<5} {rec:<5}")

conn.close()

print('\n✅ - информация есть')
print('❌ - информации нет')