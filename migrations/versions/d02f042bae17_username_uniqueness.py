"""Enforce the same case-insensitive username check at the database boundary."""

from alembic import op
import sqlalchemy as sa

revision = "d02f042bae17"
down_revision = "c12ea302f004"
branch_labels = None
depends_on = None


def upgrade():
    duplicate = (
        op.get_bind()
        .execute(
            sa.text(
                "SELECT lower(username) FROM users GROUP BY lower(username) HAVING COUNT(*) > 1"
            )
        )
        .first()
    )
    if duplicate:
        raise RuntimeError(
            "Case-insensitive username collisions exist. Resolve them explicitly before migrating; no users were removed."
        )
    op.create_index(
        "uq_users_username_lower", "users", [sa.text("lower(username)")], unique=True
    )


def downgrade():
    op.drop_index("uq_users_username_lower", table_name="users")
