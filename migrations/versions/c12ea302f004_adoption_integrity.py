"""Prevent duplicate active and approved adoption requests without deleting history."""

from alembic import op
import sqlalchemy as sa

revision = "c12ea302f004"
down_revision = "b78b1f412a0c"
branch_labels = None
depends_on = None

ACTIVE = "user_id IS NOT NULL AND status IN ('Новая', 'На рассмотрении', 'Одобрена')"
APPROVED = "status = 'Одобрена'"


def upgrade():
    connection = op.get_bind()
    for query in (
        f"SELECT user_id, cat_id FROM adoption_requests WHERE {ACTIVE} GROUP BY user_id, cat_id HAVING COUNT(*) > 1",
        f"SELECT cat_id FROM adoption_requests WHERE {APPROVED} GROUP BY cat_id HAVING COUNT(*) > 1",
    ):
        if connection.execute(sa.text(query)).first():
            raise RuntimeError(
                "Conflicting historical adoption requests exist. Review their statuses before migrating; no records have been deleted."
            )
    op.create_index(
        "uq_active_adoption_user_cat",
        "adoption_requests",
        ["user_id", "cat_id"],
        unique=True,
        postgresql_where=sa.text(ACTIVE),
        sqlite_where=sa.text(ACTIVE),
    )
    op.create_index(
        "uq_approved_adoption_cat",
        "adoption_requests",
        ["cat_id"],
        unique=True,
        postgresql_where=sa.text(APPROVED),
        sqlite_where=sa.text(APPROVED),
    )


def downgrade():
    op.drop_index("uq_approved_adoption_cat", table_name="adoption_requests")
    op.drop_index("uq_active_adoption_user_cat", table_name="adoption_requests")
