from pathlib import Path

from models import AdoptionRequest, Cat, FavoriteCat, User, db


def create_user(app, username="user", role="user", temporary=False):
    with app.app_context():
        user = User(
            username=username,
            email=f"{username}@example.com",
            role=role,
            email_confirmed=True,
            must_change_password=temporary,
        )
        user.set_password("StrongPass123")
        db.session.add(user)
        db.session.commit()
        return user.id


def login(client, username="user", password="StrongPass123"):
    return client.post(
        "/login",
        data={"username_or_email": username, "password": password},
    )


def test_login_page_loads(client):
    response = client.get("/login")

    assert response.status_code == 200
    assert "Котополис" in response.get_data(as_text=True)


def test_guest_can_open_catalog(client, app):
    with app.app_context():
        db.session.add(Cat(name="Тестовый кот", status="В приюте"))
        db.session.commit()

    login_response = client.post("/guest_login")
    catalog_response = client.get("/cats")

    assert login_response.status_code == 302
    assert catalog_response.status_code == 200
    assert "Тестовый кот" in catalog_response.get_data(as_text=True)


def test_guest_cannot_open_admin_pages(client):
    client.post("/guest_login")
    response = client.get("/users")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/cats")


def test_guest_cannot_use_json_api(client):
    client.post("/guest_login")

    response = client.get("/api/cats")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/cats")


def test_logout_requires_post(client):
    client.post("/guest_login")

    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 302


def test_security_headers_are_present(client):
    response = client.get("/login")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_all_templates_compile(app):
    with app.app_context():
        for template_name in app.jinja_env.list_templates():
            app.jinja_env.get_template(template_name)


def test_registration_creates_regular_user(client, app):
    response = client.post(
        "/register",
        data={
            "username": "new_user",
            "email": "new@example.com",
            "password": "UsefulPass123",
            "confirm_password": "UsefulPass123",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.filter_by(username="new_user").one()
        assert user.role == "user"
        assert user.must_change_password is False


def test_regular_user_cannot_open_admin_area(client, app):
    create_user(app)
    login(client)

    assert client.get("/users").status_code == 403


def test_admin_created_user_must_change_temporary_password(client, app):
    create_user(app, username="admin", role="admin")
    login(client, "admin")

    response = client.post(
        "/users/create",
        data={
            "username": "temporary",
            "email": "temporary@example.com",
            "password": "TempPass123",
            "role": "user",
        },
    )
    assert response.status_code == 302

    client.post("/logout")
    with app.app_context():
        user = User.query.filter_by(username="temporary").one()
        user.email_confirmed = True
        db.session.commit()
        assert user.must_change_password is True

    login(client, "temporary", "TempPass123")
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/change_password")

    response = client.post(
        "/change_password",
        data={
            "old_password": "TempPass123",
            "new_password": "PermanentPass456",
            "confirm_password": "PermanentPass456",
        },
    )
    assert response.status_code == 302
    assert client.get("/dashboard").status_code == 200

    with app.app_context():
        user = User.query.filter_by(username="temporary").one()
        assert user.must_change_password is False
        assert user.check_password("PermanentPass456")


def test_last_admin_cannot_be_demoted_or_deleted(client, app):
    admin_id = create_user(app, username="admin", role="admin")
    login(client, "admin")

    client.post(f"/user/{admin_id}/role", data={"role": "user"})
    client.post(f"/user/{admin_id}/delete")

    with app.app_context():
        admin = db.session.get(User, admin_id)
        assert admin is not None
        assert admin.role == "admin"


def test_favorite_can_be_added_and_removed(client, app):
    user_id = create_user(app)
    with app.app_context():
        cat = Cat(name="Марс", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id

    login(client)
    client.post(f"/favorite/{cat_id}")
    with app.app_context():
        assert FavoriteCat.query.filter_by(user_id=user_id, cat_id=cat_id).one()

    client.post(f"/favorite/{cat_id}")
    with app.app_context():
        assert (
            FavoriteCat.query.filter_by(user_id=user_id, cat_id=cat_id).first() is None
        )


def test_adoption_request_lifecycle(client, app):
    user_id = create_user(app)
    with app.app_context():
        cat = Cat(name="Луна", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id

    login(client)
    response = client.post(
        f"/cat/{cat_id}/adopt",
        data={
            "adopter_name": "Алина",
            "age": "24",
            "phone": "+79990001122",
            "email": "user@example.com",
            "occupation": "Студентка",
            "housing": "Своя квартира",
            "experience": "Раньше уже ухаживала за кошкой.",
            "reason": "Хочу дать Луне спокойный и безопасный дом.",
        },
    )
    assert response.status_code == 302

    with app.app_context():
        adoption = AdoptionRequest.query.filter_by(user_id=user_id, cat_id=cat_id).one()
        request_id = adoption.id
        assert adoption.status == "Новая"

    client.post(f"/cancel_my_request/{request_id}")
    with app.app_context():
        assert db.session.get(AdoptionRequest, request_id).status == "Отменена"


def test_comment_mutation_routes_are_not_exposed(client, app):
    create_user(app)
    login(client)

    assert client.post("/cat/1/comment", data={"comment": "test"}).status_code == 404
    assert client.post("/comment/1/delete").status_code == 404


def test_user_facing_sources_do_not_contain_long_dashes():
    root = Path(__file__).resolve().parents[1]
    files = [root / "app.py", root / "forms.py"]
    files.extend((root / "templates").glob("*.html"))

    for path in files:
        text = path.read_text(encoding="utf-8")
        assert "\u2014" not in text, path
        assert "\u2013" not in text, path
