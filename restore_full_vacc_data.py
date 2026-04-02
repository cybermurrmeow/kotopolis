# restore_full_vacc_data.py
from app import app, db
from models import Cat
from datetime import date, timedelta

# Полные данные о прививках для каждого котика
cats_vacc_data = {
    "Барсик": {"vaccinated": True, "last_vacc": date(2025, 3, 1), "next_vacc": date(2026, 3, 1)},
    "Мурка": {"vaccinated": False, "last_vacc": None, "next_vacc": None},
    "Рыжик": {"vaccinated": True, "last_vacc": date(2025, 2, 15), "next_vacc": date(2026, 2, 15)},
    "Софи": {"vaccinated": False, "last_vacc": None, "next_vacc": None},
    "Тимофей": {"vaccinated": True, "last_vacc": date(2025, 1, 10), "next_vacc": date(2026, 1, 10)},
    "Люся": {"vaccinated": True, "last_vacc": date(2025, 2, 20), "next_vacc": date(2026, 2, 20)},
    "Пушок": {"vaccinated": False, "last_vacc": None, "next_vacc": None},
    "Джесси": {"vaccinated": True, "last_vacc": date(2024, 12, 5), "next_vacc": date(2025, 12, 5)},
    "Маркиз": {"vaccinated": True, "last_vacc": date(2025, 3, 20), "next_vacc": date(2026, 3, 20)},
    "Боня": {"vaccinated": False, "last_vacc": None, "next_vacc": None},
    "Снежок": {"vaccinated": True, "last_vacc": date(2024, 9, 15), "next_vacc": date(2025, 9, 15)},
    "Шерхан": {"vaccinated": True, "last_vacc": date(2025, 1, 25), "next_vacc": date(2026, 1, 25)},
    "Карамелька": {"vaccinated": True, "last_vacc": date(2025, 3, 25), "next_vacc": date(2026, 3, 25)},
    "Граф": {"vaccinated": True, "last_vacc": date(2024, 4, 10), "next_vacc": date(2025, 4, 10)},
    "Зефирка": {"vaccinated": True, "last_vacc": date(2025, 3, 10), "next_vacc": date(2026, 3, 10)},
    "Мартин": {"vaccinated": True, "last_vacc": date(2025, 2, 5), "next_vacc": date(2026, 2, 5)},
    "Леди": {"vaccinated": True, "last_vacc": date(2024, 10, 1), "next_vacc": date(2025, 10, 1)},
    "Тоша": {"vaccinated": False, "last_vacc": None, "next_vacc": None},
    "Симба": {"vaccinated": True, "last_vacc": date(2025, 2, 28), "next_vacc": date(2026, 2, 28)},
    "Жозефина": {"vaccinated": True, "last_vacc": date(2025, 1, 30), "next_vacc": date(2026, 1, 30)},
}

with app.app_context():
    updated = 0
    not_found = []
    
    for name, data in cats_vacc_data.items():
        cat = Cat.query.filter_by(name=name).first()
        if cat:
            cat.is_vaccinated = data["vaccinated"]
            cat.last_vacc_date = data["last_vacc"]
            cat.next_vacc_date = data["next_vacc"]
            updated += 1
            
            if cat.is_vaccinated:
                print(f"✅ {name}: Привит, последняя: {cat.last_vacc_date}, следующая: {cat.next_vacc_date}")
            else:
                print(f"⚠️ {name}: Не привит")
        else:
            not_found.append(name)
            print(f"❌ {name} не найден")
    
    db.session.commit()
    
    # Подсчет статистики
    vaccinated_count = sum(1 for c in Cat.query.all() if c.is_vaccinated)
    total = Cat.query.count()
    
    print("\n" + "="*60)
    print(f"📊 ИТОГИ:")
    print(f"   ✅ Обновлено: {updated} котиков")
    print(f"   💉 Вакцинированы: {vaccinated_count} из {total} ({vaccinated_count/total*100:.0f}%)")
    if not_found:
        print(f"   ⚠️ Не найдены: {', '.join(not_found)}")
    print("="*60)