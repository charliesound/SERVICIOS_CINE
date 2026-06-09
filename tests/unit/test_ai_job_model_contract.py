from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from database import Base

import models
from models.ai_job import AIJob
import schemas.ai_job_schema as ai_job_schema
from schemas.ai_job_schema import AIJobCreate, AIJobResponse


EXPECTED_AI_JOB_COLUMNS = {
    "id",
    "organization_id",
    "project_id",
    "user_id",
    "operation_type",
    "status",
    "estimated_credits",
    "reserved_credits",
    "consumed_credits",
    "released_credits",
    "reservation_entry_id",
    "consume_entry_id",
    "release_entry_id",
    "idempotency_key",
    "provider_type",
    "provider_name",
    "provider_job_id",
    "workflow_id",
    "workflow_version",
    "workflow_hash",
    "model_name",
    "input_asset_ids",
    "output_asset_ids",
    "error_code",
    "failure_reason",
    "attempt_number",
    "parent_job_id",
    "created_at",
    "estimated_at",
    "credit_checked_at",
    "reserved_at",
    "queued_at",
    "started_at",
    "finished_at",
    "cancel_requested_at",
    "cancelled_at",
    "consume_pending_at",
    "consumed_at",
    "release_pending_at",
    "released_at",
    "expires_at",
    "metadata",
}

EXPECTED_INDEX_NAMES = {
    "ix_ai_jobs_organization_id_created_at",
    "ix_ai_jobs_organization_id_status",
    "ix_ai_jobs_organization_id_project_id_created_at",
    "ix_ai_jobs_organization_id_operation_type_created_at",
    "ix_ai_jobs_parent_job_id",
    "ix_ai_jobs_reservation_entry_id",
    "ix_ai_jobs_consume_entry_id",
    "ix_ai_jobs_release_entry_id",
    "ix_ai_jobs_provider_job_id",
}


class TestAIJobImports:
    def test_model_imports(self) -> None:
        assert AIJob is not None
        assert models is not None
        assert hasattr(models, "AIJob")
        assert "AIJob" in models.__all__

    def test_schema_module_imports(self) -> None:
        assert ai_job_schema is not None
        assert hasattr(ai_job_schema, "AIJobCreate")
        assert hasattr(ai_job_schema, "AIJobResponse")

    def test_module_does_not_import_workers_or_endpoints(self) -> None:
        model_source = (ROOT / "src" / "models" / "ai_job.py").read_text(encoding="utf-8")
        schema_source = (ROOT / "src" / "schemas" / "ai_job_schema.py").read_text(
            encoding="utf-8"
        )

        forbidden_markers = (
            "job_router",
            "job_scheduler",
            "worker",
            "comfyui",
            "endpoint",
            "FastAPI",
        )
        for marker in forbidden_markers:
            assert marker not in model_source
            assert marker not in schema_source


class TestAIJobMetadataRegistration:
    def test_ai_jobs_present_in_base_metadata(self) -> None:
        assert "ai_jobs" in Base.metadata.tables
        assert Base.metadata.tables["ai_jobs"] is AIJob.__table__


class TestAIJobTableContract:
    def test_ai_jobs_table_has_expected_columns(self) -> None:
        cols = AIJob.__table__.c
        missing = EXPECTED_AI_JOB_COLUMNS - set(cols.keys())
        assert not missing, f"Missing ai_jobs columns: {missing}"

    def test_metadata_exists_as_real_column_with_safe_python_alias(self) -> None:
        cols = AIJob.__table__.c
        assert "metadata" in cols
        assert "job_metadata" not in cols
        assert hasattr(AIJob, "job_metadata")

    def test_required_contract_columns_are_non_nullable(self) -> None:
        cols = AIJob.__table__.c
        assert cols["organization_id"].nullable is False
        assert cols["operation_type"].nullable is False
        assert cols["status"].nullable is False

    def test_credit_fields_exist_and_are_integers(self) -> None:
        cols = AIJob.__table__.c
        for name in (
            "estimated_credits",
            "reserved_credits",
            "consumed_credits",
            "released_credits",
        ):
            assert cols[name].type.python_type is int

    def test_ledger_reference_fields_exist(self) -> None:
        cols = AIJob.__table__.c
        for name in ("reservation_entry_id", "consume_entry_id", "release_entry_id"):
            assert name in cols

    def test_provider_and_workflow_fields_exist(self) -> None:
        cols = AIJob.__table__.c
        for name in (
            "provider_type",
            "provider_name",
            "provider_job_id",
            "workflow_id",
            "workflow_version",
            "workflow_hash",
            "model_name",
        ):
            assert name in cols

    def test_asset_fields_exist(self) -> None:
        cols = AIJob.__table__.c
        assert "input_asset_ids" in cols
        assert "output_asset_ids" in cols

    def test_lifecycle_timestamp_fields_exist(self) -> None:
        cols = AIJob.__table__.c
        for name in (
            "created_at",
            "estimated_at",
            "credit_checked_at",
            "reserved_at",
            "queued_at",
            "started_at",
            "finished_at",
            "cancel_requested_at",
            "cancelled_at",
            "consume_pending_at",
            "consumed_at",
            "release_pending_at",
            "released_at",
            "expires_at",
        ):
            assert name in cols

    def test_attempt_number_and_parent_job_id_exist(self) -> None:
        cols = AIJob.__table__.c
        assert "attempt_number" in cols
        assert "parent_job_id" in cols

    def test_expected_indexes_exist(self) -> None:
        index_names = {index.name for index in AIJob.__table__.indexes}
        missing = EXPECTED_INDEX_NAMES - index_names
        assert not missing, f"Missing ai_jobs indexes: {missing}"

    def test_contract_defaults_are_present(self) -> None:
        cols = AIJob.__table__.c
        assert cols["status"].default.arg == "created"
        assert cols["estimated_credits"].default.arg == 0
        assert cols["reserved_credits"].default.arg == 0
        assert cols["consumed_credits"].default.arg == 0
        assert cols["released_credits"].default.arg == 0
        assert cols["attempt_number"].default.arg == 1


class TestAIJobSchemas:
    def test_ai_job_create_accepts_minimal_payload(self) -> None:
        payload = AIJobCreate(
            organization_id="org-1",
            operation_type="image_generation",
        )

        assert payload.organization_id == "org-1"
        assert payload.operation_type == "image_generation"
        assert payload.status == "created"
        assert payload.attempt_number == 1

    def test_ai_job_response_represents_metadata_and_asset_lists(self) -> None:
        response = AIJobResponse(
            id="job-1",
            organization_id="org-1",
            operation_type="image_generation",
            created_at="2026-06-09T12:00:00Z",
            metadata={"provider_name": "internal"},
            input_asset_ids=["asset-in-1"],
            output_asset_ids=["asset-out-1"],
        )

        dumped = response.model_dump()

        assert dumped["metadata"] == {"provider_name": "internal"}
        assert dumped["input_asset_ids"] == ["asset-in-1"]
        assert dumped["output_asset_ids"] == ["asset-out-1"]

    def test_ai_job_response_reads_metadata_from_job_metadata_alias(self) -> None:
        response = AIJobResponse(
            id="job-2",
            organization_id="org-2",
            operation_type="script_analysis",
            created_at="2026-06-09T12:30:00Z",
            job_metadata={"workflow_id": "wf-1"},
        )

        assert response.metadata == {"workflow_id": "wf-1"}

    def test_contract_tests_do_not_require_real_db(self) -> None:
        assert "ai_jobs" in Base.metadata.tables
