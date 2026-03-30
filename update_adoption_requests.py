from app import app, db
from models import AdoptionRequest, Cat
from datetime import date, timedelta
import random

def update_adoption_requests():
    with app.app_context():
        # Получаем усыновлённых котов
        adopted_cats = Cat.query.filter_by(status='Усыновлён').all()
        adopted_names = [cat.name for cat in adopted_cats]
        
        # Получаем котов, которые не усыновлены
        available_cats = Cat.query.filter(Cat.status != 'Усыновлён').all()
        
        if not available_cats:
            print("❌ Нет доступных котов для заявок!")
            return
        
        print(f"📊 Усыновлённые коты: {[c.name for c in adopted_cats]}")
        print(f"📊 Доступные коты: {[c.name for c in available_cats]}")
        
        # Получаем все заявки
        requests = AdoptionRequest.query.all()
        
        if not requests:
            print("❌ Нет заявок в базе!")
            return
        
        updated = 0
        for request in requests:
            old_cat = request.cat
            # Если заявка была на усыновлённого кота
            if old_cat and old_cat.status == 'Усыновлён':
                # Выбираем случайного доступного кота
                new_cat = random.choice(available_cats)
                old_cat_name = old_cat.name
                request.cat_id = new_cat.id
                updated += 1
                print(f"🔄 Заявка от {request.adopter_name}: {old_cat_name} → {new_cat.name}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ Обновлено {updated} заявок!")
        print("="*50)
        
        # Показываем обновлённые заявки
        print("\n📋 ОБНОВЛЁННЫЕ ЗАЯВКИ:")
        for request in AdoptionRequest.query.all():
            cat_name = request.cat.name if request.cat else 'Котик удалён'
            print(f"   {request.adopter_name} → {cat_name} ({request.status})")

if __name__ == "__main__":
    update_adoption_requests()