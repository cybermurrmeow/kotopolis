# add_bio_direct.py
import psycopg2

# Данные для подключения к вашей базе PostgreSQL на Render
conn = psycopg2.connect(
    host="dpg-d762n0chg0os73bemba0-a.oregon-postgres.render.com",
    port=5432,
    database="kotopolis_db",
    user="kotopolis_db_user",
    password="iUw6DqFbyB6FrRxf13OoqbYEw0Ax5upX"
)

cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN bio TEXT;")
    conn.commit()
    print("✅ Колонка bio успешно добавлена!")
except Exception as e:
    print(f"⚠️ Ошибка: {e}")
    print("Возможно, колонка уже существует")

cursor.close()
conn.close()