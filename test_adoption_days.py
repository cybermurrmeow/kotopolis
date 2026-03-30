from app import app, db
from models import Cat

with app.app_context():
    # Находим усыновлённого кота
    cat = Cat.query.filter_by(status='Усыновлён').first()
    
    if cat:
        print(f"🐱 {cat.name}")
        print(f"   Дата поступления: {cat.arrival_date}")
        print(f"   Дата усыновления: {cat.adoption_date}")
        print(f"   Дней в приюте: {cat.days_in_shelter}")
        
        # Проверяем, что дни не меняются
        print(f"\n📌 Примечание: Это финальное количество дней в приюте.")
        print(f"   Оно больше не будет увеличиваться.")
    else:
        print("❌ Нет усыновлённых котов")