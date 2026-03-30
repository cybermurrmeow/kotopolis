import sqlite3
import os

def add_user_id_column():
    db_path = 'instance/kotopolis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли колонка user_id
    cursor.execute("PRAGMA table_info(adoption_requests)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print("📋 Существующие колонки в adoption_requests:")
    for col in existing_columns:
        print(f"   - {col}")
    
    if 'user_id' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE adoption_requests ADD COLUMN user_id INTEGER")
            print("\n✅ Добавлена колонка user_id")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
    else:
        print("\n✅ Колонка user_id уже существует")
    
    conn.commit()
    conn.close()
    print("\n✅ Готово!")

if __name__ == "__main__":
    add_user_id_column()