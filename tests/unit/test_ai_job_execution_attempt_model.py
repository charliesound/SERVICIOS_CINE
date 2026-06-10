from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test_user@localhost:5432/cid_test",
)

from models.ai_job_execution_attempt import (
    AIJobExecutionAttempt,
    AI_JOB_EXECUTION_ATTEMPT_MODES,
    AI_JOB_EXECUTION_ATTEMPT_STATUSES,
    ATTEMPT_MODE_CANCEL,
    ATTEMPT_MODE_FAILURE,
    ATTEMPT_MODE_SUCCESS,
    ATTEMPT_STATUS_CANCELLED,
    ATTEMPT_STATUS_CONFLICTED,
    ATTEMPT_STATUS_FAILED,
    ATTEMPT_STATUS_IN_PROGRESS,
    ATTEMPT_STATUS_SUCCEEDED,
)


def test_table_name() -> None:
    assert AIJobExecutionAttempt.__tablename__ == "ai_job_execution_attempts"


def test_required_columns_exist() -> None:
    columns = AIJobExecutionAttempt.__table__.columns
    for column_name in {
        "id",
        "organization_id",
        "job_id",
        "execution_attempt_id",
        "mode",
        "status",
        "fingerprint",
        "fingerprint_version",
        "created_at",
        "updated_at",
    }:
        assert column_name in columns
        assert columns[column_name].nullable is False


def test_optional_columns_exist() -> None:
    columns = AIJobExecutionAttempt.__table__.columns
    for column_name in {
        "requested_by",
        "result_status",
        "consume_entry_id",
        "release_entry_id",
        "consumed_credits",
        "released_credits",
        "error_code",
        "error_message_safe",
        "started_at",
        "finished_at",
        "metadata_json",
    }:
        assert column_name in columns
        assert columns[column_name].nullable is True


def test_payload_digest_is_not_a_column() -> None:
    assert "payload_digest" not in AIJobExecutionAttempt.__table__.columns


def test_unique_constraint_exists() -> None:
    constraints = AIJobExecutionAttempt.__table__.constraints
    assert any(
        constraint.name == "uq_ai_job_execution_attempts_org_job_attempt"
        and {column.name for column in constraint.columns}
        == {"organization_id", "job_id", "execution_attempt_id"}
        for constraint in constraints
    )


def test_check_constraints_exist() -> None:
    constraint_names = {constraint.name for constraint in AIJobExecutionAttempt.__table__.constraints}
    assert "ck_ai_job_execution_attempts_mode" in constraint_names
    assert "ck_ai_job_execution_attempts_status" in constraint_names
    assert "ck_ai_job_execution_attempts_consumed_credits_positive" in constraint_names
    assert "ck_ai_job_execution_attempts_released_credits_positive" in constraint_names
    assert "ck_ai_job_execution_attempts_finished_after_started" in constraint_names


def test_indexes_exist() -> None:
    index_names = {index.name for index in AIJobExecutionAttempt.__table__.indexes}
    assert "ix_ai_job_execution_attempts_org_job" in index_names
    assert "ix_ai_job_execution_attempts_org_job_created_at" in index_names
    assert "ix_ai_job_execution_attempts_org_status_created_at" in index_names
    assert "ix_ai_job_execution_attempts_org_attempt" in index_names


def test_foreign_key_to_ai_jobs_exists() -> None:
    foreign_keys = list(AIJobExecutionAttempt.__table__.c.job_id.foreign_keys)
    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "ai_jobs.id"


def test_constants_match_allowed_modes_and_statuses() -> None:
    assert AI_JOB_EXECUTION_ATTEMPT_MODES == (
        ATTEMPT_MODE_SUCCESS,
        ATTEMPT_MODE_FAILURE,
        ATTEMPT_MODE_CANCEL,
    )
    assert AI_JOB_EXECUTION_ATTEMPT_STATUSES == (
        ATTEMPT_STATUS_IN_PROGRESS,
        ATTEMPT_STATUS_SUCCEEDED,
        ATTEMPT_STATUS_FAILED,
        ATTEMPT_STATUS_CANCELLED,
        ATTEMPT_STATUS_CONFLICTED,
    )
