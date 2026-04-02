# restore_data.py
from app import app, db
from models import User, Cat
import json
from werkzeug.security import generate_password_hash

with app.app_context():
    with open('backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Восстанавливаем пользователей
    for user_data in data['users']:
        if not User.query.filter_by(username=user_data['username']).first():
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role'],
                email_confirmed=True
            )
            db.session.add(user)
    
    # Восстанавливаем котиков
    for cat_data in data['cats']:
        if not Cat.query.filter_by(name=cat_data['name']).first():
            cat = Cat(**cat_data)
            db.session.add(cat)
    
    db.session.commit()
    print(f"✅ Восстановлено: {len(data['users'])} пользователей, {len(data['cats'])} котиков")