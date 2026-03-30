from app import app, db
from models import Cat

with app.app_context():
    # Удаляем всех котов
    count = Cat.query.count()
    Cat.query.delete()
    db.session.commit()
    print(f"✅ Удалено {count} котиков")
    print(f"📊 В базе осталось: {Cat.query.count()} котиков")