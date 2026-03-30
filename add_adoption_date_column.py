import sqlite3
import os

def add_adoption_date_column():
    db_path = 'instance/kotopolis.db'
    
    if not os.path.exists(db_path):
        print(f"❌ База данных не найдена: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем, есть ли колонка adoption_date
    cursor.execute("PRAGMA table_info(cats)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    if 'adoption_date' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE cats ADD COLUMN adoption_date DATE")
            print("✅ Добавлена колонка adoption_date")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    else:
        print("✅ Колонка adoption_date уже существует")
    
    conn.commit()
    conn.close()
    print("✅ Готово!")

if __name__ == "__main__":
    add_adoption_date_column()