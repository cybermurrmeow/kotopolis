"""
БЕЗОПАСНОЕ ДОБАВЛЕНИЕ ПОЛЕЙ email_confirmed И email_confirmed_at
НЕ УДАЛЯЕТ СУЩЕСТВУЮЩИЕ ДАННЫЕ
"""

import sqlite3
import os

DB_PATH = 'instance/kotopolis.db'

def add_email_columns():
    print("\n" + "="*60)
    print("🔧 ДОБАВЛЕНИЕ ПОЛЕЙ ДЛЯ ПОДТВЕРЖДЕНИЯ EMAIL")
    print("="*60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена: {DB_PATH}")
        return False
    
    print(f"✅ База данных найдена")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем существующие колонки
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    print(f"\n📋 Существующие поля в таблице users:")
    for col in existing_columns:
        print(f"   - {col}")
    
    added = []
    
    # Добавляем email_confirmed
    if 'email_confirmed' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_confirmed BOOLEAN DEFAULT 0")
            added.append('email_confirmed')
            print(f"\n✅ Добавлено поле: email_confirmed (по умолчанию = 0)")
        except Exception as e:
            print(f"\n❌ Ошибка при добавлении email_confirmed: {e}")
    else:
        print(f"\n✅ Поле email_confirmed уже существует")
    
    # Добавляем email_confirmed_at
    if 'email_confirmed_at' not in existing_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email_confirmed_at TIMESTAMP")
            added.append('email_confirmed_at')
            print(f"✅ Добавлено поле: email_confirmed_at")
        except Exception as e:
            print(f"❌ Ошибка при добавлении email_confirmed_at: {e}")
    else:
        print(f"✅ Поле email_confirmed_at уже существует")
    
    # Показываем итоговую структуру
    print("\n📊 Итоговая структура таблицы users:")
    cursor.execute("PRAGMA table_info(users)")
    for col in cursor.fetchall():
        marker = "🆕" if col[1] in added else "  "
        print(f"   {marker} {col[1]} ({col[2]})")
    
    # Показываем количество пользователей
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\n👥 В таблице {user_count} пользователей (данные сохранены)")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ ГОТОВО! Поля добавлены, данные не потеряны.")
    print("="*60)
    return True

if __name__ == '__main__':
    add_email_columns()