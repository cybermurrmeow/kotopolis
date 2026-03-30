from app import app, db
from models import User, Notification
from datetime import datetime

def create_test_notifications():
    with app.app_context():
        # Получаем первого пользователя
        user = User.query.first()
        
        if not user:
            print("❌ Нет пользователей в базе")
            return
        
        # Создаём тестовые уведомления
        test_notifications = [
            {
                'title': '🐱 Новый котик!',
                'message': 'В приют поступил новый котик Барсик!',
                'type': 'success',
                'link': '/cats'
            },
            {
                'title': '✅ Заявка одобрена!',
                'message': 'Ваша заявка на усыновление одобрена!',
                'type': 'success',
                'link': '/adoption_requests'
            },
            {
                'title': '💉 Напоминание о прививке',
                'message': 'У котика Мурки скоро прививка!',
                'type': 'warning',
                'link': '/cats'
            },
            {
                'title': '❌ Заявка отклонена',
                'message': 'Ваша заявка на усыновление отклонена.',
                'type': 'danger',
                'link': '/adoption_requests'
            },
            {
                'title': '💬 Новый комментарий',
                'message': 'Пользователь Admin оставил комментарий на странице котика',
                'type': 'info',
                'link': '/cats'
            }
        ]
        
        for notif in test_notifications:
            notification = Notification(
                user_id=user.id,
                title=notif['title'],
                message=notif['message'],
                type=notif['type'],
                link=notif['link'],
                is_read=False
            )
            db.session.add(notification)
        
        db.session.commit()
        print(f"✅ Создано {len(test_notifications)} тестовых уведомлений для пользователя {user.username}")
        print(f"🔔 Теперь проверьте иконку колокольчика на сайте!")

if __name__ == "__main__":
    create_test_notifications()