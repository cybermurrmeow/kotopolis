from app import app, db
from models import Cat
from forms import CatForm

with app.app_context():
    cat = Cat.query.filter_by(name='Барсик').first()
    
    if cat:
        print("🐱 Текущие данные в БД для Барсика:")
        print(f"   personality: {cat.personality}")
        print(f"   activity_level: {cat.activity_level}")
        print(f"   vocal: {cat.vocal}")
        
        # Создаём форму с данными кота
        form = CatForm(obj=cat)
        
        print("\n📋 Данные в форме (должны совпадать):")
        print(f"   personality.data: {form.personality.data}")
        print(f"   activity_level.data: {form.activity_level.data}")
        print(f"   vocal.data: {form.vocal.data}")
        
        # Меняем значения в форме
        form.personality.data = "Тестовый характер"
        form.activity_level.data = "Тестовый уровень"
        form.vocal.data = "Тестовый голос"
        
        print("\n✏️ После изменения в форме:")
        print(f"   personality.data: {form.personality.data}")
        print(f"   activity_level.data: {form.activity_level.data}")
        print(f"   vocal.data: {form.vocal.data}")
        
        # Проверяем, что можно сохранить
        cat.personality = form.personality.data
        cat.activity_level = form.activity_level.data
        cat.vocal = form.vocal.data
        
        print("\n💾 После сохранения в объект:")
        print(f"   cat.personality: {cat.personality}")
        print(f"   cat.activity_level: {cat.activity_level}")
        print(f"   cat.vocal: {cat.vocal}")