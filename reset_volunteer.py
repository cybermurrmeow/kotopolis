from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Проверяем, есть ли волонтёр
    volunteer = User.query.filter_by(username='volunteer').first()
    
    if volunteer:
        print(f'✅ Волонтёр найден: {volunteer.username}')
        print(f'Email: {volunteer.email}')
        
        # Сбрасываем пароль
        volunteer.password = generate_password_hash('volunteer123')
        db.session.commit()
        print('✅ Пароль волонтёра сброшен на volunteer123')
    else:
        print('❌ Волонтёр не найден, создаём...')
        volunteer = User(
            username='volunteer',
            email='volunteer@kotopolis.ru',
            password=generate_password_hash('volunteer123'),
            role='volunteer',
            email_confirmed=1
        )
        db.session.add(volunteer)
        db.session.commit()
        print('✅ Волонтёр создан: volunteer / volunteer123')
    
    # Проверим всех пользователей
    print('\n📋 Все пользователи в базе:')
    users = User.query.all()
    for user in users:
        print(f'   - {user.username} ({user.role}) - email: {user.email}')