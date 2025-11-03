"""Add user plan fields and purchases table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_user_plan"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("plan", sa.String(length=50), nullable=False, server_default="free"))
    op.add_column("users", sa.Column("plan_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("status", sa.String(length=32), nullable=False, server_default="active"))
    op.add_column("users", sa.Column("trial_used", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("kirvano_customer_id", sa.String(length=128), nullable=True))
    op.add_column("users", sa.Column("kirvano_last_sale_id", sa.String(length=128), nullable=True))
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sale_id", sa.String(length=128), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("plan", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("payment_method", sa.String(length=64), nullable=True),
        sa.Column("raw_payload", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Remove server defaults (leave them only during migration)
    op.alter_column("users", "plan", server_default=None)
    op.alter_column("users", "status", server_default=None)
    op.alter_column("users", "trial_used", server_default=None)


def downgrade() -> None:
    op.drop_table("purchases")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "kirvano_last_sale_id")
    op.drop_column("users", "kirvano_customer_id")
    op.drop_column("users", "trial_used")
    op.drop_column("users", "status")
    op.drop_column("users", "plan_expires_at")
    op.drop_column("users", "plan")
    op.drop_column("users", "email")
