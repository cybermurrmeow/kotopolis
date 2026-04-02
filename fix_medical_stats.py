# fix_medical_stats.py
from app import app, db
from models import Cat

# Данные для каждого котика
cats_data = {
    "Барсик": {"vaccinated": True, "sterilized": True},
    "Мурка": {"vaccinated": False, "sterilized": True},
    "Рыжик": {"vaccinated": True, "sterilized": False},
    "Софи": {"vaccinated": False, "sterilized": True},
    "Тимофей": {"vaccinated": True, "sterilized": True},
    "Люся": {"vaccinated": True, "sterilized": True},
    "Пушок": {"vaccinated": False, "sterilized": True},
    "Джесси": {"vaccinated": True, "sterilized": True},
    "Маркиз": {"vaccinated": True, "sterilized": True},
    "Боня": {"vaccinated": False, "sterilized": False},
    "Снежок": {"vaccinated": True, "sterilized": True},
    "Шерхан": {"vaccinated": True, "sterilized": True},
    "Карамелька": {"vaccinated": True, "sterilized": False},
    "Граф": {"vaccinated": True, "sterilized": True},
    "Зефирка": {"vaccinated": True, "sterilized": True},
    "Мартин": {"vaccinated": True, "sterilized": False},
    "Леди": {"vaccinated": True, "sterilized": True},
    "Тоша": {"vaccinated": False, "sterilized": True},
    "Симба": {"vaccinated": True, "sterilized": True},
    "Жозефина": {"vaccinated": True, "sterilized": True},
}

with app.app_context():
    updated = 0
    
    for name, data in cats_data.items():
        cat = Cat.query.filter_by(name=name).first()
        if cat:
            cat.is_vaccinated = data["vaccinated"]
            cat.is_sterilized = data["sterilized"]
            updated += 1
            print(f"✅ {name}: вакцинирован={data['vaccinated']}, стерилизован={data['sterilized']}")
        else:
            print(f"❌ {name} не найден")
    
    db.session.commit()
    
    # Проверка
    vaccinated_count = sum(1 for c in Cat.query.all() if c.is_vaccinated)
    sterilized_count = sum(1 for c in Cat.query.all() if c.is_sterilized)
    total = Cat.query.count()
    
    print("\n" + "="*50)
    print(f"📊 Медицинская статистика:")
    print(f"   Всего котиков: {total}")
    print(f"   Вакцинированы: {vaccinated_count} ({vaccinated_count/total*100:.0f}%)")
    print(f"   Стерилизованы: {sterilized_count} ({sterilized_count/total*100:.0f}%)")
    print("="*50)