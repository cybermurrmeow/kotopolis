from app import app, db
from models import Cat
from datetime import date, timedelta
import random

def fill_adoption_dates():
    with app.app_context():
        # Находим всех усыновлённых котов
        adopted_cats = Cat.query.filter_by(status='Усыновлён').all()
        
        if not adopted_cats:
            print("❌ Нет усыновлённых котов")
            return
        
        print(f"📊 Найдено {len(adopted_cats)} усыновлённых котов:")
        for cat in adopted_cats:
            print(f"   - {cat.name}")
        
        print("\n🔧 Заполняем даты усыновления...")
        
        updated = 0
        for cat in adopted_cats:
            # Если дата уже есть, пропускаем
            if cat.adoption_date:
                print(f"   ⚠️ {cat.name}: уже есть дата {cat.adoption_date}")
                continue
            
            # Генерируем дату усыновления (от 1 до 6 месяцев назад)
            random_days = random.randint(30, 180)
            adoption_date = date.today() - timedelta(days=random_days)
            cat.adoption_date = adoption_date
            updated += 1
            print(f"   ✅ {cat.name}: дата усыновления {adoption_date.strftime('%d.%m.%Y')}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ Обновлено {updated} котов")
        print("="*50)
        
        # Показываем итоговую статистику
        print("\n📊 ИТОГОВАЯ СТАТИСТИКА:")
        for cat in adopted_cats:
            print(f"   {cat.name}: {cat.adoption_date.strftime('%d.%m.%Y') if cat.adoption_date else '❌ НЕТ ДАТЫ'}")

if __name__ == "__main__":
    fill_adoption_dates()