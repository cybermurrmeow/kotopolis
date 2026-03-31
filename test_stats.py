# test_stats.py
from app import app, db
from models import Cat
from utils import calculate_stats

with app.app_context():
    cats = Cat.query.all()
    stats = calculate_stats(cats)
    
    print("📊 Статистика:")
    print(f"Всего котиков: {stats['total']}")
    print(f"Котята (<1 года): {stats['kittens']}")
    print(f"Молодые (1-3 года): {stats['young']}")
    print(f"Взрослые (4-7 лет): {stats['adult']}")
    print(f"Пожилые (8+ лет): {stats['senior']}")
    
    print("\n🐱 Возраст каждого котика в месяцах:")
    for cat in cats:
        print(f"   {cat.name}: {cat.age} мес.")