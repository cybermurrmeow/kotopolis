# update_all_photos.py
from app import app, db
from models import Cat

# Новые рабочие ссылки на GIF (с GIPHY и Imgur — стабильнее Tenor)
new_photos = {
    "Барсик": "https://i.imgur.com/C0iXc5n.gif",
    "Мурка": "https://i.imgur.com/JBsjR8H.gif",
    "Рыжик": "https://i.imgur.com/Cg9menh.gif",
    "Софи": "https://i.imgur.com/FDLLkmQ.gif",
    "Тимофей": "https://i.imgur.com/0ktvWM1.gif",
    "Люся": "https://i.imgur.com/Kzbdxax.gif",
    "Пушок": "https://i.imgur.com/OSjMu71.gif",
    "Джесси": "https://i.imgur.com/X8nt9Qm.gif",
    "Маркиз": "https://i.imgur.com/hS1Qw3p.gif",
    "Боня": "https://i.imgur.com/WvSmWKi.gif",
    "Снежок": "https://i.imgur.com/yeU1hDZ.gif",
    "Шерхан": "https://i.imgur.com/LcapDKf.gif",
    "Карамелька": "https://i.imgur.com/dxYK1L5.gif",
    "Граф": "https://i.imgur.com/CNSqUCh.gif",
    "Зефирка": "https://i.imgur.com/0irP0vl.gif",
    "Мартин": "https://i.imgur.com/reAnRRD.gif",
    "Леди": "https://i.imgur.com/0MWIZ21.gif",
    "Тоша": "https://i.imgur.com/8u7XhMb.gif",
    "Симба": "https://i.imgur.com/v6Nswyx.gif",
    "Жозефина": "https://i.imgur.com/AehM3ph.gif",
}

with app.app_context():
    updated = 0
    not_found = []
    
    for name, url in new_photos.items():
        cat = Cat.query.filter_by(name=name).first()
        if cat:
            cat.photo_path = url
            updated += 1
            print(f"✅ {name} — фото обновлено")
        else:
            not_found.append(name)
            print(f"❌ {name} — не найден в базе")
    
    db.session.commit()
    
    print("\n" + "="*50)
    print(f"📊 ИТОГИ:")
    print(f"   ✅ Обновлено: {updated} котиков")
    print(f"   ❌ Не найдено: {len(not_found)}")
    if not_found:
        print(f"   Список не найденных: {', '.join(not_found)}")
    print("="*50)