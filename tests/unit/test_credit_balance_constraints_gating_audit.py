"""Gating audit for current CreditBalance constraints.

This phase is documentation/test-only. It inspects the current ORM model and
historical Alembic migration without changing runtime, schema, or database.
"""

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path

from sqlalchemy import CheckConstraint, UniqueConstraint


ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / "src"
DOC_PATH = ROOT / "docs" / "architecture" / "cid_credit_balance_constraints_gating_audit_v1.md"
MIGRATION_PATH = ROOT / "alembic" / "versions" / "20260605_000001_add_cid_billing_models.py"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://cid_test:cid_test@localhost:5432/cid_test",
)

from models.billing import CreditBalance  # noqa: E402


REQUIRED_SECTIONS = [
    "## 1. Propósito",
    "## 2. Estado actual de `CreditBalance`",
    "## 3. Constraints actuales protegidas",
    "## 4. Campos no protegidos actualmente por check constraint",
    "## 5. Decisión recomendada",
    "## 6. Aislamiento organización/proyecto",
    "## 7. Riesgos actuales",
    "## 8. Recomendación de implementación futura",
    "## 9. No-goals",
]

REQUIRED_TERMS = [
    "CreditBalance",
    "credit_balances",
    "organization_id",
    "uq_credit_balances_organization_id",
    "ck_credit_balances_non_negative_subbalances",
    "included_monthly_remaining",
    "purchased_balance",
    "promotional_balance",
    "trial_balance",
    "enterprise_balance",
    "reserved_active",
    "consumed_period",
    "expired_total",
    "refunded_total",
    "adjusted_total",
    "version",
    "project_id",
    "film_id",
    "migración histórica",
    "nueva migración",
    "no editar la histórica",
    "test-only",
]

CURRENTLY_PROTECTED_FIELDS = [
    "included_monthly_remaining",
    "purchased_balance",
    "promotional_balance",
    "trial_balance",
    "enterprise_balance",
    "reserved_active",
]

FUTURE_FIELDS_NOT_IN_CURRENT_CHECK = [
    "consumed_period",
    "expired_total",
    "refunded_total",
    "adjusted_total",
    "version",
]


def _doc_text() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _migration_text() -> str:
    return MIGRATION_PATH.read_text(encoding="utf-8")


def _credit_balance_constraints() -> set:
    return set(CreditBalance.__table__.constraints)


def _current_subbalances_check() -> CheckConstraint:
    for constraint in _credit_balance_constraints():
        if (
            isinstance(constraint, CheckConstraint)
            and constraint.name == "ck_credit_balances_non_negative_subbalances"
        ):
            return constraint
    raise AssertionError("Missing ck_credit_balances_non_negative_subbalances")


def _current_subbalances_check_expr() -> str:
    return str(_current_subbalances_check().sqltext)


def test_gating_audit_document_exists() -> None:
    assert DOC_PATH.exists()


def test_gating_audit_document_has_all_sections() -> None:
    text = _doc_text()
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    assert missing == []


def test_gating_audit_document_contains_required_terms() -> None:
    text = _doc_text()
    missing = [term for term in REQUIRED_TERMS if term not in text]
    assert missing == []


def test_credit_balance_has_unique_constraint_by_organization_id() -> None:
    matching = [
        constraint
        for constraint in _credit_balance_constraints()
        if isinstance(constraint, UniqueConstraint)
        and constraint.name == "uq_credit_balances_organization_id"
    ]
    assert len(matching) == 1
    columns = [column.name for column in matching[0].columns]
    assert columns == ["organization_id"]


def test_credit_balance_has_current_non_negative_subbalances_check() -> None:
    constraint = _current_subbalances_check()
    assert constraint.name == "ck_credit_balances_non_negative_subbalances"


def test_current_model_check_includes_six_protected_fields() -> None:
    expression = _current_subbalances_check_expr()
    for field in CURRENTLY_PROTECTED_FIELDS:
        assert field in expression
        assert f"{field} >= 0" in expression


def test_current_model_check_does_not_include_future_fields_yet() -> None:
    expression = _current_subbalances_check_expr()
    for field in FUTURE_FIELDS_NOT_IN_CURRENT_CHECK:
        assert field not in expression


def test_historical_migration_contains_same_constraints() -> None:
    text = _migration_text()
    assert "credit_balances" in text
    assert "uq_credit_balances_organization_id" in text
    assert "ck_credit_balances_non_negative_subbalances" in text
    for field in CURRENTLY_PROTECTED_FIELDS:
        assert field in text
        assert f"{field} >= 0" in text


def test_document_recommends_future_counter_protection() -> None:
    text = _doc_text()
    for recommendation in [
        "consumed_period >= 0",
        "expired_total >= 0",
        "refunded_total >= 0",
        "version >= 1",
    ]:
        assert recommendation in text


def test_document_keeps_adjusted_total_signed() -> None:
    text = _doc_text()
    assert "adjusted_total" in text
    assert "firmado" in text
    assert "negativo o positivo" in text


def test_historical_alembic_migration_not_modified() -> None:
    status = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    historical_changes = [
        line
        for line in status
        if "alembic/versions/20260605_000001_add_cid_billing_models.py" in line
    ]
    assert historical_changes == []


def test_billing_model_preserves_historical_subbalances_constraint() -> None:
    expression = _current_subbalances_check_expr()
    for field in CURRENTLY_PROTECTED_FIELDS:
        assert field in expression


def test_credit_ledger_service_not_modified_by_phase_contract() -> None:
    status = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--untracked-files=all",
            "src/services/credit_ledger_service.py",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    assert status == ""
