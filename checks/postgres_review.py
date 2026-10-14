"""Exercise migrations only in random schemas in a local *_review database.

Requires REVIEW_POSTGRES_URL. Never reads .env or DATABASE_URL, and never drops
an existing schema or database. The application pytest suite stays SQLite-only.
"""

import importlib.util
import os
from pathlib import Path
import re
import uuid

from alembic.migration import MigrationContext
from alembic.operations import Operations
import sqlalchemy as sa
from sqlalchemy.engine import make_url


def validate_url(value):
    url = make_url(value)
    if (
        url.get_backend_name() != "postgresql"
        or url.host not in {"localhost", "127.0.0.1", "::1"}
        or not (url.database or "").endswith("_review")
        or url.query
    ):
        raise ValueError(
            "Use only a local PostgreSQL *_review database without URL query options"
        )
    return url


def migration_modules():
    directory = Path(__file__).resolve().parents[1] / "migrations/versions"
    for name in [
        "713e4cad75bd_baseline_schema.py",
        "b78b1f412a0c_roles_and_temporary_passwords.py",
        "c12ea302f004_adoption_integrity.py",
        "d02f042bae17_username_uniqueness.py",
    ]:
        spec = importlib.util.spec_from_file_location(name[:-3], directory / name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module


def run(value):
    engine = sa.create_engine(validate_url(value), connect_args={"connect_timeout": 5})
    baseline, passwords, integrity, usernames = list(migration_modules())
    try:
        for existing in (False, True):
            schema = "kotopolis_review_" + uuid.uuid4().hex
            assert re.fullmatch(r"kotopolis_review_[a-f0-9]{32}", schema)
            with engine.begin() as connection:
                connection.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
            try:
                with engine.begin() as connection:
                    connection.exec_driver_sql(f'SET LOCAL search_path TO "{schema}"')
                    with Operations.context(MigrationContext.configure(connection)):
                        baseline.upgrade()
                        connection.execute(
                            sa.text(
                                "INSERT INTO users (id, username, email, password, role, email_code_attempts) VALUES (1, 'synthetic', 'synthetic@example.com', 'unused-hash', 'user', 0)"
                            )
                        )
                        if existing:
                            connection.exec_driver_sql(
                                "ALTER TABLE users ADD COLUMN must_change_password BOOLEAN"
                            )
                            connection.exec_driver_sql(
                                "UPDATE users SET must_change_password = TRUE"
                            )
                        passwords.upgrade()
                        integrity.upgrade()
                        usernames.upgrade()
                    assert (
                        connection.execute(
                            sa.text("SELECT must_change_password FROM users WHERE id=1")
                        ).scalar_one()
                        is existing
                    )
                    indexes = {
                        item["name"]
                        for item in sa.inspect(connection).get_indexes(
                            "adoption_requests"
                        )
                    }
                    assert {
                        "uq_active_adoption_user_cat",
                        "uq_approved_adoption_cat",
                    } <= indexes
                print(
                    f"PostgreSQL migrations: existing password column={existing}: passed"
                )
            finally:
                with engine.begin() as connection:
                    connection.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')
    finally:
        engine.dispose()


if __name__ == "__main__":
    value = os.environ.get("REVIEW_POSTGRES_URL")
    if not value:
        raise SystemExit(
            "Set REVIEW_POSTGRES_URL to an isolated local *_review database"
        )
    run(value)
