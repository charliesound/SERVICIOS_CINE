from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_transition_service import (
    ACCOUNTING_ACTION_CONSUME,
    ACCOUNTING_ACTION_NONE,
    ACCOUNTING_ACTION_RELEASE,
    ACCOUNTING_ACTION_RESERVE,
    AIJobTransitionError,
    build_ai_job_transition_plan,
    get_ai_job_transition_accounting_action,
    is_ai_job_transition_terminal,
    should_ai_job_transition_consume_credits,
    should_ai_job_transition_release_credits,
    validate_ai_job_transition,
)


class TestAIJobTransitionPlan:
    def test_builds_valid_created_to_estimated_plan(self) -> None:
        plan = build_ai_job_transition_plan("created", "estimated")

        assert plan.from_status == "created"
        assert plan.to_status == "estimated"
        assert plan.accounting_action == ACCOUNTING_ACTION_NONE
        assert plan.timestamp_field == "estimated_at"
        assert plan.is_terminal is False
        assert plan.requires_consumption is False
        assert plan.requires_release is False

    def test_builds_valid_credit_checked_to_reserved_plan(self) -> None:
        plan = build_ai_job_transition_plan("credit_checked", "reserved")

        assert plan.accounting_action == ACCOUNTING_ACTION_RESERVE
        assert plan.timestamp_field == "reserved_at"
        assert plan.requires_reservation_entry is True
        assert plan.requires_consume_entry is False
        assert plan.requires_release_entry is False

    def test_builds_valid_succeeded_to_consume_pending_plan(self) -> None:
        plan = build_ai_job_transition_plan("succeeded", "consume_pending")

        assert plan.accounting_action == ACCOUNTING_ACTION_NONE
        assert plan.timestamp_field == "consume_pending_at"
        assert plan.requires_consumption is True
        assert plan.requires_consume_entry is False
        assert should_ai_job_transition_consume_credits("succeeded", "consume_pending") is False

    def test_builds_valid_consume_pending_to_consumed_plan(self) -> None:
        plan = build_ai_job_transition_plan("consume_pending", "consumed")

        assert plan.accounting_action == ACCOUNTING_ACTION_CONSUME
        assert plan.timestamp_field == "consumed_at"
        assert plan.requires_consume_entry is True
        assert plan.is_terminal is True
        assert should_ai_job_transition_consume_credits("consume_pending", "consumed") is True
        assert is_ai_job_transition_terminal("consume_pending", "consumed") is True

    def test_builds_valid_failed_to_release_pending_plan(self) -> None:
        plan = build_ai_job_transition_plan("failed", "release_pending")

        assert plan.accounting_action == ACCOUNTING_ACTION_NONE
        assert plan.timestamp_field == "release_pending_at"
        assert plan.requires_release is True
        assert plan.requires_release_entry is False
        assert should_ai_job_transition_release_credits("failed", "release_pending") is False

    def test_builds_valid_release_pending_to_released_plan(self) -> None:
        plan = build_ai_job_transition_plan("release_pending", "released")

        assert plan.accounting_action == ACCOUNTING_ACTION_RELEASE
        assert plan.timestamp_field == "released_at"
        assert plan.requires_release_entry is True
        assert plan.is_terminal is True
        assert should_ai_job_transition_release_credits("release_pending", "released") is True
        assert is_ai_job_transition_terminal("release_pending", "released") is True

    def test_builds_reserved_cancel_release_path(self) -> None:
        cancel_requested = build_ai_job_transition_plan("reserved", "cancel_requested")
        cancelled = build_ai_job_transition_plan("cancel_requested", "cancelled")
        release_pending = build_ai_job_transition_plan("cancelled", "release_pending")
        released = build_ai_job_transition_plan("release_pending", "released")

        assert cancel_requested.timestamp_field == "cancel_requested_at"
        assert cancelled.timestamp_field == "cancelled_at"
        assert release_pending.timestamp_field == "release_pending_at"
        assert released.accounting_action == ACCOUNTING_ACTION_RELEASE

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            ("created", "running"),
            ("queued", "consumed"),
            ("released", "consumed"),
        ],
    )
    def test_rejects_invalid_transitions(self, from_status: str, to_status: str) -> None:
        with pytest.raises(AIJobTransitionError, match="Invalid AI job transition plan"):
            build_ai_job_transition_plan(from_status, to_status)

    def test_normalizes_spaces_in_statuses(self) -> None:
        plan = build_ai_job_transition_plan("  release_pending ", " released  ")

        assert plan.from_status == "release_pending"
        assert plan.to_status == "released"
        assert plan.accounting_action == ACCOUNTING_ACTION_RELEASE

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            ("unknown", "estimated"),
            ("created", "unknown"),
            ("", "estimated"),
        ],
    )
    def test_rejects_unknown_or_invalid_statuses(self, from_status: str, to_status: str) -> None:
        with pytest.raises(AIJobTransitionError, match="Invalid AI job transition plan"):
            validate_ai_job_transition(from_status, to_status)

    @pytest.mark.parametrize(
        ("to_status", "expected_timestamp_field"),
        [
            ("estimated", "estimated_at"),
            ("credit_checked", "credit_checked_at"),
            ("reserved", "reserved_at"),
            ("queued", "queued_at"),
            ("running", "started_at"),
            ("succeeded", "finished_at"),
            ("partial_succeeded", "finished_at"),
            ("failed", "finished_at"),
            ("cancel_requested", "cancel_requested_at"),
            ("cancelled", "cancelled_at"),
            ("consume_pending", "consume_pending_at"),
            ("consumed", "consumed_at"),
            ("release_pending", "release_pending_at"),
            ("released", "released_at"),
            ("expired", "expires_at"),
        ],
    )
    def test_timestamp_field_by_destination(
        self,
        to_status: str,
        expected_timestamp_field: str,
    ) -> None:
        from_status_by_to_status = {
            "estimated": "created",
            "credit_checked": "estimated",
            "reserved": "credit_checked",
            "queued": "reserved",
            "running": "queued",
            "succeeded": "running",
            "partial_succeeded": "running",
            "failed": "running",
            "cancel_requested": "queued",
            "cancelled": "cancel_requested",
            "consume_pending": "succeeded",
            "consumed": "consume_pending",
            "release_pending": "failed",
            "released": "release_pending",
            "expired": "reserved",
        }

        plan = build_ai_job_transition_plan(
            from_status_by_to_status[to_status],
            to_status,
        )

        assert plan.timestamp_field == expected_timestamp_field

    def test_module_is_pure_and_does_not_import_db_or_orm(self) -> None:
        module_source = (
            ROOT / "src" / "services" / "ai_job_transition_service.py"
        ).read_text(encoding="utf-8")

        assert "sqlalchemy" not in module_source
        assert "AsyncSession" not in module_source
        assert "database import" not in module_source

    def test_accounting_action_helper_matches_terminal_actions(self) -> None:
        assert (
            get_ai_job_transition_accounting_action("credit_checked", "reserved")
            == ACCOUNTING_ACTION_RESERVE
        )
        assert (
            get_ai_job_transition_accounting_action("consume_pending", "consumed")
            == ACCOUNTING_ACTION_CONSUME
        )
        assert (
            get_ai_job_transition_accounting_action("release_pending", "released")
            == ACCOUNTING_ACTION_RELEASE
        )
        assert (
            get_ai_job_transition_accounting_action("created", "estimated")
            == ACCOUNTING_ACTION_NONE
        )
