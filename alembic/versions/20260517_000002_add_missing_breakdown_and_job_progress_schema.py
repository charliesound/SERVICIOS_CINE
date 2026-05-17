"""add missing breakdown, budget, document asset and job progress schema

Revision ID: 20260517_000002
Revises: 20260517_000001
Create Date: 2026-05-17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260517_000002"
down_revision: Union[str, None] = "20260517_000001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    if not _table_exists(bind, table_name):
        return False
    inspector = sa.inspect(bind)
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()

    if not _table_exists(bind, "production_breakdowns"):
        op.create_table(
            "production_breakdowns",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("project_id", sa.String(length=64), nullable=False),
            sa.Column("organization_id", sa.String(length=64), nullable=False),
            sa.Column("script_text", sa.Text(), nullable=True),
            sa.Column("breakdown_json", sa.Text(), nullable=True),
            sa.Column("budget_estimate", sa.Float(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="completed"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_production_breakdowns_project_id",
            "production_breakdowns",
            ["project_id"],
            unique=False,
        )
        op.create_index(
            "ix_production_breakdowns_organization_id",
            "production_breakdowns",
            ["organization_id"],
            unique=False,
        )

    if not _table_exists(bind, "project_budgets"):
        op.create_table(
            "project_budgets",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("scenario_type", sa.String(length=20), nullable=False, server_default="standard"),
            sa.Column("grand_total", sa.Float(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_project_budgets_project_id",
            "project_budgets",
            ["project_id"],
            unique=False,
        )
        op.create_index(
            "ix_project_budgets_organization_id",
            "project_budgets",
            ["organization_id"],
            unique=False,
        )
        op.create_index(
            "ix_project_budget_project_id",
            "project_budgets",
            ["project_id"],
            unique=False,
        )

    if not _table_exists(bind, "document_assets"):
        op.create_table(
            "document_assets",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("storage_source_id", sa.String(length=36), nullable=True),
            sa.Column("media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("file_name", sa.String(length=255), nullable=False),
            sa.Column("file_extension", sa.String(length=50), nullable=False),
            sa.Column("mime_type", sa.String(length=255), nullable=True),
            sa.Column("source_kind", sa.String(length=50), nullable=False, server_default="script_text"),
            sa.Column("original_path", sa.Text(), nullable=True),
            sa.Column("uploaded_by", sa.String(length=36), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="registered"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_document_assets_project_id",
            "document_assets",
            ["project_id"],
            unique=False,
        )
        op.create_index(
            "ix_document_assets_organization_id",
            "document_assets",
            ["organization_id"],
            unique=False,
        )
        op.create_index(
            "ix_document_assets_media_asset",
            "document_assets",
            ["media_asset_id"],
            unique=False,
        )
        op.create_index(
            "ix_document_assets_org_project",
            "document_assets",
            ["organization_id", "project_id"],
            unique=False,
        )
        op.create_index(
            "ix_document_assets_status_created_at",
            "document_assets",
            ["status", "created_at"],
            unique=False,
        )

    if not _table_exists(bind, "budget_lines"):
        op.create_table(
            "budget_lines",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("budget_id", sa.String(length=36), nullable=False),
            sa.Column("section", sa.String(length=50), nullable=False),
            sa.Column("category", sa.String(length=100), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=False),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("unit_cost", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_cost", sa.Float(), nullable=False, server_default="0"),
            sa.Column("is_manual_override", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["budget_id"], ["project_budgets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_budget_line_budget_id", "budget_lines", ["budget_id"], unique=False)
        op.create_index("ix_budget_line_section", "budget_lines", ["section"], unique=False)

    if not _table_exists(bind, "project_funding_sources"):
        op.create_table(
            "project_funding_sources",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("source_name", sa.String(length=255), nullable=False),
            sa.Column("source_type", sa.String(length=50), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="projected"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_project_funding_sources_project_id", "project_funding_sources", ["project_id"], unique=False)
        op.create_index("ix_project_funding_sources_organization_id", "project_funding_sources", ["organization_id"], unique=False)
        op.create_index("ix_pfs_project_org", "project_funding_sources", ["project_id", "organization_id"], unique=False)

    if not _table_exists(bind, "budget_estimates"):
        op.create_table(
            "budget_estimates",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("source_script_version_id", sa.String(length=36), nullable=True),
            sa.Column("source_breakdown_id", sa.String(length=36), nullable=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
            sa.Column("budget_level", sa.String(length=20), nullable=False, server_default="medium"),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
            sa.Column("total_min", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_estimated", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_max", sa.Float(), nullable=False, server_default="0"),
            sa.Column("contingency_percent", sa.Float(), nullable=False, server_default="0"),
            sa.Column("assumptions_json", sa.JSON(), nullable=True),
            sa.Column("role_summaries_json", sa.JSON(), nullable=True),
            sa.Column("summary", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_budget_estimate_project_id", "budget_estimates", ["project_id"], unique=False)
        op.create_index("ix_budget_estimate_org_project", "budget_estimates", ["organization_id", "project_id"], unique=False)
        op.create_index("ix_budget_estimate_status", "budget_estimates", ["status"], unique=False)

    if not _table_exists(bind, "budget_line_items"):
        op.create_table(
            "budget_line_items",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("budget_estimate_id", sa.String(length=36), nullable=False),
            sa.Column("category", sa.String(length=50), nullable=False),
            sa.Column("subcategory", sa.String(length=100), nullable=True),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("unit_cost_min", sa.Float(), nullable=False, server_default="0"),
            sa.Column("unit_cost_estimated", sa.Float(), nullable=False, server_default="0"),
            sa.Column("unit_cost_max", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_min", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_estimated", sa.Float(), nullable=False, server_default="0"),
            sa.Column("total_max", sa.Float(), nullable=False, server_default="0"),
            sa.Column("source", sa.String(length=20), nullable=False, server_default="default_rule"),
            sa.Column("confidence", sa.String(length=20), nullable=False, server_default="medium"),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["budget_estimate_id"], ["budget_estimates.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_budget_line_item_estimate_id", "budget_line_items", ["budget_estimate_id"], unique=False)
        op.create_index("ix_budget_line_item_category", "budget_line_items", ["category"], unique=False)

    if not _table_exists(bind, "document_extractions"):
        op.create_table(
            "document_extractions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_asset_id", sa.String(length=36), nullable=False),
            sa.Column("extraction_status", sa.String(length=50), nullable=False, server_default="pending"),
            sa.Column("extraction_engine", sa.String(length=100), nullable=True),
            sa.Column("raw_text", sa.Text(), nullable=True),
            sa.Column("extracted_table_json", sa.Text(), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_asset_id"], ["document_assets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("document_asset_id", name="uq_document_extractions_document_asset_id"),
        )
        op.create_index(
            "ix_document_extractions_document_asset_id",
            "document_extractions",
            ["document_asset_id"],
            unique=False,
        )

    if not _table_exists(bind, "document_classifications"):
        op.create_table(
            "document_classifications",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_asset_id", sa.String(length=36), nullable=False),
            sa.Column("doc_type", sa.String(length=100), nullable=False, server_default="unknown_document"),
            sa.Column("classification_status", sa.String(length=50), nullable=False, server_default="pending"),
            sa.Column("confidence_score", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_asset_id"], ["document_assets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("document_asset_id", name="uq_document_classifications_document_asset_id"),
        )
        op.create_index(
            "ix_document_classifications_document_asset_id",
            "document_classifications",
            ["document_asset_id"],
            unique=False,
        )

    if not _table_exists(bind, "document_structured_data"):
        op.create_table(
            "document_structured_data",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_asset_id", sa.String(length=36), nullable=False),
            sa.Column("schema_type", sa.String(length=100), nullable=False),
            sa.Column("structured_payload_json", sa.Text(), nullable=False),
            sa.Column("review_status", sa.String(length=50), nullable=False, server_default="draft"),
            sa.Column("approved_by", sa.String(length=36), nullable=True),
            sa.Column("approved_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_asset_id"], ["document_assets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("document_asset_id", name="uq_document_structured_data_document_asset_id"),
        )
        op.create_index(
            "ix_document_structured_data_document_asset_id",
            "document_structured_data",
            ["document_asset_id"],
            unique=False,
        )

    if not _table_exists(bind, "document_links"):
        op.create_table(
            "document_links",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("document_asset_id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("shooting_day_id", sa.String(length=36), nullable=True),
            sa.Column("sequence_id", sa.String(length=36), nullable=True),
            sa.Column("scene_id", sa.String(length=36), nullable=True),
            sa.Column("shot_id", sa.String(length=36), nullable=True),
            sa.Column("media_asset_id", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["document_asset_id"], ["document_assets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_document_links_document_asset_id", "document_links", ["document_asset_id"], unique=False)
        op.create_index("ix_document_links_organization_id", "document_links", ["organization_id"], unique=False)
        op.create_index("ix_document_links_project_id", "document_links", ["project_id"], unique=False)
        op.create_index("ix_document_links_media_asset_id", "document_links", ["media_asset_id"], unique=False)
        op.create_index("ix_document_links_org_project", "document_links", ["organization_id", "project_id"], unique=False)
        op.create_index("ix_document_links_media_asset", "document_links", ["media_asset_id"], unique=False)

    if not _table_exists(bind, "ingest_events"):
        op.create_table(
            "ingest_events",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("organization_id", sa.String(length=36), nullable=False),
            sa.Column("project_id", sa.String(length=36), nullable=False),
            sa.Column("storage_source_id", sa.String(length=36), nullable=True),
            sa.Column("document_asset_id", sa.String(length=36), nullable=True),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("event_payload_json", sa.Text(), nullable=True),
            sa.Column("created_by", sa.String(length=36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ingest_events_organization_id", "ingest_events", ["organization_id"], unique=False)
        op.create_index("ix_ingest_events_project_id", "ingest_events", ["project_id"], unique=False)
        op.create_index("ix_ingest_events_storage_source_id", "ingest_events", ["storage_source_id"], unique=False)
        op.create_index("ix_ingest_events_document_asset_id", "ingest_events", ["document_asset_id"], unique=False)
        op.create_index("ix_ingest_events_org_project", "ingest_events", ["organization_id", "project_id"], unique=False)
        op.create_index("ix_ingest_events_source", "ingest_events", ["storage_source_id"], unique=False)
        op.create_index("ix_ingest_events_created_at", "ingest_events", ["created_at"], unique=False)

    if _table_exists(bind, "project_jobs"):
        if not _column_exists(bind, "project_jobs", "progress_percent"):
            op.add_column(
                "project_jobs",
                sa.Column("progress_percent", sa.Integer(), nullable=False, server_default="0"),
            )

        if not _column_exists(bind, "project_jobs", "progress_stage"):
            op.add_column(
                "project_jobs",
                sa.Column("progress_stage", sa.String(length=120), nullable=True),
            )

        if not _column_exists(bind, "project_jobs", "progress_code"):
            op.add_column(
                "project_jobs",
                sa.Column("progress_code", sa.String(length=80), nullable=True),
            )

    if _table_exists(bind, "project_funding_matches"):
        if not _column_exists(bind, "project_funding_matches", "baseline_score"):
            op.add_column("project_funding_matches", sa.Column("baseline_score", sa.Float(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "rag_enriched_score"):
            op.add_column("project_funding_matches", sa.Column("rag_enriched_score", sa.Float(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "fit_level"):
            op.add_column("project_funding_matches", sa.Column("fit_level", sa.String(length=20), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "fit_summary"):
            op.add_column("project_funding_matches", sa.Column("fit_summary", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "blocking_reasons"):
            op.add_column("project_funding_matches", sa.Column("blocking_reasons", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "missing_documents"):
            op.add_column("project_funding_matches", sa.Column("missing_documents", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "recommended_actions"):
            op.add_column("project_funding_matches", sa.Column("recommended_actions", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "evidence_chunks_json"):
            op.add_column("project_funding_matches", sa.Column("evidence_chunks_json", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "rag_rationale"):
            op.add_column("project_funding_matches", sa.Column("rag_rationale", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "rag_missing_requirements"):
            op.add_column("project_funding_matches", sa.Column("rag_missing_requirements", sa.Text(), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "confidence_level"):
            op.add_column("project_funding_matches", sa.Column("confidence_level", sa.String(length=20), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "rag_confidence_level"):
            op.add_column("project_funding_matches", sa.Column("rag_confidence_level", sa.String(length=20), nullable=True))
        if not _column_exists(bind, "project_funding_matches", "matcher_mode"):
            op.add_column("project_funding_matches", sa.Column("matcher_mode", sa.String(length=30), nullable=True, server_default="classic"))
        if not _column_exists(bind, "project_funding_matches", "evaluation_version"):
            op.add_column("project_funding_matches", sa.Column("evaluation_version", sa.String(length=20), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, "project_jobs"):
        if _column_exists(bind, "project_jobs", "progress_code"):
            op.drop_column("project_jobs", "progress_code")
        if _column_exists(bind, "project_jobs", "progress_stage"):
            op.drop_column("project_jobs", "progress_stage")
        if _column_exists(bind, "project_jobs", "progress_percent"):
            op.drop_column("project_jobs", "progress_percent")

    if _table_exists(bind, "project_funding_matches"):
        if _column_exists(bind, "project_funding_matches", "evaluation_version"):
            op.drop_column("project_funding_matches", "evaluation_version")
        if _column_exists(bind, "project_funding_matches", "matcher_mode"):
            op.drop_column("project_funding_matches", "matcher_mode")
        if _column_exists(bind, "project_funding_matches", "rag_confidence_level"):
            op.drop_column("project_funding_matches", "rag_confidence_level")
        if _column_exists(bind, "project_funding_matches", "confidence_level"):
            op.drop_column("project_funding_matches", "confidence_level")
        if _column_exists(bind, "project_funding_matches", "rag_missing_requirements"):
            op.drop_column("project_funding_matches", "rag_missing_requirements")
        if _column_exists(bind, "project_funding_matches", "rag_rationale"):
            op.drop_column("project_funding_matches", "rag_rationale")
        if _column_exists(bind, "project_funding_matches", "evidence_chunks_json"):
            op.drop_column("project_funding_matches", "evidence_chunks_json")
        if _column_exists(bind, "project_funding_matches", "recommended_actions"):
            op.drop_column("project_funding_matches", "recommended_actions")
        if _column_exists(bind, "project_funding_matches", "missing_documents"):
            op.drop_column("project_funding_matches", "missing_documents")
        if _column_exists(bind, "project_funding_matches", "blocking_reasons"):
            op.drop_column("project_funding_matches", "blocking_reasons")
        if _column_exists(bind, "project_funding_matches", "fit_summary"):
            op.drop_column("project_funding_matches", "fit_summary")
        if _column_exists(bind, "project_funding_matches", "fit_level"):
            op.drop_column("project_funding_matches", "fit_level")
        if _column_exists(bind, "project_funding_matches", "rag_enriched_score"):
            op.drop_column("project_funding_matches", "rag_enriched_score")
        if _column_exists(bind, "project_funding_matches", "baseline_score"):
            op.drop_column("project_funding_matches", "baseline_score")

    if _table_exists(bind, "document_extractions"):
        if _index_exists(bind, "document_extractions", "ix_document_extractions_document_asset_id"):
            op.drop_index("ix_document_extractions_document_asset_id", table_name="document_extractions")
        op.drop_table("document_extractions")

    if _table_exists(bind, "document_structured_data"):
        if _index_exists(bind, "document_structured_data", "ix_document_structured_data_document_asset_id"):
            op.drop_index("ix_document_structured_data_document_asset_id", table_name="document_structured_data")
        op.drop_table("document_structured_data")

    if _table_exists(bind, "document_links"):
        if _index_exists(bind, "document_links", "ix_document_links_media_asset"):
            op.drop_index("ix_document_links_media_asset", table_name="document_links")
        if _index_exists(bind, "document_links", "ix_document_links_org_project"):
            op.drop_index("ix_document_links_org_project", table_name="document_links")
        if _index_exists(bind, "document_links", "ix_document_links_media_asset_id"):
            op.drop_index("ix_document_links_media_asset_id", table_name="document_links")
        if _index_exists(bind, "document_links", "ix_document_links_project_id"):
            op.drop_index("ix_document_links_project_id", table_name="document_links")
        if _index_exists(bind, "document_links", "ix_document_links_organization_id"):
            op.drop_index("ix_document_links_organization_id", table_name="document_links")
        if _index_exists(bind, "document_links", "ix_document_links_document_asset_id"):
            op.drop_index("ix_document_links_document_asset_id", table_name="document_links")
        op.drop_table("document_links")

    if _table_exists(bind, "document_classifications"):
        if _index_exists(bind, "document_classifications", "ix_document_classifications_document_asset_id"):
            op.drop_index("ix_document_classifications_document_asset_id", table_name="document_classifications")
        op.drop_table("document_classifications")

    if _table_exists(bind, "ingest_events"):
        if _index_exists(bind, "ingest_events", "ix_ingest_events_created_at"):
            op.drop_index("ix_ingest_events_created_at", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_source"):
            op.drop_index("ix_ingest_events_source", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_org_project"):
            op.drop_index("ix_ingest_events_org_project", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_document_asset_id"):
            op.drop_index("ix_ingest_events_document_asset_id", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_storage_source_id"):
            op.drop_index("ix_ingest_events_storage_source_id", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_project_id"):
            op.drop_index("ix_ingest_events_project_id", table_name="ingest_events")
        if _index_exists(bind, "ingest_events", "ix_ingest_events_organization_id"):
            op.drop_index("ix_ingest_events_organization_id", table_name="ingest_events")
        op.drop_table("ingest_events")

    if _table_exists(bind, "budget_line_items"):
        if _index_exists(bind, "budget_line_items", "ix_budget_line_item_category"):
            op.drop_index("ix_budget_line_item_category", table_name="budget_line_items")
        if _index_exists(bind, "budget_line_items", "ix_budget_line_item_estimate_id"):
            op.drop_index("ix_budget_line_item_estimate_id", table_name="budget_line_items")
        op.drop_table("budget_line_items")

    if _table_exists(bind, "budget_estimates"):
        if _index_exists(bind, "budget_estimates", "ix_budget_estimate_status"):
            op.drop_index("ix_budget_estimate_status", table_name="budget_estimates")
        if _index_exists(bind, "budget_estimates", "ix_budget_estimate_org_project"):
            op.drop_index("ix_budget_estimate_org_project", table_name="budget_estimates")
        if _index_exists(bind, "budget_estimates", "ix_budget_estimate_project_id"):
            op.drop_index("ix_budget_estimate_project_id", table_name="budget_estimates")
        op.drop_table("budget_estimates")

    if _table_exists(bind, "project_funding_sources"):
        if _index_exists(bind, "project_funding_sources", "ix_pfs_project_org"):
            op.drop_index("ix_pfs_project_org", table_name="project_funding_sources")
        if _index_exists(bind, "project_funding_sources", "ix_project_funding_sources_organization_id"):
            op.drop_index("ix_project_funding_sources_organization_id", table_name="project_funding_sources")
        if _index_exists(bind, "project_funding_sources", "ix_project_funding_sources_project_id"):
            op.drop_index("ix_project_funding_sources_project_id", table_name="project_funding_sources")
        op.drop_table("project_funding_sources")

    if _table_exists(bind, "budget_lines"):
        if _index_exists(bind, "budget_lines", "ix_budget_line_section"):
            op.drop_index("ix_budget_line_section", table_name="budget_lines")
        if _index_exists(bind, "budget_lines", "ix_budget_line_budget_id"):
            op.drop_index("ix_budget_line_budget_id", table_name="budget_lines")
        op.drop_table("budget_lines")

    if _table_exists(bind, "document_assets"):
        if _index_exists(bind, "document_assets", "ix_document_assets_status_created_at"):
            op.drop_index("ix_document_assets_status_created_at", table_name="document_assets")
        if _index_exists(bind, "document_assets", "ix_document_assets_org_project"):
            op.drop_index("ix_document_assets_org_project", table_name="document_assets")
        if _index_exists(bind, "document_assets", "ix_document_assets_media_asset"):
            op.drop_index("ix_document_assets_media_asset", table_name="document_assets")
        if _index_exists(bind, "document_assets", "ix_document_assets_organization_id"):
            op.drop_index("ix_document_assets_organization_id", table_name="document_assets")
        if _index_exists(bind, "document_assets", "ix_document_assets_project_id"):
            op.drop_index("ix_document_assets_project_id", table_name="document_assets")
        op.drop_table("document_assets")

    if _table_exists(bind, "project_budgets"):
        if _index_exists(bind, "project_budgets", "ix_project_budget_project_id"):
            op.drop_index("ix_project_budget_project_id", table_name="project_budgets")
        if _index_exists(bind, "project_budgets", "ix_project_budgets_organization_id"):
            op.drop_index("ix_project_budgets_organization_id", table_name="project_budgets")
        if _index_exists(bind, "project_budgets", "ix_project_budgets_project_id"):
            op.drop_index("ix_project_budgets_project_id", table_name="project_budgets")
        op.drop_table("project_budgets")

    if _table_exists(bind, "production_breakdowns"):
        if _index_exists(bind, "production_breakdowns", "ix_production_breakdowns_organization_id"):
            op.drop_index("ix_production_breakdowns_organization_id", table_name="production_breakdowns")
        if _index_exists(bind, "production_breakdowns", "ix_production_breakdowns_project_id"):
            op.drop_index("ix_production_breakdowns_project_id", table_name="production_breakdowns")
        op.drop_table("production_breakdowns")
