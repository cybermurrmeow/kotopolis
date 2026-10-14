"""Limit roles and add temporary-password state.

Revision ID: b78b1f412a0c
Revises: 713e4cad75bd
"""

from alembic import op
import sqlalchemy as sa


revision = "b78b1f412a0c"
down_revision = "713e4cad75bd"
branch_labels = None
depends_on = None


def upgrade():
    columns = {
        column["name"]: column
        for column in sa.inspect(op.get_bind()).get_columns("users")
    }
    existing = columns.get("must_change_password")
    if existing is not None and not isinstance(existing["type"], sa.Boolean):
        raise RuntimeError(
            "Existing must_change_password must be BOOLEAN; inspect the schema before upgrading"
        )
    if existing is None:
        with op.batch_alter_table("users") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "must_change_password",
                    sa.Boolean(),
                    nullable=False,
                    server_default=sa.false(),
                )
            )
    else:
        op.execute(
            sa.text(
                "UPDATE users SET must_change_password = FALSE WHERE must_change_password IS NULL"
            )
        )
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column(
                "must_change_password",
                existing_type=sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )

    op.execute(
        sa.text("UPDATE users SET role = 'user' WHERE role NOT IN ('user', 'admin')")
    )


def downgrade():
    raise RuntimeError(
        "This migration adopts an existing column and changes roles irreversibly. Restore a verified backup instead of deleting password state."
    )
