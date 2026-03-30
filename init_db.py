from app import app, db
from models import User, Cat
from werkzeug.security import generate_password_hash
from datetime import date

print("=" * 50)
print("СОЗДАНИЕ БАЗЫ ДАННЫХ")
print("=" * 50)

with app.app_context():
    # Создаём таблицы
    db.create_all()
    print("✅ Таблицы созданы")
    
    # Создаём админа
    admin = User(
        username='admin',
        email='admin@kotopolis.ru',
        password=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(admin)
    print("✅ Админ создан: admin / admin123")
    
    # Создаём волонтёра
    volunteer = User(
        username='volunteer',
        email='volunteer@kotopolis.ru',
        password=generate_password_hash('volunteer123'),
        role='volunteer'
    )
    db.session.add(volunteer)
    print("✅ Волонтёр создан: volunteer / volunteer123")
    
    # Добавляем тестовых котов
    cats = [
        Cat(
            name='Барсик', nickname='Барс', age=2, breed='Сиамский', gender='Мальчик',
            color='Кремовый', weight=4.5, mood='Игривое', favorite_toy='Мячик',
            status='В приюте', health='Здоров',
            description='Очень активный и ласковый кот'
        ),
        Cat(
            name='Мурка', nickname='Мура', age=3, breed='Персидская', gender='Девочка',
            color='Белый', weight=3.8, mood='Спокойное', favorite_toy='Мышка',
            status='В приюте', health='Аллергия на корм',
            description='Спокойная и ласковая'
        ),
        Cat(
            name='Рыжик', nickname='Рыжий', age=1, breed='Дворняжка', gender='Мальчик',
            color='Рыжий', weight=3.2, mood='Весёлое', favorite_toy='Верёвочка',
            status='В приюте', health='Здоров',
            description='Энергичный котёнок'
        )
    ]
    
    for cat in cats:
        db.session.add(cat)
    
    db.session.commit()
    print(f"✅ Добавлено {len(cats)} тестовых котов")
    
    print("\n" + "=" * 50)
    print("✅ БАЗА ДАННЫХ ГОТОВА!")
    print("=" * 50)
    print(f"   Пользователей: {User.query.count()}")
    print(f"   Котов: {Cat.query.count()}")
    print("\n📝 ДАННЫЕ ДЛЯ ВХОДА:")
    print("   👑 Админ: admin / admin123")
    print("   🤝 Волонтёр: volunteer / volunteer123")