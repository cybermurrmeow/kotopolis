# remove_avatar_column.py
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Проверяем, есть ли колонка avatar
        result = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
        columns = [col[1] for col in result]
        
        if 'avatar' in columns:
            # SQLite не поддерживает DROP COLUMN, но колонка останется неиспользуемой
            print("⚠️ Колонка avatar существует, но будет игнорироваться")
        
        print("✅ Модель обновлена, загрузка аватара удалена")
    except Exception as e:
        print(f"❌ Ошибка: {e}")