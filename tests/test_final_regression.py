import importlib.util
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from PIL import Image
from werkzeug.datastructures import FileStorage

from media import media_paths, save_cat_media
from models import Cat, User, db
from test_app import create_user, login


def test_integrity_migration_refuses_to_remove_conflicting_history():
    path = (
        Path(__file__).resolve().parents[1]
        / "migrations/versions/c12ea302f004_adoption_integrity.py"
    )
    spec = importlib.util.spec_from_file_location("integrity_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE adoption_requests (id INTEGER PRIMARY KEY, user_id INTEGER, cat_id INTEGER, status TEXT)"
        )
        connection.exec_driver_sql(
            "INSERT INTO adoption_requests VALUES (1, 1, 1, 'Новая'), (2, 1, 1, 'На рассмотрении')"
        )
        with Operations.context(MigrationContext.configure(connection)):
            with pytest.raises(RuntimeError, match="Conflicting historical"):
                migration.upgrade()
        assert (
            connection.exec_driver_sql(
                "SELECT COUNT(*) FROM adoption_requests"
            ).scalar_one()
            == 2
        )
        assert not sa.inspect(connection).get_indexes("adoption_requests")
    engine.dispose()


@pytest.mark.parametrize("failure_stage", ["upload", "preview"])
def test_failed_preview_generation_cleans_only_its_files(tmp_path, failure_stage):
    image = BytesIO()
    Image.new("RGB", (10, 10), "red").save(image, "PNG")
    image.seek(0)
    upload = FileStorage(image, filename="cat.png")
    form = SimpleNamespace(
        photo=SimpleNamespace(data=upload), gif_url=SimpleNamespace(data="")
    )
    sentinel = tmp_path / "keep.txt"
    sentinel.write_text("existing user data", encoding="utf-8")

    def fail(source, directory):
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{source.stem}-poster.webp").write_bytes(b"partial")
        raise OSError("failed encoder")

    def fail_upload(target):
        target.write_bytes(b"partial upload")
        raise OSError("failed storage")

    target = upload if failure_stage == "upload" else None
    patcher = (
        patch.object(target, "save", side_effect=fail_upload)
        if target
        else patch("media.create_catalog_previews", side_effect=fail)
    )
    with patcher:
        with pytest.raises(ValueError, match="обработать"):
            save_cat_media(form, tmp_path)
    assert sentinel.read_text(encoding="utf-8") == "existing user data"
    assert not list(tmp_path.glob("*.png"))
    assert not list(tmp_path.rglob("*.webp"))


def test_media_path_traversal_and_missing_file_use_placeholder(tmp_path):
    for path in ("../../private.png", "uploads/cat_media/missing.png"):
        assert media_paths(path, tmp_path)["poster"] == "img/cat-placeholder.svg"


def test_cat_details_escapes_untrusted_name(client, app):
    create_user(app)
    with app.app_context():
        cat = Cat(name="<script>alert(1)</script>", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id
    login(client)
    html = client.get(f"/cat/{cat_id}").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_unconfirmed_account_cannot_use_existing_session(client, app):
    user_id = create_user(app)
    login(client)
    with app.app_context():
        db.session.get(User, user_id).email_confirmed = False
        db.session.commit()
    response = client.get("/profile")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/resend_confirmation")


def test_case_insensitive_username_is_unique_in_database(app):
    create_user(app, "Student")
    with app.app_context():
        user = User(username="student", email="other@example.com", role="user")
        user.set_password("StrongPass123")
        db.session.add(user)
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        assert User.query.count() == 1


@pytest.mark.parametrize("collision", [False, True])
def test_username_migration_preflight_preserves_users(collision):
    path = (
        Path(__file__).resolve().parents[1]
        / "migrations/versions/d02f042bae17_username_uniqueness.py"
    )
    spec = importlib.util.spec_from_file_location("username_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL)"
        )
        connection.execute(
            sa.text("INSERT INTO users VALUES (1, 'Student'), (2, :name)"),
            {"name": "student" if collision else "another"},
        )
        with Operations.context(MigrationContext.configure(connection)):
            if collision:
                with pytest.raises(RuntimeError, match="collisions"):
                    migration.upgrade()
            else:
                migration.upgrade()
        assert (
            connection.exec_driver_sql("SELECT COUNT(*) FROM users").scalar_one() == 2
        )
        indexes = (
            connection.exec_driver_sql(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            .scalars()
            .all()
        )
        assert ("uq_users_username_lower" in indexes) is not collision
    engine.dispose()
