"""Add channel configuration and delivery tracking tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0003_channel_config"
down_revision = "0002_user_plan"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_channel_configs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("channel_name", sa.String(length=150), nullable=True),
        sa.Column("channel_slug", sa.String(length=150), nullable=True, unique=True),
        sa.Column("monitor_mode", sa.String(length=32), nullable=False, server_default=sa.text("'AUTOMATICO'")),
        sa.Column("partner_mode", sa.String(length=32), nullable=False, server_default=sa.text("'somente_bot'")),
        sa.Column("clipador_chefe_username", sa.String(length=80), nullable=True),
        sa.Column("manual_min_clips", sa.Integer(), nullable=True),
        sa.Column("manual_interval_seconds", sa.Integer(), nullable=True),
        sa.Column("manual_min_clips_vod", sa.Integer(), nullable=True),
        sa.Column("slots_configured", sa.Integer(), nullable=True),
        sa.Column("last_streamers_update", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notify_online", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("twitch_client_id", sa.String(length=120), nullable=True),
        sa.Column("twitch_client_secret", sa.String(length=160), nullable=True),
        sa.Column("public_share_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("public_description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "user_streamers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("streamer_id", sa.Integer(), sa.ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "streamer_id", name="uq_user_streamer"),
    )

    op.create_table(
        "clip_deliveries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("streamer_id", sa.Integer(), sa.ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("burst_id", sa.Integer(), sa.ForeignKey("bursts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("clip_id", sa.Integer(), sa.ForeignKey("clips.id", ondelete="SET NULL"), nullable=True),
        sa.Column("clip_external_id", sa.String(length=120), nullable=True),
        sa.Column("burst_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("burst_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("delivery_channel", sa.String(length=32), nullable=False, server_default=sa.text("'web'")),
        sa.Column("extra_payload", sa.Text(), nullable=True),
        sa.UniqueConstraint(
            "user_id",
            "streamer_id",
            "burst_start",
            "burst_end",
            "clip_external_id",
            name="uq_clip_delivery_window",
        ),
    )

    op.create_table(
        "streamer_status",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("streamer_id", sa.Integer(), sa.ForeignKey("streamers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default=sa.text("'offline'")),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_notified", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "streamer_id", name="uq_streamer_status_user"),
    )


def downgrade() -> None:
    op.drop_table("streamer_status")
    op.drop_table("clip_deliveries")
    op.drop_table("user_streamers")
    op.drop_table("user_channel_configs")
