import os
from pathlib import Path

import pytest
from dotenv import dotenv_values
from flask_login import UserMixin
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def configure_test_database():
    config = Path("/root/kotopolis-test-db.env")
    values = dotenv_values(config)
    url = values.get("TEST_DATABASE_URL")

    if not url:
        raise RuntimeError("Test database is not configured")

    parsed = make_url(url)

    if (
        parsed.database != "kotopolis_test"
        or parsed.username != "kotopolis_test_runner"
    ):
        raise RuntimeError("Unsafe test database configuration")

    engine = create_engine(url)

    try:
        with engine.connect() as connection:
            database, username = connection.execute(
                text("SELECT current_database(), current_user")
            ).one()

            if (
                database != "kotopolis_test"
                or username != "kotopolis_test_runner"
            ):
                raise RuntimeError("Wrong database connection")
    finally:
        engine.dispose()

    os.environ["DATABASE_URL"] = url


configure_test_database()

from app import app
from models import db


class TestAccount(UserMixin):
    def __init__(self, role="user", must_change_password=False):
        self.id = -999999
        self.username = "test_account"
        self.email = "test@example.invalid"
        self.role = role
        self.email_confirmed = True
        self.must_change_password = must_change_password
        self.is_admin = role == "admin"
        self.password = "test-only-password-hash"


@pytest.fixture(autouse=True)
def safe_test_settings(monkeypatch):
    with app.app_context():
        if db.engine.url.database != "kotopolis_test":
            raise RuntimeError("Tests cannot use production database")

    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "WTF_CSRF_ENABLED", False)


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture
def logged_in_client(monkeypatch):
    def create(role="user", must_change_password=False):
        account = TestAccount(
            role=role,
            must_change_password=must_change_password,
        )

        monkeypatch.setattr(
            app.login_manager,
            "_user_callback",
            lambda user_id: account,
        )

        client = app.test_client()

        with client.session_transaction() as session:
            session["_user_id"] = str(account.id)
            session["_fresh"] = True

        return client

    return create
