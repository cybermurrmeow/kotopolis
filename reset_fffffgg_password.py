from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User.query.filter_by(username='fffffgg').first()
    
    if user:
        new_password = '12345'
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        print(f'✅ Пароль пользователя {user.username} изменён на "{new_password}"')
        print(f'   Теперь вы можете войти с логином: {user.username} и паролем: {new_password}')
    else:
        print('❌ Пользователь fffffgg не найден')
        print('Доступные пользователи:')
        users = User.query.all()
        for u in users:
            print(f'  - {u.username}')