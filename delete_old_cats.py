from app import app, db
from models import Cat

def delete_old_cats():
    with app.app_context():
        # Список имен старых котов, которые были добавлены первыми
        old_cats_names = [
            "Барсик", "Мурка", "Рыжик", "Снежок", "Черныш", "Маркиза", 
            "Тиша", "Леопольд", "Пушинка", "Граф", "Симба", "Багира", 
            "Зефир", "Васька", "Маня", "Кекс", "Ночка", "Боня", 
            "Фрося", "Мармеладка"
        ]
        
        # Проверяем, сколько котов в базе
        all_cats = Cat.query.all()
        print(f"📊 В базе {len(all_cats)} котиков")
        
        # Удаляем старых котов
        deleted_count = 0
        for cat_name in old_cats_names:
            cat = Cat.query.filter_by(name=cat_name).first()
            if cat:
                db.session.delete(cat)
                deleted_count += 1
                print(f"🗑️ Удалён: {cat_name}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"✅ УДАЛЕНО: {deleted_count} старых котиков")
        print(f"📊 Осталось в базе: {Cat.query.count()} котиков")
        print("="*50)
        
        # Показываем оставшихся
        remaining = Cat.query.all()
        if remaining:
            print("\n🐱 ОСТАВШИЕСЯ КОТИКИ:")
            for cat in remaining:
                print(f"   - {cat.name} ({cat.breed}) - {cat.status}")

if __name__ == "__main__":
    delete_old_cats()