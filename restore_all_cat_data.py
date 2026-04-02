# restore_all_cat_data.py
from app import app, db
from models import Cat
from datetime import date, timedelta

# ПОЛНЫЕ ДАННЫЕ О КОТИКАХ
cats_full_data = {
    "Барсик": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 3, 1), "next_vacc": date(2026, 3, 1),
        "adoption_date": None, "status": "В приюте"
    },
    "Мурка": {
        "vaccinated": False, "sterilized": True,
        "last_vacc": None, "next_vacc": None,
        "adoption_date": None, "status": "В приюте"
    },
    "Рыжик": {
        "vaccinated": True, "sterilized": False,
        "last_vacc": date(2025, 2, 15), "next_vacc": date(2026, 2, 15),
        "adoption_date": None, "status": "В приюте"
    },
    "Софи": {
        "vaccinated": False, "sterilized": True,
        "last_vacc": None, "next_vacc": None,
        "adoption_date": None, "status": "В приюте"
    },
    "Тимофей": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 1, 10), "next_vacc": date(2026, 1, 10),
        "adoption_date": None, "status": "В приюте"
    },
    "Люся": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 2, 20), "next_vacc": date(2026, 2, 20),
        "adoption_date": None, "status": "В приюте"
    },
    "Пушок": {
        "vaccinated": False, "sterilized": True,
        "last_vacc": None, "next_vacc": None,
        "adoption_date": None, "status": "В приюте"
    },
    "Джесси": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2024, 12, 5), "next_vacc": date(2025, 12, 5),
        "adoption_date": date(2025, 3, 15), "status": "Усыновлён"
    },
    "Маркиз": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 3, 20), "next_vacc": date(2026, 3, 20),
        "adoption_date": None, "status": "В приюте"
    },
    "Боня": {
        "vaccinated": False, "sterilized": False,
        "last_vacc": None, "next_vacc": None,
        "adoption_date": None, "status": "В приюте"
    },
    "Снежок": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2024, 9, 15), "next_vacc": date(2025, 9, 15),
        "adoption_date": None, "status": "В приюте"
    },
    "Шерхан": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 1, 25), "next_vacc": date(2026, 1, 25),
        "adoption_date": None, "status": "В приюте"
    },
    "Карамелька": {
        "vaccinated": True, "sterilized": False,
        "last_vacc": date(2025, 3, 25), "next_vacc": date(2026, 3, 25),
        "adoption_date": None, "status": "В приюте"
    },
    "Граф": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2024, 4, 10), "next_vacc": date(2025, 4, 10),
        "adoption_date": None, "status": "В приюте"
    },
    "Зефирка": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 3, 10), "next_vacc": date(2026, 3, 10),
        "adoption_date": None, "status": "В приюте"
    },
    "Мартин": {
        "vaccinated": True, "sterilized": False,
        "last_vacc": date(2025, 2, 5), "next_vacc": date(2026, 2, 5),
        "adoption_date": None, "status": "В приюте"
    },
    "Леди": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2024, 10, 1), "next_vacc": date(2025, 10, 1),
        "adoption_date": date(2025, 2, 10), "status": "Усыновлён"
    },
    "Тоша": {
        "vaccinated": False, "sterilized": True,
        "last_vacc": None, "next_vacc": None,
        "adoption_date": None, "status": "В приюте"
    },
    "Симба": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 2, 28), "next_vacc": date(2026, 2, 28),
        "adoption_date": None, "status": "В приюте"
    },
    "Жозефина": {
        "vaccinated": True, "sterilized": True,
        "last_vacc": date(2025, 1, 30), "next_vacc": date(2026, 1, 30),
        "adoption_date": None, "status": "В приюте"
    },
}

with app.app_context():
    updated = 0
    not_found = []
    
    for name, data in cats_full_data.items():
        cat = Cat.query.filter_by(name=name).first()
        if cat:
            # Основные поля
            cat.is_vaccinated = data["vaccinated"]
            cat.is_sterilized = data["sterilized"]
            cat.last_vacc_date = data["last_vacc"]
            cat.next_vacc_date = data["next_vacc"]
            cat.adoption_date = data["adoption_date"]
            cat.status = data["status"]
            updated += 1
            
            # Вывод информации
            vacc_status = "✅ Привит" if cat.is_vaccinated else "❌ Не привит"
            steril_status = "✅ Стерилизован" if cat.is_sterilized else "❌ Не стерилизован"
            print(f"\n📌 {name}:")
            print(f"   💉 {vacc_status}")
            if cat.last_vacc_date:
                print(f"   📅 Последняя прививка: {cat.last_vacc_date}")
            if cat.next_vacc_date:
                print(f"   📅 Следующая прививка: {cat.next_vacc_date}")
            print(f"   ✂️ {steril_status}")
            if cat.status == "Усыновлён" and cat.adoption_date:
                print(f"   🏠 Усыновлён: {cat.adoption_date}")
            print(f"   📍 Статус: {cat.status}")
        else:
            not_found.append(name)
            print(f"❌ {name} не найден")
    
    db.session.commit()
    
    # Статистика
    total = Cat.query.count()
    vaccinated = sum(1 for c in Cat.query.all() if c.is_vaccinated)
    sterilized = sum(1 for c in Cat.query.all() if c.is_sterilized)
    adopted = sum(1 for c in Cat.query.all() if c.status == "Усыновлён")
    
    print("\n" + "="*60)
    print("📊 СТАТИСТИКА ПОСЛЕ ВОССТАНОВЛЕНИЯ:")
    print(f"   🐱 Всего котиков: {total}")
    print(f"   💉 Вакцинированы: {vaccinated} ({vaccinated/total*100:.0f}%)")
    print(f"   ✂️ Стерилизованы: {sterilized} ({sterilized/total*100:.0f}%)")
    print(f"   🏠 Усыновлены: {adopted}")
    print(f"   ✅ Обновлено: {updated} котиков")
    if not_found:
        print(f"   ⚠️ Не найдены: {', '.join(not_found)}")
    print("="*60)