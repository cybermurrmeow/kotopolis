# backup_data.py
from app import app, db
from models import User, Cat, AdoptionRequest, CatComment
import json
from datetime import datetime

with app.app_context():
    data = {
        'users': [],
        'cats': [],
        'adoption_requests': [],
        'comments': []
    }
    
    # Сохраняем пользователей
    for user in User.query.all():
        data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'email_confirmed': user.email_confirmed,
            'bio': user.bio
        })
    
    # Сохраняем котиков
    for cat in Cat.query.all():
        data['cats'].append({
            'id': cat.id,
            'name': cat.name,
            'nickname': cat.nickname,
            'age': cat.age,
            'breed': cat.breed,
            'gender': cat.gender,
            'color': cat.color,
            'weight': cat.weight,
            'mood': cat.mood,
            'status': cat.status,
            'photo_path': cat.photo_path,
            'is_vaccinated': cat.is_vaccinated,
            'is_sterilized': cat.is_sterilized,
            'last_vacc_date': cat.last_vacc_date.isoformat() if cat.last_vacc_date else None,
            'next_vacc_date': cat.next_vacc_date.isoformat() if cat.next_vacc_date else None,
            'adoption_date': cat.adoption_date.isoformat() if cat.adoption_date else None
        })
    
    # Сохраняем в файл
    with open('backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Сохранено: {len(data['users'])} пользователей, {len(data['cats'])} котиков")