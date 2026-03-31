# add_emoji_column.py
import sqlite3

# Путь к вашей базе данных
db_path = 'instance/kotopolis.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Добавляем колонку
    cursor.execute("ALTER TABLE users ADD COLUMN avatar_emoji VARCHAR(10) DEFAULT '🐱'")
    conn.commit()
    print("✅ Колонка avatar_emoji добавлена")
    
    # Проверяем
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\n📊 Колонки в таблице users:")
    for col in columns:
        print(f"   {col[1]} ({col[2]})")
    
    conn.close()
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("⚠️ Колонка avatar_emoji уже существует")
    else:
        print(f"❌ Ошибка: {e}")