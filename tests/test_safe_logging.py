import logging
from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from app import load_user
from models import Cat, User, db
from test_app import create_user, login


def database_error():
    return OperationalError(
        "UPDATE private_query_marker SET email = :email",
        {"email": "private_parameter_marker@example.com"},
        Exception("private_driver_marker: sensitive database detail"),
    )


def assert_safe_log(caplog, error_type):
    assert error_type in caplog.text
    for marker in (
        "private_query_marker",
        "private_parameter_marker",
        "private_driver_marker",
    ):
        assert marker not in caplog.text
    assert caplog.records
    assert all(record.exc_info is None for record in caplog.records)


def test_engine_hides_database_parameters(app):
    with app.app_context():
        assert db.engine.hide_parameters is True


def test_real_integrity_error_hides_bound_values(app):
    with app.app_context():
        db.session.add(
            User(username="duplicate", email="first@example.com", password="unused")
        )
        db.session.commit()
        db.session.add(
            User(
                username="duplicate",
                email="private_parameter_marker@example.com",
                password="unused",
            )
        )
        try:
            with pytest.raises(IntegrityError) as caught:
                db.session.commit()
            assert "private_parameter_marker" not in str(caught.value)
            assert "parameters hidden" in str(caught.value)
        finally:
            db.session.rollback()


@pytest.mark.parametrize(
    "error", [database_error(), ValueError("private_driver_marker")]
)
def test_user_loader_does_not_log_exception_details(app, caplog, error):
    with (
        app.test_request_context(),
        caplog.at_level(logging.ERROR, logger=app.logger.name),
        patch.object(db.session, "get", side_effect=error),
    ):
        assert load_user("1") is None
    assert_safe_log(caplog, type(error).__name__)


def test_database_error_handler_logs_safely_and_rolls_back(client, app, caplog):
    create_user(app)
    with app.app_context():
        cat = Cat(name="Test", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id
    login(client)
    caplog.clear()
    with (
        caplog.at_level(logging.ERROR, logger=app.logger.name),
        patch.object(db.session, "commit", side_effect=database_error()),
        patch.object(db.session, "rollback", wraps=db.session.rollback) as rollback,
    ):
        response = client.post(f"/favorite/{cat_id}")
        rollback.assert_called_once()
    assert response.status_code == 503
    assert "private_" not in response.get_data(as_text=True)
    assert_safe_log(caplog, "OperationalError")
    with app.app_context():
        assert db.session.execute(db.select(User)).scalars().all()


@pytest.mark.parametrize("operation", ["add_cat", "edit_cat", "edit_profile"])
def test_locally_handled_database_errors_do_not_log_details(
    client, app, caplog, operation
):
    user_id = create_user(app, "admin", "admin")
    with app.app_context():
        cat = Cat(name="Original", status="В приюте")
        db.session.add(cat)
        db.session.commit()
        cat_id = cat.id
    login(client, "admin")
    if operation == "edit_profile":
        path = "/edit_profile"
        data = {"username": "changed", "email": "admin@example.com"}
    else:
        path = "/add_cat" if operation == "add_cat" else f"/edit_cat/{cat_id}"
        data = {"name": "Changed", "status": "В приюте", "gender": "", "mood": ""}
    caplog.clear()
    with (
        caplog.at_level(logging.ERROR, logger=app.logger.name),
        patch.object(db.session, "commit", side_effect=database_error()),
        patch.object(db.session, "rollback", wraps=db.session.rollback) as rollback,
    ):
        response = client.post(path, data=data)
        rollback.assert_called_once()
    assert response.status_code == 200
    assert "private_" not in response.get_data(as_text=True)
    assert_safe_log(caplog, "OperationalError")
    with app.app_context():
        assert Cat.query.count() == 1
        assert db.session.get(Cat, cat_id).name == "Original"
        assert db.session.get(User, user_id).username == "admin"
