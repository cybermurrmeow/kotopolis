import sqlite3
import os

def add_profile_columns():
    db_path = 'instance/kotopolis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем существующие колонки
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print("📋 Существующие колонки в таблице users:")
    for col in existing_columns:
        print(f"   - {col}")
    
    # Добавляем avatar
    if 'avatar' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN avatar VARCHAR(200)")
            print("\n✅ Добавлена колонка avatar")
        except Exception as e:
            print(f"\n❌ Ошибка при добавлении avatar: {e}")
    else:
        print("\n✅ Колонка avatar уже существует")
    
    # Добавляем bio
    if 'bio' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT")
            print("✅ Добавлена колонка bio")
        except Exception as e:
            print(f"❌ Ошибка при добавлении bio: {e}")
    else:
        print("✅ Колонка bio уже существует")
    
    conn.commit()
    conn.close()
    print("\n✅ Готово!")

if __name__ == "__main__":
    add_profile_columns()