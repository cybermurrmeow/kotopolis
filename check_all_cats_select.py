import sqlite3

conn = sqlite3.connect('instance/kotopolis.db')
c = conn.cursor()

c.execute('SELECT name, personality, activity_level, vocal FROM cats ORDER BY name')
rows = c.fetchall()

print("="*70)
print("ПРОВЕРКА ВСЕХ 20 КОТОВ")
print("="*70)
print(f"{'Имя':<12} {'Характер':<15} {'Активность':<12} {'Голос':<15}")
print("-"*70)

for row in rows:
    name = row[0]
    pers = row[1] if row[1] else "❌ НЕТ"
    act = row[2] if row[2] else "❌ НЕТ"
    voc = row[3] if row[3] else "❌ НЕТ"
    print(f"{name:<12} {pers:<15} {act:<12} {voc:<15}")

conn.close()