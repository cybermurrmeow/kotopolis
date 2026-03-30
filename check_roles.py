from app import app, db
from models import User

with app.app_context():
    users = User.query.all()
    print("Текущие роли в базе данных:")
    print("=" * 40)
    for user in users:
        print(f"{user.username}: {user.role}")