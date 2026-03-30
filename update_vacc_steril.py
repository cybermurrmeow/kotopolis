from app import app, db
from models import Cat
from datetime import date, timedelta

with app.app_context():
    cats = Cat.query.all()
    updated = 0
    
    # Обновляем информацию для каждого кота
    cats_data = {
        "Барсик": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 12, 10), "next_vacc_date": date(2026, 12, 10)},
        "Мурка": {"is_vaccinated": False, "is_sterilized": True, "last_vacc_date": date(2024, 12, 15), "next_vacc_date": date(2025, 12, 15)},
        "Рыжик": {"is_vaccinated": True, "is_sterilized": False, "last_vacc_date": date(2026, 1, 5), "next_vacc_date": date(2026, 7, 5)},
        "Софи": {"is_vaccinated": False, "is_sterilized": True, "last_vacc_date": date(2024, 3, 1), "next_vacc_date": date(2025, 3, 1)},
        "Тимофей": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2026, 2, 10), "next_vacc_date": date(2027, 2, 10)},
        "Люся": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 5, 15), "next_vacc_date": date(2026, 5, 15)},
        "Пушок": {"is_vaccinated": False, "is_sterilized": True, "last_vacc_date": date(2024, 8, 20), "next_vacc_date": date(2025, 8, 20)},
        "Джесси": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 10, 25), "next_vacc_date": date(2026, 10, 25)},
        "Маркиз": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2026, 2, 10), "next_vacc_date": date(2027, 2, 10)},
        "Боня": {"is_vaccinated": False, "is_sterilized": False, "last_vacc_date": None, "next_vacc_date": None},
        "Снежок": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 12, 1), "next_vacc_date": date(2026, 12, 1)},
        "Шерхан": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 7, 10), "next_vacc_date": date(2026, 7, 10)},
        "Карамелька": {"is_vaccinated": True, "is_sterilized": False, "last_vacc_date": date(2026, 2, 15), "next_vacc_date": date(2026, 8, 15)},
        "Граф": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 5, 5), "next_vacc_date": date(2026, 5, 5)},
        "Зефирка": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 11, 20), "next_vacc_date": date(2026, 11, 20)},
        "Мартин": {"is_vaccinated": True, "is_sterilized": False, "last_vacc_date": date(2026, 1, 10), "next_vacc_date": date(2026, 7, 10)},
        "Леди": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 3, 5), "next_vacc_date": date(2026, 3, 5)},
        "Тоша": {"is_vaccinated": False, "is_sterilized": True, "last_vacc_date": date(2024, 6, 1), "next_vacc_date": date(2025, 6, 1)},
        "Симба": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 9, 1), "next_vacc_date": date(2026, 9, 1)},
        "Жозефина": {"is_vaccinated": True, "is_sterilized": True, "last_vacc_date": date(2025, 10, 5), "next_vacc_date": date(2026, 10, 5)},
    }
    
    for name, data in cats_data.items():
        cat = Cat.query.filter_by(name=name).first()
        if cat:
            cat.is_vaccinated = data["is_vaccinated"]
            cat.is_sterilized = data["is_sterilized"]
            cat.last_vacc_date = data["last_vacc_date"]
            cat.next_vacc_date = data["next_vacc_date"]
            updated += 1
            print(f"✅ {name}: вакцинация={data['is_vaccinated']}, стерилизация={data['is_sterilized']}")
    
    db.session.commit()
    print(f"\n✅ Обновлено {updated} котиков!")
    
    # Статистика
    vaccinated = Cat.query.filter_by(is_vaccinated=True).count()
    sterilized = Cat.query.filter_by(is_sterilized=True).count()
    total = Cat.query.count()
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   Вакцинировано: {vaccinated} из {total} ({round(vaccinated/total*100)}%)")
    print(f"   Стерилизовано: {sterilized} из {total} ({round(sterilized/total*100)}%)")