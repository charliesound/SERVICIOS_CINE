"""Tests for CreditBalance counter constraints implementation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import CheckConstraint


ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
DOC_PATH = ROOT / "docs" / "architecture" / "cid_credit_balance_constraints_implementation_v1.md"
MIGRATION_PATH = (
    ROOT
    / "alembic"
    / "versions"
    / "20260615_000001_add_credit_balance_counter_constraints.py"
)
HISTORICAL_MIGRATION_PATH = (
    ROOT
    / "alembic"
    / "versions"
    / "20260605_000001_add_cid_billing_models.py"
)

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test:cid_test@localhost:5432/cid_test",
)

from models.billing import CreditBalance  # noqa: E402


CONSTRAINT_NAME = "ck_credit_balances_non_negative_counters"
SUBBALANCE_CONSTRAINT_NAME = "ck_credit_balances_non_negative_subbalances"
EXPECTED_EXPRESSIONS = [
    "consumed_period >= 0",
    "expired_total >= 0",
    "refunded_total >= 0",
    "version >= 1",
]


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _migration_text() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def _counter_constraint() -> CheckConstraint:
    for constraint in CreditBalance.__table__.constraints:
        if isinstance(constraint, CheckConstraint) and constraint.name == CONSTRAINT_NAME:
            return constraint
    raise AssertionError(f"Missing {CONSTRAINT_NAME}")


def _counter_expression() -> str:
    return str(_counter_constraint().sqltext)


def test_implementation_document_exists() -> None:
    assert DOC_PATH.exists()


def test_new_migration_exists() -> None:
    assert MIGRATION_PATH.exists()


def test_model_contains_counter_constraint() -> None:
    assert _counter_constraint().name == CONSTRAINT_NAME


def test_model_counter_constraint_expression() -> None:
    expression = _counter_expression()
    for expected in EXPECTED_EXPRESSIONS:
        assert expected in expression


def test_model_counter_constraint_does_not_include_adjusted_total() -> None:
    assert "adjusted_total" not in _counter_expression()


def test_new_migration_contains_counter_constraint() -> None:
    text = _migration_text()
    assert CONSTRAINT_NAME in text
    for expected in EXPECTED_EXPRESSIONS:
        assert expected in text


def test_new_migration_does_not_touch_subbalances_constraint() -> None:
    assert SUBBALANCE_CONSTRAINT_NAME not in _migration_text()


def test_new_migration_does_not_mention_disallowed_db_backend() -> None:
    disallowed_backend = "sql" + "ite"
    assert disallowed_backend not in _migration_text().lower()


def test_new_migration_down_revision_matches_detected_head() -> None:
    text = _migration_text()
    assert 'down_revision: Union[str, None] = "20260610_000003_ai_job_execution_attempts"' in text


def test_historical_migration_not_modified() -> None:
    status = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--untracked-files=all",
            str(HISTORICAL_MIGRATION_PATH.relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert status == ""


def test_document_says_not_to_edit_historical_migration() -> None:
    text = _doc_text()
    assert "No editar la histórica" in text or "no editar la histórica" in text
    assert "20260605_000001_add_cid_billing_models.py" in text


def test_document_keeps_credit_balance_by_organization_id() -> None:
    text = _doc_text()
    assert "CreditBalance" in text
    assert "organization_id" in text
    assert "sigue siendo por `organization_id`" in text


def test_document_mentions_project_and_film_isolation() -> None:
    text = _doc_text()
    assert "project_id" in text
    assert "film_id" in text
    assert "aislamiento" in text


def test_document_includes_preflight_sql() -> None:
    text = _doc_text()
    assert "SELECT id, organization_id, consumed_period, expired_total, refunded_total, version" in text
    assert "WHERE consumed_period < 0" in text
    assert "OR version < 1" in text
