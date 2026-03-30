from app import app, db
from models import Cat

with app.app_context():
    cat = Cat.query.filter_by(name='Рыжик').first()
    if cat:
        print(f'Рыжик: статус={cat.status}, здоровье={cat.health}')
    else:
        print('Кот Рыжик не найден')