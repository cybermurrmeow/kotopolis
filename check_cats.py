from app import app, db
from models import Cat

with app.app_context():
    cats = Cat.query.all()
    print(f'Всего котиков: {len(cats)}')
    for cat in cats:
        print(f'  - {cat.name}')