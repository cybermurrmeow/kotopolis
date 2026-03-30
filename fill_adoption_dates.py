from app import app, db
from models import Cat
from datetime import date, timedelta
import random

with app.app_context():
    adopted_cats = Cat.query.filter_by(status='Усыновлён').all()
    
    if adopted_cats:
        print(f"Найдено {len(adopted_cats)} усыновлённых котов")
        
        for cat in adopted_cats:
            if not cat.adoption_date:
                # Случайная дата от 1 до 6 месяцев назад
                random_days = random.randint(30, 180)
                cat.adoption_date = date.today() - timedelta(days=random_days)
                print(f"✅ {cat.name}: дата усыновления {cat.adoption_date}")
        
        db.session.commit()
        print("✅ Готово!")
    else:
        print("❌ Нет усыновлённых котов")