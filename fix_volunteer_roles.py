from app import app, db
from models import User

with app.app_context():
    # Список пользователей, которые должны быть волонтёрами (только volunteer)
    volunteer_users = ['volunteer']
    
    # Список пользователей, которые должны быть обычными пользователями
    normal_users = ['fffffgg', 'ssss', 'testuser', 'test']
    
    # Список админов
    admin_users = ['admin']
    
    # Обновляем роли
    for user in User.query.all():
        if user.username in volunteer_users:
            user.role = 'volunteer'
            print(f"✅ {user.username} → волонтёр")
        elif user.username in admin_users:
            user.role = 'admin'
            print(f"✅ {user.username} → админ")
        elif user.username in normal_users:
            user.role = 'user'
            print(f"✅ {user.username} → обычный пользователь")
        else:
            # Остальным ставим роль 'user'
            user.role = 'user'
            print(f"✅ {user.username} → обычный пользователь")
    
    db.session.commit()
    
    print("\n📊 ИТОГОВЫЕ РОЛИ:")
    for user in User.query.all():
        print(f"   {user.username}: {user.role}")