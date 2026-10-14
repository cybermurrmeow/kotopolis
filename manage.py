import argparse
import getpass
import os
from pathlib import Path
import re

from werkzeug.security import generate_password_hash

from app import app
from media import create_catalog_previews
from models import Cat, User, db
from passwords import password_errors

DEMO_CATS = [
    {
        "name": "Персик",
        "age": 2,
        "gender": "Мальчик",
        "breed": "Метис",
        "color": "Рыжий",
        "status": "В приюте",
        "mood": "Игривое",
        "personality": "Общительный и любопытный",
        "description": "Любит игрушки и быстро привыкает к людям.",
        "is_vaccinated": True,
        "is_sterilized": True,
        "kids_friendly": True,
        "cats_friendly": True,
    },
    {
        "name": "Луна",
        "age": 4,
        "gender": "Девочка",
        "breed": "Домашняя короткошёрстная",
        "color": "Серая",
        "status": "В приюте",
        "mood": "Спокойное",
        "personality": "Независимая, но ласковая",
        "description": "Подойдёт для тихого дома без суеты.",
        "is_vaccinated": True,
        "is_sterilized": True,
        "cats_friendly": False,
    },
    {
        "name": "Тиша",
        "age": 7,
        "gender": "Мальчик",
        "breed": "Метис",
        "color": "Чёрно-белый",
        "status": "На лечении",
        "mood": "Спокойное",
        "personality": "Тихий и терпеливый",
        "description": "Сейчас восстанавливается и ждёт будущего хозяина.",
        "is_vaccinated": False,
        "is_sterilized": True,
    },
]


def seed_demo():
    with app.app_context():
        if Cat.query.first() is not None:
            print("Cats table is not empty; demo data was not added.")
            return
        db.session.add_all(Cat(**item) for item in DEMO_CATS)
        db.session.commit()
    print("Demo cats added.")


def create_admin():
    username = input("Username: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass.getpass("Password: ")

    if not 3 <= len(username) <= 30 or not re.fullmatch(
        r"[a-zA-Z0-9_а-яА-ЯёЁ-]+", username
    ):
        raise SystemExit(
            "Use a 3-30 character username containing letters, digits, _ or -."
        )
    if len(email) > 120 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise SystemExit("Provide a valid email address.")
    errors = password_errors(password, username, email)
    if errors:
        raise SystemExit("; ".join(errors))

    with app.app_context():
        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            raise SystemExit("This username already exists.")
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
            role="admin",
            email_confirmed=True,
        )
        db.session.add(user)
        db.session.commit()
    print("Admin account created.")


def rebuild_previews():
    upload_folder = app.config["UPLOAD_FOLDER"]
    rebuilt = 0
    skipped = 0

    with app.app_context():
        for cat in Cat.query.order_by(Cat.id).all():
            photo_path = cat.photo_path or ""
            prefix = "uploads/cat_media/"
            if not photo_path.startswith(prefix):
                skipped += 1
                continue

            source = (Path(upload_folder) / photo_path.removeprefix(prefix)).resolve()
            if not source.is_relative_to(Path(upload_folder).resolve()):
                skipped += 1
                continue
            if not os.path.isfile(source):
                skipped += 1
                continue

            create_catalog_previews(
                source,
                os.path.join(upload_folder, "catalog_previews"),
            )
            rebuilt += 1

    print(f"Previews rebuilt: {rebuilt}; skipped: {skipped}.")


def main():
    parser = argparse.ArgumentParser(description="Kotopolis project utilities")
    parser.add_argument(
        "command", choices=("seed-demo", "create-admin", "rebuild-previews")
    )
    args = parser.parse_args()
    commands = {
        "seed-demo": seed_demo,
        "create-admin": create_admin,
        "rebuild-previews": rebuild_previews,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
