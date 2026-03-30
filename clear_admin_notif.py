from app import app, db
from models import User, Notification

with app.app_context():
    admin = User.query.filter_by(role='admin').first()
    if admin:
        count = Notification.query.filter_by(user_id=admin.id).delete()
        db.session.commit()
        print(f"🗑️ Удалено {count} уведомлений администратора")
    else:
        print("❌ Администратор не найден")