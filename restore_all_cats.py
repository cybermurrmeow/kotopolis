from app import app, db
from models import Cat
from datetime import date, datetime

def restore_all_cats():
    with app.app_context():
        # Проверяем, есть ли котики
        existing_cats = {cat.name: cat for cat in Cat.query.all()}
        print(f"📊 В базе уже {len(existing_cats)} котиков")
        
        # Полный список всех котиков, которые были в проекте
        all_cats_data = [
            # Оригинальные три котика
            {
                "name": "Барсик",
                "nickname": "Барс",
                "age": 2,
                "breed": "Сиамский",
                "gender": "Мальчик",
                "color": "Кремовый",
                "weight": 4.5,
                "mood": "Игривое",
                "favorite_toy": "Мячик",
                "status": "В приюте",
                "health": "Здоров",
                "description": "Очень активный и ласковый кот",
                "personality": "Игривый",
                "activity_level": "Высокий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": False,
                "favorite_place": "Окно",
                "vocal": "Разговорчивый",
                "food_preferences": "Сухой корм",
                "story": "Найден на улице в 2 месяца",
                "adoption_recommendation": "Идеальный кот для активной семьи"
            },
            {
                "name": "Мурка",
                "nickname": "Мура",
                "age": 3,
                "breed": "Персидская",
                "gender": "Девочка",
                "color": "Белый",
                "weight": 3.8,
                "mood": "Спокойное",
                "favorite_toy": "Мышка",
                "status": "В приюте",
                "health": "Аллергия на корм",
                "description": "Спокойная и ласковая",
                "personality": "Ласковый",
                "activity_level": "Низкий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Диван",
                "vocal": "Молчаливый",
                "food_preferences": "Гипоаллергенный корм",
                "story": "Хозяйка переехала",
                "adoption_recommendation": "Идеальный компаньон для пожилых людей"
            },
            {
                "name": "Рыжик",
                "nickname": "Рыжий",
                "age": 1,
                "breed": "Дворняжка",
                "gender": "Мальчик",
                "color": "Рыжий",
                "weight": 3.2,
                "mood": "Весёлое",
                "favorite_toy": "Верёвочка",
                "status": "В приюте",
                "health": "Здоров",
                "description": "Очень энергичный котёнок",
                "personality": "Игривый",
                "activity_level": "Высокий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коробка",
                "vocal": "Разговорчивый",
                "food_preferences": "Влажный корм",
                "story": "Подкинули в приют",
                "adoption_recommendation": "Нужны активные игры"
            },
            # Дополнительные котики
            {
                "name": "Снежок",
                "nickname": "Снежа",
                "age": 4,
                "breed": "Ангорская",
                "gender": "Девочка",
                "color": "Белый",
                "weight": 4.2,
                "mood": "Спокойное",
                "favorite_toy": "Перо",
                "status": "В приюте",
                "health": "Здорова",
                "description": "Красивая белая кошечка с голубыми глазами",
                "personality": "Спокойный",
                "activity_level": "Средний",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Кресло",
                "vocal": "Молчаливый",
                "food_preferences": "Сухой корм",
                "story": "Спасена с улицы",
                "adoption_recommendation": "Прекрасный питомец для любой семьи"
            },
            {
                "name": "Черныш",
                "nickname": "Черный",
                "age": 5,
                "breed": "Дворняжка",
                "gender": "Мальчик",
                "color": "Черный",
                "weight": 5.0,
                "mood": "Спокойное",
                "favorite_toy": "Мячик",
                "status": "В приюте",
                "health": "Здоров",
                "description": "Чёрный кот с зелёными глазами",
                "personality": "Независимый",
                "activity_level": "Низкий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Тёмный угол",
                "vocal": "Молчаливый",
                "food_preferences": "Влажный корм",
                "story": "Остался без хозяина",
                "adoption_recommendation": "Спокойный кот для уютного дома"
            },
            {
                "name": "Маркиза",
                "nickname": "Маркиза",
                "age": 2,
                "breed": "Мейн-кун",
                "gender": "Девочка",
                "color": "Серебристый",
                "weight": 5.5,
                "mood": "Игривое",
                "favorite_toy": "Верёвочка",
                "status": "В приюте",
                "health": "Здорова",
                "description": "Крупная кошечка с кисточками на ушах",
                "personality": "Игривый",
                "activity_level": "Высокий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Высокое место",
                "vocal": "Разговорчивый",
                "food_preferences": "Сухой корм",
                "story": "Из питомника",
                "adoption_recommendation": "Для активных хозяев"
            },
            {
                "name": "Тиша",
                "nickname": "Тиша",
                "age": 3,
                "breed": "Британская",
                "gender": "Девочка",
                "color": "Голубой",
                "weight": 4.0,
                "mood": "Спокойное",
                "favorite_toy": "Мышка",
                "status": "Усыновлён",
                "health": "Здорова",
                "description": "Пушистая британская кошечка",
                "personality": "Спокойный",
                "activity_level": "Низкий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Диван",
                "vocal": "Молчаливый",
                "food_preferences": "Сухой корм",
                "story": "Найдена в подъезде",
                "adoption_recommendation": "Идеальная кошечка для квартиры"
            },
            {
                "name": "Леопольд",
                "nickname": "Лёпа",
                "age": 6,
                "breed": "Дворняжка",
                "gender": "Мальчик",
                "color": "Рыжий с белым",
                "weight": 4.8,
                "mood": "Весёлое",
                "favorite_toy": "Лазерная указка",
                "status": "На лечении",
                "health": "Лечение зубов",
                "description": "Добрый и мудрый кот",
                "personality": "Ласковый",
                "activity_level": "Средний",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Коврик",
                "vocal": "Разговорчивый",
                "food_preferences": "Влажный корм",
                "story": "Старый кот без хозяина",
                "adoption_recommendation": "Прекрасный компаньон"
            },
            {
                "name": "Пушинка",
                "nickname": "Пуша",
                "age": 1,
                "breed": "Сибирская",
                "gender": "Девочка",
                "color": "Серый",
                "weight": 3.0,
                "mood": "Игривое",
                "favorite_toy": "Бантик",
                "status": "В приюте",
                "health": "Здорова",
                "description": "Пушистый комочек счастья",
                "personality": "Игривый",
                "activity_level": "Высокий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Игрушки",
                "vocal": "Разговорчивый",
                "food_preferences": "Сухой корм",
                "story": "Маленький котёнок",
                "adoption_recommendation": "Для семьи с детьми"
            },
            {
                "name": "Граф",
                "nickname": "Граф",
                "age": 7,
                "breed": "Дворняжка",
                "gender": "Мальчик",
                "color": "Черно-белый",
                "weight": 5.2,
                "mood": "Спокойное",
                "favorite_toy": "Когтеточка",
                "status": "В приюте",
                "health": "Здоров",
                "description": "Благородный кот во фраке",
                "personality": "Спокойный",
                "activity_level": "Низкий",
                "kids_friendly": True,
                "cats_friendly": True,
                "dogs_friendly": True,
                "favorite_place": "Подоконник",
                "vocal": "Молчаливый",
                "food_preferences": "Сухой корм",
                "story": "Пожилой кот",
                "adoption_recommendation": "Спокойный кот для пенсионеров"
            }
        ]
        
        # Добавляем или обновляем котиков
        added = 0
        updated = 0
        
        for data in all_cats_data:
            name = data["name"]
            
            if name in existing_cats:
                # Обновляем существующего котика
                cat = existing_cats[name]
                updated_fields = 0
                
                for key, value in data.items():
                    if hasattr(cat, key) and getattr(cat, key) != value:
                        setattr(cat, key, value)
                        updated_fields += 1
                
                if updated_fields > 0:
                    updated += 1
                    print(f"🔄 Обновлён {name} (+{updated_fields} полей)")
            else:
                # Добавляем нового котика
                cat = Cat(
                    name=data["name"],
                    nickname=data["nickname"],
                    age=data["age"],
                    breed=data["breed"],
                    gender=data["gender"],
                    color=data["color"],
                    weight=data["weight"],
                    mood=data["mood"],
                    favorite_toy=data["favorite_toy"],
                    arrival_date=date.today(),
                    status=data["status"],
                    health=data["health"],
                    description=data["description"],
                    personality=data["personality"],
                    activity_level=data["activity_level"],
                    kids_friendly=data["kids_friendly"],
                    cats_friendly=data["cats_friendly"],
                    dogs_friendly=data["dogs_friendly"],
                    favorite_place=data["favorite_place"],
                    vocal=data["vocal"],
                    food_preferences=data["food_preferences"],
                    story=data["story"],
                    adoption_recommendation=data["adoption_recommendation"],
                    last_vacc_date=date.today(),
                    is_vaccinated=True,
                    is_sterilized=False
                )
                db.session.add(cat)
                added += 1
                print(f"➕ Добавлен {name}")
        
        db.session.commit()
        
        print("\n" + "="*50)
        print(f"📊 ИТОГИ:")
        print(f"   ✅ Добавлено: {added} котиков")
        print(f"   🔄 Обновлено: {updated} котиков")
        print(f"   📋 Всего в базе: {Cat.query.count()} котиков")
        print("="*50)
        
        # Показываем всех котиков
        print("\n🐱 СПИСОК КОТИКОВ:")
        for cat in Cat.query.order_by(Cat.name).all():
            print(f"   - {cat.name} ({cat.breed}) - {cat.status}")

if __name__ == "__main__":
    restore_all_cats()