from app import app, db
from models import Notification

with app.app_context():
    # Удаляем все демо-уведомления
    demo_titles = [
        '🐱 ДЕМО: Новый котик',
        '📝 ДЕМО: Новая заявка',
        '✅ ДЕМО: Заявка одобрена',
        '❌ ДЕМО: Заявка отклонена',
        '💉 ДЕМО: Прививка просрочена',
        '🏥 ДЕМО: Котик на лечении',
        '💬 ДЕМО: Новый комментарий',
        '🔔 ДЕМО: Тестовое уведомление'
    ]
    
    deleted = Notification.query.filter(Notification.title.in_(demo_titles)).delete()
    db.session.commit()
    
    print(f"🗑️ Удалено {deleted} демо-уведомлений")