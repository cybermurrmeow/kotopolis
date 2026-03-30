from app import app, db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

with app.app_context():
    # Проверяем, есть ли админ
    admin = User.query.filter_by(username='admin').first()
    
    if admin:
        print(f'Админ найден: {admin.username}')
        print(f'Email: {admin.email}')
        
        # Сбрасываем пароль
        admin.password = generate_password_hash('admin123')
        db.session.commit()
        print('✅ Пароль админа сброшен на admin123')
        
        # Проверяем
        test = check_password_hash(admin.password, 'admin123')
        print(f'Проверка пароля: {test}')
    else:
        print('❌ Админ не найден, создаём...')
        admin = User(
            username='admin',
            email='admin@kotopolis.ru',
            password=generate_password_hash('admin123'),
            role='admin',
            email_confirmed=1
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Админ создан: admin / admin123')