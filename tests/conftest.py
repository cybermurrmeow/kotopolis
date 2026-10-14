import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ["SECRET_KEY"] = "test-only-secret-key"
# This suite owns only an in-memory database, never a configurable database.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["COOKIE_SECURE"] = "false"
os.environ["RATELIMIT_ENABLED"] = "false"

from app import app as flask_app  # noqa: E402
from models import db  # noqa: E402


@pytest.fixture()
def app(tmp_path):
    original_config = dict(flask_app.config)
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        MAIL_SUPPRESS_SEND=True,
        STORY_STATE_DIR=str(tmp_path / "story"),
        UPLOAD_FOLDER=str(tmp_path / "media"),
    )

    with flask_app.app_context():
        test_engine = db.engine
        if (
            test_engine.url.get_backend_name() != "sqlite"
            or test_engine.url.database != ":memory:"
        ):
            raise RuntimeError(
                "Refusing to create or drop tables outside in-memory SQLite"
            )
        with test_engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys = ON")
        db.create_all()
    try:
        yield flask_app
    finally:
        with flask_app.app_context():
            db.session.remove()
            db.metadata.drop_all(bind=test_engine)
        flask_app.config.clear()
        flask_app.config.update(original_config)


@pytest.fixture()
def client(app):
    return app.test_client()
