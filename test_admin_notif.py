from app import app, db
from models import User, Notification
from werkzeug.security import generate_password_hash

def create_admin_notifications():
    with app.app_context():
        # Находим администратора
        admin = User.query.filter_by(role='admin').first()
        
        if not admin:
            print("❌ Администратор не найден! Создаём...")
            admin = User(
                username='admin',
                email='admin@kotopolis.ru',
                password=generate_password_hash('admin123'),
                role='admin',
                email_confirmed=1
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Администратор создан: admin / admin123")
        
        # Удаляем старые тестовые уведомления
        Notification.query.filter(
            Notification.user_id == admin.id,
            Notification.title.in_([
                '🐱 Новый котик в приюте!',
                '📝 Новая заявка на усыновление',
                '💉 Внимание! Просрочена прививка',
                '🏥 Котик нуждается в лечении',
                '✅ Заявка одобрена',
                '💬 Новый комментарий'
            ])
        ).delete()
        
        # Создаём новые уведомления
        notifications = [
            {
                'title': '🐱 Новый котик в приюте!',
                'message': 'В приют поступил новый котик "Мурзик". Требуется осмотр и вакцинация.',
                'type': 'success',
                'link': '/cats'
            },
            {
                'title': '📝 Новая заявка на усыновление',
                'message': 'Пользователь "Анна Иванова" подал заявку на усыновление котика "Барсик".',
                'type': 'info',
                'link': '/adoption_requests'
            },
            {
                'title': '💉 Внимание! Просрочена прививка',
                'message': 'У котика "Рыжик" просрочена прививка! Требуется вакцинация.',
                'type': 'danger',
                'link': '/edit_cat/1'
            },
            {
                'title': '🏥 Котик нуждается в лечении',
                'message': 'Котик "Снежок" переведён на лечение. Нужна помощь в уходе.',
                'type': 'warning',
                'link': '/cats'
            },
            {
                'title': '✅ Заявка одобрена',
                'message': 'Заявка на усыновление котика "Мурка" одобрена!',
                'type': 'success',
                'link': '/adoption_requests'
            },
            {
                'title': '💬 Новый комментарий',
                'message': 'Пользователь "Волонтёр" оставил комментарий на странице котика "Барсик".',
                'type': 'info',
                'link': '/cats'
            }
        ]
        
        for notif in notifications:
            notification = Notification(
                user_id=admin.id,
                title=notif['title'],
                message=notif['message'],
                type=notif['type'],
                link=notif['link'],
                is_read=False
            )
            db.session.add(notification)
        
        db.session.commit()
        print(f"✅ Создано {len(notifications)} тестовых уведомлений для администратора {admin.username}")
        print(f"🔔 Теперь проверьте иконку колокольчика на сайте!")
        print(f"\n📋 Уведомления:")
        for n in notifications:
            print(f"   - {n['title']}")

if __name__ == "__main__":
    create_admin_notifications()