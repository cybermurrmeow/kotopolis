# fix_age.py
from app import app, db
from models import Cat

with app.app_context():
    cats = Cat.query.all()
    for cat in cats:
        if cat.age and cat.age < 12:  # Если возраст меньше 12 (был в годах)
            cat.age = cat.age * 12    # Переводим в месяцы
            print(f"✅ {cat.name}: {cat.age//12} лет → {cat.age} мес.")
    
    db.session.commit()
    print("🎉 Возраст обновлен!")