from app import app, db
from models import Notification

with app.app_context():
    count = Notification.query.count()
    Notification.query.delete()
    db.session.commit()
    print(f"🗑️ Удалено {count} уведомлений")