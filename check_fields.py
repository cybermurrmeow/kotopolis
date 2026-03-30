from app import app, db
from models import Cat

with app.app_context():
    # Получаем первого кота для примера
    cat = Cat.query.first()
    
    print("📋 Доступные поля в модели Cat:")
    print("="*50)
    
    # Список полей, которые мы хотим проверить
    fields_to_check = [
        'name', 'nickname', 'age', 'breed', 'gender', 'color', 'weight', 
        'mood', 'favorite_toy', 'status', 'health', 'description',
        'personality', 'activity_level', 'kids_friendly', 'cats_friendly', 
        'dogs_friendly', 'favorite_place', 'vocal', 'food_preferences', 
        'story', 'adoption_recommendation', 'photo_path'
    ]
    
    for field in fields_to_check:
        if hasattr(Cat, field):
            # Пытаемся получить значение у первого кота
            try:
                value = getattr(cat, field)
                print(f"✅ {field} = {value}")
            except:
                print(f"✅ {field} - поле существует")
        else:
            print(f"❌ {field} - отсутствует")