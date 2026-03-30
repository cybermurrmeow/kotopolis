from app import app, db
import sqlite3
import os

def add_columns():
    db_path = 'instance/kotopolis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем существующие колонки
    cursor.execute("PRAGMA table_info(cats)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print("📋 Существующие колонки в таблице cats:")
    for col in existing_columns:
        print(f"   - {col}")
    
    # Новые колонки для добавления
    new_columns = [
        ("personality", "TEXT"),
        ("activity_level", "VARCHAR(200)"),
        ("kids_friendly", "BOOLEAN DEFAULT 1"),
        ("cats_friendly", "BOOLEAN DEFAULT 1"),
        ("dogs_friendly", "BOOLEAN DEFAULT 1"),
        ("favorite_place", "VARCHAR(200)"),
        ("vocal", "VARCHAR(100)"),
        ("food_preferences", "TEXT"),
        ("story", "TEXT"),
        ("adoption_recommendation", "TEXT")
    ]
    
    print("\n🔧 Добавляем новые колонки:")
    added = []
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE cats ADD COLUMN {col_name} {col_type}")
                added.append(col_name)
                print(f"   ✅ Добавлена: {col_name}")
            except Exception as e:
                print(f"   ❌ Ошибка: {col_name} - {e}")
        else:
            print(f"   ⚠️ Уже есть: {col_name}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print(f"✅ Добавлено {len(added)} новых колонок")
    print("="*50)

if __name__ == "__main__":
    add_columns()