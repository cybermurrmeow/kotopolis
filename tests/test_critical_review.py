import importlib.util
import re
from pathlib import Path
from unittest.mock import patch

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from PIL import Image

from app import send_password_reset_email
from media import create_catalog_previews
from models import AdoptionRequest, Cat, CatComment, User, db
from test_app import create_user, login


def test_reset_email_ignores_untrusted_host(app):
    user_id = create_user(app)
    app.config.update(
        MAIL_USERNAME="test",
        MAIL_PASSWORD="test",
        PUBLIC_BASE_URL="https://meowly.space",
    )
    try:
        with app.test_request_context(
            headers={"Host": "evil.example", "X-Forwarded-Host": "evil.example"}
        ):
            with patch("app.mail.send") as send:
                assert send_password_reset_email(db.session.get(User, user_id))
                html = send.call_args.args[0].html
                assert 'href="https://meowly.space/reset_password/' in html
                assert "evil.example" not in html
    finally:
        app.config.update(
            MAIL_USERNAME=None,
            MAIL_PASSWORD=None,
            PUBLIC_BASE_URL="http://127.0.0.1:5000",
        )


def test_csrf_rejects_missing_token_and_accepts_valid_token(client, app):
    app.config["WTF_CSRF_ENABLED"] = True
    assert client.post("/guest_login").status_code == 400
    assert client.post("/login", data={"csrf_token": "forged"}).status_code == 400
    html = client.get("/login").get_data(as_text=True)
    token = re.search(r'name="csrf_token"\s+value="([^"]+)"', html).group(1)
    assert client.post("/guest_login", data={"csrf_token": token}).status_code == 302
    assert client.post("/logout").status_code == 400
    assert client.post("/logout", data={"csrf_token": token}).status_code == 302


def test_all_mutating_routes_require_csrf(client, app):
    app.config["WTF_CSRF_ENABLED"] = True
    for rule in app.url_map.iter_rules():
        if "POST" not in rule.methods:
            continue
        path = re.sub(r"<int:[^>]+>", "1", rule.rule)
        path = re.sub(r"<[^>]+>", "invalid-token", path)
        assert client.post(path).status_code == 400, path


def test_edit_profile_script_is_outside_title(client, app):
    create_user(app)
    login(client)
    html = client.get("/edit_profile").get_data(as_text=True)
    title = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    assert "<script" not in title
    assert 'document.addEventListener("DOMContentLoaded"' in html


def test_large_animation_is_rejected_before_frame_conversion(tmp_path):
    source = tmp_path / "large.gif"
    frames = [Image.new("RGB", (20, 20), (number, 0, 0)) for number in range(40)]
    frames[0].save(source, save_all=True, append_images=frames[1:], duration=50)
    with patch("media._prepare_frame") as prepare:
        with pytest.raises(ValueError, match="Анимация"):
            create_catalog_previews(source, tmp_path / "previews")
        prepare.assert_not_called()


@pytest.mark.parametrize("existing", [False, True])
def test_password_migration_handles_existing_column(existing):
    path = (
        Path(__file__).resolve().parents[1]
        / "migrations/versions/b78b1f412a0c_roles_and_temporary_passwords.py"
    )
    spec = importlib.util.spec_from_file_location("password_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    engine = sa.create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        columns = "id INTEGER PRIMARY KEY, role VARCHAR(50) NOT NULL"
        if existing:
            columns += ", must_change_password BOOLEAN"
        connection.execute(sa.text(f"CREATE TABLE users ({columns})"))
        if existing:
            connection.execute(
                sa.text(
                    "INSERT INTO users VALUES (1, 'user', TRUE), (2, 'legacy', NULL)"
                )
            )
        else:
            connection.execute(
                sa.text("INSERT INTO users VALUES (1, 'user'), (2, 'legacy')")
            )
        with Operations.context(MigrationContext.configure(connection)):
            migration.upgrade()
        rows = connection.execute(
            sa.text("SELECT role, must_change_password FROM users ORDER BY id")
        ).all()
        assert rows[0] == ("user", int(existing))
        assert rows[1] == ("user", 0)
        assert not next(
            c
            for c in sa.inspect(connection).get_columns("users")
            if c["name"] == "must_change_password"
        )["nullable"]
    engine.dispose()


def test_history_cannot_be_deleted_by_admin(client, app):
    create_user(app, "admin", "admin")
    user_id = create_user(app)
    with app.app_context():
        cat = Cat(name="История", status="В приюте")
        db.session.add(cat)
        db.session.flush()
        adoption = AdoptionRequest(
            cat_id=cat.id,
            user_id=user_id,
            adopter_name="Test",
            email="test@example.com",
            status="Отменена",
        )
        comment = CatComment(
            cat_id=cat.id, user_id=user_id, comment="Historical comment"
        )
        db.session.add_all([adoption, comment])
        db.session.commit()
        cat_id, request_id, comment_id = cat.id, adoption.id, comment.id
    login(client, "admin")
    for path in [
        f"/delete_cat/{cat_id}",
        f"/user/{user_id}/delete",
        f"/adoption_request/{request_id}/delete",
    ]:
        assert client.post(path).status_code == 302
    with app.app_context():
        assert db.session.get(User, user_id)
        assert db.session.get(Cat, cat_id)
        assert db.session.get(AdoptionRequest, request_id)
        assert db.session.get(CatComment, comment_id)
