from app import app, db
from models import Notification

with app.app_context():
    db.create_all()
    print('✅ Таблица notifications создана')