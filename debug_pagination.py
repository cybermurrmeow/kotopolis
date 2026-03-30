from app import app, db
from models import Cat

with app.app_context():
    # Проверяем количество котов
    total = Cat.query.count()
    print(f"1. Всего котов: {total}")
    
    # Проверяем пагинацию
    per_page = 9
    page = 1
    
    pagination = Cat.query.order_by(Cat.name).paginate(page=page, per_page=per_page, error_out=False)
    
    print(f"\n2. Пагинация на странице {page}:")
    print(f"   - Всего страниц: {pagination.pages}")
    print(f"   - Котов на странице: {len(pagination.items)}")
    print(f"   - Есть следующая страница: {pagination.has_next}")
    print(f"   - Есть предыдущая: {pagination.has_prev}")
    
    if pagination.has_next:
        print(f"   - Номер следующей страницы: {pagination.next_num}")
    
    print("\n3. Коты на первой странице:")
    for cat in pagination.items:
        print(f"   - {cat.name}")
    
    print("\n4. Проверка переменных для шаблона:")
    print(f"   pagination.pages: {pagination.pages}")
    print(f"   pagination.page: {pagination.page}")
    print(f"   pagination.has_prev: {pagination.has_prev}")
    print(f"   pagination.has_next: {pagination.has_next}")