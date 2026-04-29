"""initial schema: providers, routes, scrape_jobs, scrape_results + seed data

Revision ID: 0001
Revises:
Create Date: 2026-04-30 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- providers ---
    op.create_table(
        "providers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", postgresql.JSONB(), nullable=False),
        sa.Column("base_url", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_providers_code"),
    )

    # --- routes ---
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("origin_id", sa.String(50), nullable=False),
        sa.Column("destination_id", sa.String(50), nullable=False),
        sa.Column("origin_name", postgresql.JSONB(), nullable=False),
        sa.Column("destination_name", postgresql.JSONB(), nullable=False),
        sa.Column("is_popular", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("origin_id", "destination_id", name="uq_routes_origin_destination"),
    )

    # --- scrape_jobs ---
    op.create_table(
        "scrape_jobs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'"), nullable=False),
        sa.Column(
            "triggered_by", sa.String(20), server_default=sa.text("'scheduler'"), nullable=False
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["route_id"], ["routes.id"], name="fk_scrape_jobs_route_id"),
        sa.ForeignKeyConstraint(
            ["provider_id"], ["providers.id"], name="fk_scrape_jobs_provider_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_scrape_jobs_status", "scrape_jobs", ["status"])
    op.create_index("idx_scrape_jobs_route_id", "scrape_jobs", ["route_id"])

    # --- scrape_results ---
    op.create_table(
        "scrape_results",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("route_id", sa.Integer(), nullable=False),
        sa.Column("provider_id", sa.Integer(), nullable=False),
        sa.Column("departure_time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("arrival_time", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("price_jpy", sa.Integer(), nullable=False),
        sa.Column("seat_type", sa.String(100), nullable=True),
        sa.Column("available_seats", sa.Integer(), nullable=True),
        sa.Column("booking_url", sa.Text(), nullable=False),
        sa.Column("pickup_stop", postgresql.JSONB(), nullable=True),
        sa.Column("dropoff_stop", postgresql.JSONB(), nullable=True),
        sa.Column(
            "scraped_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_stale", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["job_id"], ["scrape_jobs.id"], name="fk_scrape_results_job_id"),
        sa.ForeignKeyConstraint(
            ["route_id"], ["routes.id"], name="fk_scrape_results_route_id"
        ),
        sa.ForeignKeyConstraint(
            ["provider_id"], ["providers.id"], name="fk_scrape_results_provider_id"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_scrape_results_route_id", "scrape_results", ["route_id"])
    op.create_index("idx_scrape_results_scraped_at", "scrape_results", ["scraped_at"])
    op.create_index("idx_scrape_results_job_id", "scrape_results", ["job_id"])

    # --- seed: providers ---
    op.execute(
        """
        INSERT INTO providers (code, name, base_url, is_active) VALUES
        (
            'willer',
            '{"vi": "Willer Express", "en": "Willer Express", "ja": "\\u30a6\\u30a3\\u30e9\\u30fc\\u30a8\\u30af\\u30b9\\u30d7\\u30ec\\u30b9"}'::jsonb,
            'https://travel.willer.co.jp',
            true
        ),
        (
            'kosoku',
            '{"vi": "Kosoku Bus", "en": "Kosoku Bus", "ja": "\\u9ad8\\u901f\\u30d0\\u30b9"}'::jsonb,
            'https://www.kosokubus.com',
            true
        )
        """
    )

    # --- seed: popular routes ---
    op.execute(
        """
        INSERT INTO routes (origin_id, destination_id, origin_name, destination_name, is_popular) VALUES
        (
            'tokyo', 'osaka',
            '{"vi": "Tokyo", "en": "Tokyo", "ja": "\\u6771\\u4eac"}'::jsonb,
            '{"vi": "Osaka", "en": "Osaka", "ja": "\\u5927\\u962a"}'::jsonb,
            true
        ),
        (
            'tokyo', 'kyoto',
            '{"vi": "Tokyo", "en": "Tokyo", "ja": "\\u6771\\u4eac"}'::jsonb,
            '{"vi": "Kyoto", "en": "Kyoto", "ja": "\\u4eac\\u90fd"}'::jsonb,
            true
        ),
        (
            'osaka', 'tokyo',
            '{"vi": "Osaka", "en": "Osaka", "ja": "\\u5927\\u962a"}'::jsonb,
            '{"vi": "Tokyo", "en": "Tokyo", "ja": "\\u6771\\u4eac"}'::jsonb,
            true
        ),
        (
            'nagoya', 'tokyo',
            '{"vi": "Nagoya", "en": "Nagoya", "ja": "\\u540d\\u53e4\\u5c4b"}'::jsonb,
            '{"vi": "Tokyo", "en": "Tokyo", "ja": "\\u6771\\u4eac"}'::jsonb,
            true
        ),
        (
            'tokyo', 'nagoya',
            '{"vi": "Tokyo", "en": "Tokyo", "ja": "\\u6771\\u4eac"}'::jsonb,
            '{"vi": "Nagoya", "en": "Nagoya", "ja": "\\u540d\\u53e4\\u5c4b"}'::jsonb,
            true
        ),
        (
            'fukuoka', 'osaka',
            '{"vi": "Fukuoka", "en": "Fukuoka", "ja": "\\u798f\\u5ca1"}'::jsonb,
            '{"vi": "Osaka", "en": "Osaka", "ja": "\\u5927\\u962a"}'::jsonb,
            true
        )
        """
    )


def downgrade() -> None:
    op.drop_table("scrape_results")
    op.drop_table("scrape_jobs")
    op.drop_table("routes")
    op.drop_table("providers")
