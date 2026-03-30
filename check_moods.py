from app import app, db
from models import Cat

with app.app_context():
    moods = db.session.query(Cat.mood).distinct().all()
    print('Настроения в базе:')
    for m in moods:
        if m[0]:
            print(f'  - {m[0]}')
    
    print(f'\nВсего котов: {Cat.query.count()}')
    
    # Проверяем, сколько котов с каждым настроением
    print('\nКоличество по настроениям:')
    for mood in ['Весёлое', 'Спокойное', 'Игривое', 'Грустное']:
        count = Cat.query.filter_by(mood=mood).count()
        print(f'  {mood}: {count} котов')