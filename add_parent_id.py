import sqlite3
import os

def add_parent_id_column():
    db_path = 'instance/kotopolis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли колонка parent_id
    cursor.execute("PRAGMA table_info(cat_comments)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    if 'parent_id' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE cat_comments ADD COLUMN parent_id INTEGER REFERENCES cat_comments(id)")
            print("✅ Добавлена колонка parent_id")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    else:
        print("✅ Колонка parent_id уже существует")
    
    conn.commit()
    conn.close()
    print("✅ Готово!")

if __name__ == "__main__":
    add_parent_id_column()