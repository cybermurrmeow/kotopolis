import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Данные для всех котов (только значения из выпадающих списков)
cats_data = {
    "Барсик": {"personality": "Игривый", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Мурка": {"personality": "Ласковый", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Рыжик": {"personality": "Энергичный", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Софи": {"personality": "Спокойный", "activity_level": "Средний", "vocal": "Молчаливый"},
    "Тимофей": {"personality": "Добрый", "activity_level": "Высокий", "vocal": "Поющий"},
    "Люся": {"personality": "Ласковый", "activity_level": "Средний", "vocal": "Разговорчивый"},
    "Пушок": {"personality": "Спокойный", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Джесси": {"personality": "Игривый", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Маркиз": {"personality": "Спокойный", "activity_level": "Средний", "vocal": "Молчаливый"},
    "Боня": {"personality": "Ласковый", "activity_level": "Высокий", "vocal": "Поющий"},
    "Снежок": {"personality": "Ласковый", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Шерхан": {"personality": "Энергичный", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Карамелька": {"personality": "Игривый", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Граф": {"personality": "Спокойный", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Зефирка": {"personality": "Игривый", "activity_level": "Средний", "vocal": "Поющий"},
    "Мартин": {"personality": "Энергичный", "activity_level": "Высокий", "vocal": "Разговорчивый"},
    "Леди": {"personality": "Ласковый", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Тоша": {"personality": "Спокойный", "activity_level": "Низкий", "vocal": "Молчаливый"},
    "Симба": {"personality": "Игривый", "activity_level": "Высокий", "vocal": "Поющий"},
    "Жозефина": {"personality": "Ласковый", "activity_level": "Средний", "vocal": "Разговорчивый"}
}

# Обновляем данные
updated = 0
for name, info in cats_data.items():
    c.execute('''
        UPDATE cats 
        SET personality = ?, activity_level = ?, vocal = ?
        WHERE name = ?
    ''', (info["personality"], info["activity_level"], info["vocal"], name))
    updated += 1
    print(f"✅ {name}: характер={info['personality']}, активность={info['activity_level']}, голос={info['vocal']}")

conn.commit()
conn.close()

print(f"\n✅ Обновлено {updated} котиков!")