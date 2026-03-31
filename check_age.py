# check_age.py
from app import app, db
from models import Cat

with app.app_context():
    print("🐱 Возраст котиков:")
    print("=" * 40)
    for cat in Cat.query.all():
        if cat.age:
            print(f"{cat.name}: {cat.age} лет")
        else:
            print(f"{cat.name}: возраст не указан")
    print("=" * 40)