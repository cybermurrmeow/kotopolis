import sqlite3
from datetime import date, timedelta

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

# Даты для каждого кота (из вашего скрипта)
cats_dates = {
    "Барсик": {
        "arrival_date": date(2025, 6, 15),
        "last_vacc_date": date(2025, 12, 10),
        "next_vacc_date": date(2026, 12, 10)
    },
    "Мурка": {
        "arrival_date": date(2025, 8, 20),
        "last_vacc_date": date(2024, 12, 15),
        "next_vacc_date": date(2025, 12, 15)
    },
    "Рыжик": {
        "arrival_date": date(2026, 1, 10),
        "last_vacc_date": date(2026, 1, 5),
        "next_vacc_date": date(2026, 7, 5)
    },
    "Софи": {
        "arrival_date": date(2025, 4, 5),
        "last_vacc_date": date(2024, 3, 1),
        "next_vacc_date": date(2025, 3, 1)
    },
    "Тимофей": {
        "arrival_date": date(2026, 2, 12),
        "last_vacc_date": date(2026, 2, 10),
        "next_vacc_date": date(2027, 2, 10)
    },
    "Люся": {
        "arrival_date": date(2025, 11, 18),
        "last_vacc_date": date(2025, 5, 15),
        "next_vacc_date": date(2026, 5, 15)
    },
    "Пушок": {
        "arrival_date": date(2025, 9, 22),
        "last_vacc_date": date(2024, 8, 20),
        "next_vacc_date": date(2025, 8, 20)
    },
    "Джесси": {
        "arrival_date": date(2025, 10, 30),
        "last_vacc_date": date(2025, 10, 25),
        "next_vacc_date": date(2026, 10, 25)
    },
    "Маркиз": {
        "arrival_date": date(2026, 2, 14),
        "last_vacc_date": date(2026, 2, 10),
        "next_vacc_date": date(2027, 2, 10)
    },
    "Боня": {
        "arrival_date": date(2026, 3, 1),
        "last_vacc_date": None,
        "next_vacc_date": None
    },
    "Снежок": {
        "arrival_date": date(2025, 12, 5),
        "last_vacc_date": date(2025, 12, 1),
        "next_vacc_date": date(2026, 12, 1)
    },
    "Шерхан": {
        "arrival_date": date(2025, 7, 18),
        "last_vacc_date": date(2025, 7, 10),
        "next_vacc_date": date(2026, 7, 10)
    },
    "Карамелька": {
        "arrival_date": date(2026, 2, 20),
        "last_vacc_date": date(2026, 2, 15),
        "next_vacc_date": date(2026, 8, 15)
    },
    "Граф": {
        "arrival_date": date(2025, 5, 10),
        "last_vacc_date": date(2025, 5, 5),
        "next_vacc_date": date(2026, 5, 5)
    },
    "Зефирка": {
        "arrival_date": date(2025, 11, 25),
        "last_vacc_date": date(2025, 11, 20),
        "next_vacc_date": date(2026, 11, 20)
    },
    "Мартин": {
        "arrival_date": date(2026, 1, 15),
        "last_vacc_date": date(2026, 1, 10),
        "next_vacc_date": date(2026, 7, 10)
    },
    "Леди": {
        "arrival_date": date(2025, 3, 10),
        "last_vacc_date": date(2025, 3, 5),
        "next_vacc_date": date(2026, 3, 5)
    },
    "Тоша": {
        "arrival_date": date(2025, 6, 1),
        "last_vacc_date": date(2024, 6, 1),
        "next_vacc_date": date(2025, 6, 1)
    },
    "Симба": {
        "arrival_date": date(2025, 9, 5),
        "last_vacc_date": date(2025, 9, 1),
        "next_vacc_date": date(2026, 9, 1)
    },
    "Жозефина": {
        "arrival_date": date(2025, 10, 10),
        "last_vacc_date": date(2025, 10, 5),
        "next_vacc_date": date(2026, 10, 5)
    }
}

# Обновляем даты
updated = 0
for name, dates in cats_dates.items():
    # Проверяем, есть ли такой кот
    c.execute("SELECT id FROM cats WHERE name = ?", (name,))
    if c.fetchone():
        c.execute('''
            UPDATE cats 
            SET arrival_date = ?, last_vacc_date = ?, next_vacc_date = ?
            WHERE name = ?
        ''', (dates["arrival_date"], dates["last_vacc_date"], dates["next_vacc_date"], name))
        updated += 1
        print(f"✅ {name}: даты обновлены")
    else:
        print(f"⚠️ {name}: кот не найден")

conn.commit()
conn.close()

print(f"\n✅ Обновлено {updated} котиков!")