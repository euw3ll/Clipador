"""Initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=100), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "streamers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("twitch_user_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("monitor_interval_seconds", sa.Integer(), nullable=False, server_default="180"),
        sa.Column("monitor_min_clips", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("last_clip_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "clips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("clip_id", sa.String(length=64), nullable=False),
        sa.Column("streamer_id", sa.Integer(), sa.ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("streamer_name", sa.String(length=256), nullable=False),
        sa.Column("streamer_external_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("viewer_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("video_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("broadcaster_level", sa.Integer(), nullable=True),
        sa.UniqueConstraint("clip_id"),
    )

    op.create_table(
        "bursts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("streamer_id", sa.Integer(), sa.ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("clip_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "burst_clips",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("burst_id", sa.Integer(), sa.ForeignKey("bursts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clip_id", sa.Integer(), sa.ForeignKey("clips.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clip_external_id", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("burst_id", "clip_external_id", name="uq_burst_clip"),
    )


def downgrade() -> None:
    op.drop_table("burst_clips")
    op.drop_table("bursts")
    op.drop_table("clips")
    op.drop_table("streamers")
    op.drop_table("users")
