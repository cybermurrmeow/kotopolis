import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Проверяем все дополнительные поля для одного кота
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
           story, 
           adoption_recommendation 
    FROM cats 
    WHERE name = 'Барсик'
''')
row = c.fetchone()

print('='*70)
print('ПОЛНАЯ ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ДЛЯ БАРСИКА')
print('='*70)
print(f"""
🐱 Имя: {row[0]}

📝 ХАРАКТЕР:
   {row[1]}

⚡ АКТИВНОСТЬ:
   {row[2]}

👶 ОТНОШЕНИЕ К ДЕТЯМ:
   {'✅ Да' if row[3] else '❌ Нет'}

🐱 ОТНОШЕНИЕ К ДРУГИМ КОШКАМ:
   {'✅ Да' if row[4] else '❌ Нет'}

🐕 ОТНОШЕНИЕ К СОБАКАМ:
   {'✅ Да' if row[5] else '❌ Нет'}

📍 ЛЮБИМОЕ МЕСТО:
   {row[6]}

🎤 ГОЛОС:
   {row[7]}

🍽️ ПИТАНИЕ:
   {row[8]}

📖 ИСТОРИЯ:
   {row[9]}

💡 РЕКОМЕНДАЦИИ:
   {row[10]}
""")

conn.close()