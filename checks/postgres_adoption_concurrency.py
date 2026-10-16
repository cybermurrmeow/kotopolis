"""Check concurrent requests in a disposable local PostgreSQL *_review database.

Run: python checks/postgres_adoption_concurrency.py
Set REVIEW_POSTGRES_URL with an explicit port other than 5432. Uses synthetic
accounts and its own random schema, which is removed afterwards. Never reads .env.
This checks transactions through Flask test clients, not a browser or HTTP server.
Sessions are synthetic and CSRF is disabled; this is not an authentication test.
"""

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa

from postgres_review import migration_modules, validate_url


def concurrent_posts(engine, clients, posts, cat_id, application_name):
    # Hold the row until both request connections are waiting for it.
    with engine.connect() as blocker:
        blocker.execute(
            sa.text("SELECT id FROM cats WHERE id = :id FOR UPDATE"), {"id": cat_id}
        ).scalar_one()
        pid = blocker.execute(sa.text("SELECT pg_backend_pid()")).scalar_one()
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(client.post, path, data=data)
                for client, (path, data) in zip(clients, posts, strict=True)
            ]
            try:
                deadline = time.monotonic() + 8
                while time.monotonic() < deadline:
                    with engine.connect() as observer:
                        waiting = observer.execute(
                            sa.text(
                                # A queued request can wait on another waiter.
                                "WITH RECURSIVE blocked(pid) AS ("
                                "SELECT pid FROM pg_stat_activity "
                                "WHERE :blocker = ANY(pg_blocking_pids(pid)) "
                                "UNION "
                                "SELECT activity.pid FROM pg_stat_activity activity "
                                "JOIN blocked ON blocked.pid = ANY(pg_blocking_pids(activity.pid))"
                                ") SELECT count(*) FROM pg_stat_activity "
                                "JOIN blocked USING (pid) "
                                "WHERE datname = current_database() "
                                "AND application_name = :name "
                                "AND wait_event_type = 'Lock'"
                            ),
                            {"name": application_name, "blocker": pid},
                        ).scalar_one()
                    if waiting == 2:
                        break
                    if any(future.done() for future in futures):
                        raise AssertionError(
                            "A request finished before both acquired contention"
                        )
                    time.sleep(0.02)
                else:
                    raise AssertionError(
                        "Two concurrent PostgreSQL lock waits not observed"
                    )
            finally:
                blocker.rollback()
            responses = [future.result(timeout=20) for future in futures]
    assert all(response.status_code == 302 for response in responses)
    return responses


def check_routes(app, engine, application_name):
    from models import AdoptionRequest, Cat, User, db

    with app.app_context():
        people = []
        for name, role in (
            ("review_owner", "user"),
            ("review_other", "user"),
            ("review_admin", "admin"),
        ):
            person = User(
                username=name,
                email=name + "@example.com",
                role=role,
                email_confirmed=True,
                must_change_password=False,
            )
            person.set_password(uuid.uuid4().hex)
            db.session.add(person)
            people.append(person)
        cats = [
            Cat(name=name, status="В приюте") for name in ("Submission", "Approval")
        ]
        db.session.add_all(cats)
        db.session.flush()
        owner, other, admin = people
        records = [
            AdoptionRequest(
                user_id=person.id,
                cat_id=cats[1].id,
                adopter_name="Review",
                email=person.email,
                status="Новая",
            )
            for person in (owner, other)
        ]
        db.session.add_all(records)
        db.session.commit()
        submission_cat, approval_cat = [cat.id for cat in cats]
        record_ids = [record.id for record in records]
        identities = {
            person.role: (person.id, sha256(person.password.encode()).hexdigest())
            for person in (owner, admin)
        }

    def clients_for(role):
        clients = [app.test_client(), app.test_client()]
        user_id, password_version = identities[role]
        for client in clients:
            with client.session_transaction() as session:
                session["_user_id"] = str(user_id)
                session["_fresh"] = True
                session["password_version"] = password_version
        return clients

    data = {
        "adopter_name": "Review User",
        "age": "24",
        "phone": "+79990001122",
        "email": "review_owner@example.com",
        "occupation": "Студент",
        "housing": "Своя квартира",
        "experience": "Раньше ухаживал за кошкой.",
        "reason": "Хочу дать котику спокойный и безопасный дом.",
    }
    responses = concurrent_posts(
        engine,
        clients_for("user"),
        [(f"/cat/{submission_cat}/adopt", data)] * 2,
        submission_cat,
        application_name,
    )
    assert all(
        response.headers["Location"].endswith("/profile") for response in responses
    )
    with app.app_context():
        records = AdoptionRequest.query.filter_by(cat_id=submission_cat).all()
        assert len(records) == 1 and records[0].status == "Новая"
        assert records[0].user_id == identities["user"][0]
        assert db.session.get(Cat, submission_cat).status == "В приюте"
    print("PASS: concurrent duplicate submissions leave one active request")

    responses = concurrent_posts(
        engine,
        clients_for("admin"),
        [
            (f"/adoption_request/{record_id}/status", {"status": "Одобрена"})
            for record_id in record_ids
        ],
        approval_cat,
        application_name,
    )
    assert all(
        response.headers["Location"].endswith("/adoption_requests")
        for response in responses
    )
    with app.app_context():
        records = AdoptionRequest.query.filter_by(cat_id=approval_cat).all()
        assert {record.id for record in records} == set(record_ids)
        assert sorted(record.status for record in records) == sorted(
            ["Одобрена", "Отклонена"]
        )
        cat = db.session.get(Cat, approval_cat)
        assert cat.status == "Усыновлён" and cat.adoption_date is not None
        assert cat.previous_status == "В приюте"
    print("PASS: concurrent approvals preserve both requests and approve only one")


def run(value):
    url = validate_url(value)
    if not url.port or url.port == 5432 or not url.username:
        raise ValueError("Use an explicit non-default port and a dedicated review role")
    if "app" in sys.modules or "models" in sys.modules:
        raise RuntimeError("Run this check in a separate Python process")
    schema = "kotopolis_review_" + uuid.uuid4().hex
    application_name = "adoption_check_" + uuid.uuid4().hex
    url = url.set(drivername="postgresql+psycopg2")
    engine = sa.create_engine(
        url, hide_parameters=True, connect_args={"connect_timeout": 5}
    )
    created = False
    application = None
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        created = True
        scoped_url = url.update_query_dict(
            {
                "options": f"-csearch_path={schema} -clock_timeout=10000 -cstatement_timeout=15000"
            }
        )
        scoped_engine = sa.create_engine(scoped_url, hide_parameters=True)
        try:
            with scoped_engine.begin() as connection:
                with Operations.context(MigrationContext.configure(connection)):
                    for migration in migration_modules():
                        migration.upgrade()
            with tempfile.TemporaryDirectory(prefix="kotopolis-adoption-") as temporary:
                os.environ.update(
                    PYTHON_DOTENV_DISABLED="1",
                    SECRET_KEY=uuid.uuid4().hex,
                    DATABASE_URL=scoped_url.update_query_dict(
                        {"application_name": application_name}
                    ).render_as_string(hide_password=False),
                    RATELIMIT_ENABLED="false",
                    RATELIMIT_STORAGE_URI="memory://",
                    COOKIE_SECURE="false",
                    PUBLIC_BASE_URL="http://127.0.0.1:5000",
                )
                sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                from app import app
                from models import db

                application = app
                app.config.update(
                    TESTING=True,
                    WTF_CSRF_ENABLED=False,
                    MAIL_SUPPRESS_SEND=True,
                    STORY_STATE_DIR=temporary,
                )
                check_routes(app, scoped_engine, application_name)
        finally:
            if application is not None:
                with application.app_context():
                    db.session.remove()
                    db.engine.dispose()
            scoped_engine.dispose()
    finally:
        try:
            if created:
                with engine.begin() as connection:
                    connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
        finally:
            engine.dispose()


if __name__ == "__main__":
    value = os.environ.get("REVIEW_POSTGRES_URL")
    if not value:
        raise SystemExit(
            "Set REVIEW_POSTGRES_URL to a disposable local *_review database"
        )
    try:
        run(value)
    except Exception as error:
        raise SystemExit(f"FAIL: {type(error).__name__}; check did not pass") from None
