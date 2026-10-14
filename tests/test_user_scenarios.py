from datetime import timedelta
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image
from sqlalchemy.exc import IntegrityError, OperationalError

from app import serializer
from daily_story import build_story, read_state
from models import AdoptionRequest, Cat, User, db, utc_now
from test_app import create_user, login


def cat(app):
    with app.app_context():
        item = Cat(name="Тест", status="В приюте")
        db.session.add(item)
        db.session.commit()
        return item.id


def request_record(app, user_id, cat_id, status="Новая"):
    with app.app_context():
        record = AdoptionRequest(
            user_id=user_id,
            cat_id=cat_id,
            adopter_name="Test",
            email="test@example.com",
            status=status,
        )
        db.session.add(record)
        db.session.commit()
        return record.id


@pytest.mark.parametrize(
    "path",
    [
        "/users",
        "/add_cat",
        "/adoption_requests",
        "/exports",
        "/export_cats_csv",
        "/export_cats_excel",
        "/export_cats_pdf",
    ],
)
def test_user_cannot_read_admin_resources(client, app, path):
    create_user(app)
    login(client)
    assert client.get(path).status_code == 403


@pytest.mark.parametrize(
    "path",
    [
        "/users/create",
        "/user/1/delete",
        "/user/1/role",
        "/delete_cat/1",
        "/adoption_request/1/status",
        "/adoption_request/1/delete",
    ],
)
def test_user_cannot_mutate_admin_resources(client, app, path):
    create_user(app)
    login(client)
    assert client.post(path).status_code == 403


def test_password_change_invalidates_other_sessions(client, app):
    create_user(app)
    other = app.test_client()
    login(client)
    login(other)
    client.post(
        "/change_password",
        data={
            "old_password": "StrongPass123",
            "new_password": "NewStrong456",
            "confirm_password": "NewStrong456",
        },
    )
    assert client.get("/profile").status_code == 200
    assert other.get("/profile").status_code == 302


def test_reset_token_is_single_use(client, app):
    user_id = create_user(app)
    with app.app_context():
        user = db.session.get(User, user_id)
        token = serializer.dumps(
            {
                "user_id": user.id,
                "email": user.email,
                "password_sig": user.password[-16:],
            },
            salt="password-reset",
        )
    assert (
        client.post(
            f"/reset_password/{token}",
            data={"password": "ChangedPass456", "confirm_password": "ChangedPass456"},
        ).status_code
        == 302
    )
    assert (
        client.get(f"/reset_password/{token}")
        .headers["Location"]
        .endswith("/forgot_password")
    )
    assert (
        client.get("/reset_password/forged-token")
        .headers["Location"]
        .endswith("/forgot_password")
    )


def test_email_code_confirmation_and_failed_attempts(client, app):
    user_id = create_user(app)
    with app.app_context():
        user = db.session.get(User, user_id)
        user.email_confirmed = False
        from werkzeug.security import generate_password_hash

        user.email_code_hash = generate_password_hash("012345")
        user.email_code_expires_at = utc_now() + timedelta(minutes=10)
        db.session.commit()
        ticket = serializer.dumps(
            {"user_id": user.id, "email": user.email}, salt="email-code-context"
        )
    assert (
        client.post(
            "/verify_email?ticket=" + ticket, data={"code": "999999"}
        ).status_code
        == 200
    )
    with app.app_context():
        assert db.session.get(User, user_id).email_code_attempts == 1
    assert (
        client.post(
            "/verify_email?ticket=" + ticket, data={"code": "012345"}
        ).status_code
        == 302
    )
    assert client.get("/profile").status_code == 200


def test_email_change_revokes_access_and_keeps_profile(client, app):
    user_id = create_user(app)
    login(client)
    response = client.post(
        "/edit_profile", data={"username": "updated", "email": "changed@example.com"}
    )
    assert "/verify_email?ticket=" in response.headers["Location"]
    assert client.get("/profile").status_code == 302
    with app.app_context():
        user = db.session.get(User, user_id)
        assert user.username == "updated"
        assert not user.email_confirmed


def test_owner_only_can_cancel_request(client, app):
    owner = create_user(app)
    create_user(app, "other")
    cat_id = cat(app)
    request_id = request_record(app, owner, cat_id)
    login(client, "other")
    assert client.post(f"/cancel_my_request/{request_id}").status_code == 403
    with app.app_context():
        assert db.session.get(AdoptionRequest, request_id).status == "Новая"


def test_approval_closes_other_requests_and_can_be_reversed(client, app):
    create_user(app, "admin", "admin")
    owner = create_user(app)
    other = create_user(app, "other")
    cat_id = cat(app)
    first = request_record(app, owner, cat_id)
    second = request_record(app, other, cat_id)
    login(client, "admin")
    client.post(f"/adoption_request/{first}/status", data={"status": "Одобрена"})
    with app.app_context():
        assert db.session.get(Cat, cat_id).status == "Усыновлён"
        assert db.session.get(AdoptionRequest, second).status == "Отклонена"
    client.post(f"/adoption_request/{first}/status", data={"status": "На рассмотрении"})
    with app.app_context():
        assert db.session.get(Cat, cat_id).status == "В приюте"
        assert db.session.get(Cat, cat_id).adoption_date is None


def test_active_request_unique_index_preserves_history(app):
    owner = create_user(app)
    cat_id = cat(app)
    request_record(app, owner, cat_id)
    with app.app_context():
        db.session.add(
            AdoptionRequest(
                user_id=owner,
                cat_id=cat_id,
                adopter_name="Test",
                email="test@example.com",
                status="Новая",
            )
        )
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        assert AdoptionRequest.query.count() == 1


def test_favorite_does_not_redirect_to_external_referrer(client, app):
    create_user(app)
    cat_id = cat(app)
    login(client)
    response = client.post(
        f"/favorite/{cat_id}", headers={"Referer": "https://evil.example/"}
    )
    assert response.headers["Location"] == "/cats"


def test_upload_creates_previews_and_invalid_upload_is_rejected(client, app):
    create_user(app, "admin", "admin")
    login(client, "admin")
    image = BytesIO()
    Image.new("RGB", (40, 40), "pink").save(image, format="PNG")
    image.seek(0)
    data = {
        "name": "Кот",
        "status": "В приюте",
        "gender": "",
        "mood": "",
        "photo": (image, "cat.png"),
    }
    assert client.post("/add_cat", data=data).status_code == 302
    with app.app_context():
        assert Cat.query.count() == 1
    assert len(list(Path(app.config["UPLOAD_FOLDER"]).rglob("*.webp"))) == 2
    client.post(
        "/add_cat",
        data={
            "name": "Bad",
            "status": "В приюте",
            "gender": "",
            "mood": "",
            "photo": (BytesIO(b"not an image"), "cat.png"),
        },
    )
    with app.app_context():
        assert Cat.query.count() == 1


def test_database_failure_returns_generic_response_and_rolls_back(client, app):
    create_user(app)
    cat_id = cat(app)
    login(client)
    with patch.object(
        db.session,
        "commit",
        side_effect=OperationalError("query", {}, Exception("secret database details")),
    ):
        response = client.post(f"/favorite/{cat_id}")
    assert response.status_code == 503
    assert "secret database details" not in response.get_data(as_text=True)


def test_story_does_not_assign_another_cats_id_based_story():
    story = build_story(Cat(id=1, name="Персик"), 0)["text"]
    assert "Барсик" not in story
    assert "Персик" in story


def test_invalid_story_state_is_ignored(tmp_path):
    state = tmp_path / "state.json"
    state.write_text('{"cycle_shown": null}', encoding="utf-8")
    assert read_state(state) == {}


@pytest.mark.parametrize(
    "path, mime, prefix",
    [
        ("/export_cats_csv", "text/csv", b"\xef\xbb\xbf"),
        (
            "/export_cats_excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            b"PK",
        ),
        ("/export_cats_pdf", "application/pdf", b"%PDF"),
    ],
)
def test_admin_can_download_each_export(client, app, path, mime, prefix):
    create_user(app, "admin", "admin")
    cat(app)
    login(client, "admin")
    response = client.get(path)
    assert response.status_code == 200
    assert response.mimetype == mime
    assert response.data.startswith(prefix)


def test_large_text_and_nan_weight_are_rejected(client, app):
    create_user(app, "admin", "admin")
    login(client, "admin")
    for invalid in ({"health": "x" * 10001}, {"weight": "NaN"}):
        data = {
            "name": "Bad",
            "status": "В приюте",
            "gender": "",
            "mood": "",
            **invalid,
        }
        assert client.post("/add_cat", data=data).status_code == 200
    with app.app_context():
        assert Cat.query.count() == 0


def test_password_mismatch_keeps_hash_unchanged(client, app):
    user_id = create_user(app)
    login(client)
    client.post(
        "/change_password",
        data={
            "old_password": "WrongPass123",
            "new_password": "NewPass456",
            "confirm_password": "NewPass456",
        },
    )
    with app.app_context():
        assert db.session.get(User, user_id).check_password("StrongPass123")


def test_reopening_old_request_does_not_duplicate_active_request(client, app):
    create_user(app, "admin", "admin")
    owner = create_user(app)
    cat_id = cat(app)
    old = request_record(app, owner, cat_id, "Отклонена")
    request_record(app, owner, cat_id)
    login(client, "admin")
    assert (
        client.post(
            f"/adoption_request/{old}/status", data={"status": "Новая"}
        ).status_code
        == 302
    )
    with app.app_context():
        assert db.session.get(AdoptionRequest, old).status == "Отклонена"
