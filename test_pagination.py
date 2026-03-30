from app import app, db
from models import Cat

with app.app_context():
    # Проверяем количество котов
    total = Cat.query.count()
    print(f"Всего котов: {total}")
    
    # Проверяем пагинацию
    per_page = 9
    page = 2
    
    # Получаем котов для страницы 2
    cats_page2 = Cat.query.order_by(Cat.name).paginate(page=page, per_page=per_page, error_out=False)
    print(f"\nСтраница {page}:")
    print(f"  Всего страниц: {cats_page2.pages}")
    print(f"  Котов на странице: {len(cats_page2.items)}")
    
    for cat in cats_page2.items:
        print(f"    - {cat.name}")