from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.ai_job_status_service import (
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_CONSUME_PENDING,
    AI_JOB_STATUS_CREATED,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_ESTIMATED,
    AI_JOB_STATUS_EXPIRED,
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_QUEUED,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RELEASE_PENDING,
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_RETRY_PENDING,
    AI_JOB_STATUS_RUNNING,
    AI_JOB_STATUS_SUCCEEDED,
    AI_JOB_STATUSES,
    InvalidAIJobStatusTransitionError,
    UnknownAIJobStatusError,
    can_transition_ai_job_status,
    get_allowed_ai_job_status_transitions,
    is_ai_job_reserved_accounting_status,
    is_ai_job_terminal_status,
    is_known_ai_job_status,
    normalize_ai_job_status,
    requires_ai_job_credit_consumption,
    requires_ai_job_credit_release,
    validate_ai_job_status_transition,
)


class TestCanonicalStatuses:
    def test_recognizes_all_canonical_statuses(self) -> None:
        for status in AI_JOB_STATUSES:
            assert is_known_ai_job_status(status) is True

    def test_rejects_unknown_status(self) -> None:
        assert is_known_ai_job_status("unknown") is False
        with pytest.raises(UnknownAIJobStatusError, match="Unknown AI job status"):
            validate_ai_job_status_transition("unknown", AI_JOB_STATUS_ESTIMATED)

    def test_normalizes_status_with_strip(self) -> None:
        assert normalize_ai_job_status("  queued  ") == AI_JOB_STATUS_QUEUED

    @pytest.mark.parametrize("invalid_value", ["", "   ", 123, None])
    def test_rejects_empty_or_non_string_status(self, invalid_value: object) -> None:
        with pytest.raises(UnknownAIJobStatusError, match="non-empty string"):
            normalize_ai_job_status(invalid_value)  # type: ignore[arg-type]


class TestTransitions:
    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            (AI_JOB_STATUS_CREATED, AI_JOB_STATUS_ESTIMATED),
            (AI_JOB_STATUS_ESTIMATED, AI_JOB_STATUS_CREDIT_CHECKED),
            (AI_JOB_STATUS_CREDIT_CHECKED, AI_JOB_STATUS_RESERVED),
            (AI_JOB_STATUS_RESERVED, AI_JOB_STATUS_QUEUED),
            (AI_JOB_STATUS_RESERVED, AI_JOB_STATUS_CANCEL_REQUESTED),
            (AI_JOB_STATUS_QUEUED, AI_JOB_STATUS_RUNNING),
            (AI_JOB_STATUS_QUEUED, AI_JOB_STATUS_CANCEL_REQUESTED),
            (AI_JOB_STATUS_RUNNING, AI_JOB_STATUS_SUCCEEDED),
            (AI_JOB_STATUS_RUNNING, AI_JOB_STATUS_PARTIAL_SUCCEEDED),
            (AI_JOB_STATUS_RUNNING, AI_JOB_STATUS_FAILED),
            ("failed", AI_JOB_STATUS_RELEASE_PENDING),
            (AI_JOB_STATUS_RELEASE_PENDING, AI_JOB_STATUS_RELEASED),
            (AI_JOB_STATUS_FAILED, AI_JOB_STATUS_RETRY_PENDING),
            (AI_JOB_STATUS_RETRY_PENDING, AI_JOB_STATUS_QUEUED),
            (AI_JOB_STATUS_RESERVED, AI_JOB_STATUS_EXPIRED),
            (AI_JOB_STATUS_EXPIRED, AI_JOB_STATUS_RELEASE_PENDING),
            (AI_JOB_STATUS_PARTIAL_SUCCEEDED, AI_JOB_STATUS_CONSUME_PENDING),
        ],
    )
    def test_allows_canonical_transitions(self, from_status: str, to_status: str) -> None:
        assert can_transition_ai_job_status(from_status, to_status) is True
        validate_ai_job_status_transition(from_status, to_status)

    @pytest.mark.parametrize(
        ("from_status", "to_status"),
        [
            (AI_JOB_STATUS_CREATED, AI_JOB_STATUS_RUNNING),
            (AI_JOB_STATUS_ESTIMATED, AI_JOB_STATUS_RUNNING),
            (AI_JOB_STATUS_QUEUED, AI_JOB_STATUS_CONSUMED),
            (AI_JOB_STATUS_RELEASED, AI_JOB_STATUS_CONSUMED),
            (AI_JOB_STATUS_CONSUMED, AI_JOB_STATUS_RELEASED),
        ],
    )
    def test_rejects_prohibited_transitions(self, from_status: str, to_status: str) -> None:
        assert can_transition_ai_job_status(from_status, to_status) is False
        with pytest.raises(
            InvalidAIJobStatusTransitionError,
            match="Invalid AI job status transition",
        ):
            validate_ai_job_status_transition(from_status, to_status)

    def test_no_direct_transition_to_running_without_reserved_then_queued(self) -> None:
        assert can_transition_ai_job_status(AI_JOB_STATUS_CREATED, AI_JOB_STATUS_RUNNING) is False
        assert can_transition_ai_job_status(AI_JOB_STATUS_ESTIMATED, AI_JOB_STATUS_RUNNING) is False
        assert can_transition_ai_job_status(AI_JOB_STATUS_CREDIT_CHECKED, AI_JOB_STATUS_RUNNING) is False

    def test_allowed_transitions_helper_returns_expected_tuple(self) -> None:
        assert get_allowed_ai_job_status_transitions(AI_JOB_STATUS_FAILED) == (
            AI_JOB_STATUS_RELEASE_PENDING,
            AI_JOB_STATUS_RETRY_PENDING,
        )


class TestStatusGroups:
    def test_consumed_and_released_are_terminal(self) -> None:
        assert is_ai_job_terminal_status(AI_JOB_STATUS_CONSUMED) is True
        assert is_ai_job_terminal_status(AI_JOB_STATUS_RELEASED) is True
        assert is_ai_job_terminal_status(AI_JOB_STATUS_RUNNING) is False

    def test_reserved_accounting_statuses_are_coherent(self) -> None:
        assert is_ai_job_reserved_accounting_status(AI_JOB_STATUS_RESERVED) is True
        assert is_ai_job_reserved_accounting_status(AI_JOB_STATUS_RUNNING) is True
        assert is_ai_job_reserved_accounting_status(AI_JOB_STATUS_FAILED) is True
        assert is_ai_job_reserved_accounting_status(AI_JOB_STATUS_RELEASED) is False

    def test_consumption_required_statuses_are_coherent(self) -> None:
        assert requires_ai_job_credit_consumption(AI_JOB_STATUS_SUCCEEDED) is True
        assert requires_ai_job_credit_consumption(AI_JOB_STATUS_PARTIAL_SUCCEEDED) is True
        assert requires_ai_job_credit_consumption(AI_JOB_STATUS_CONSUME_PENDING) is True
        assert requires_ai_job_credit_consumption(AI_JOB_STATUS_FAILED) is False

    def test_release_required_statuses_are_coherent(self) -> None:
        assert requires_ai_job_credit_release(AI_JOB_STATUS_FAILED) is True
        assert requires_ai_job_credit_release(AI_JOB_STATUS_CANCELLED) is True
        assert requires_ai_job_credit_release(AI_JOB_STATUS_EXPIRED) is True
        assert requires_ai_job_credit_release(AI_JOB_STATUS_RELEASE_PENDING) is True
        assert requires_ai_job_credit_release(AI_JOB_STATUS_CONSUMED) is False

    def test_failed_release_and_retry_paths_are_allowed(self) -> None:
        assert can_transition_ai_job_status(AI_JOB_STATUS_FAILED, AI_JOB_STATUS_RELEASE_PENDING) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_RELEASE_PENDING, AI_JOB_STATUS_RELEASED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_FAILED, AI_JOB_STATUS_RETRY_PENDING) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_RETRY_PENDING, AI_JOB_STATUS_QUEUED) is True

    def test_reserved_expired_release_path_is_allowed(self) -> None:
        assert can_transition_ai_job_status(AI_JOB_STATUS_RESERVED, AI_JOB_STATUS_EXPIRED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_EXPIRED, AI_JOB_STATUS_RELEASE_PENDING) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_RELEASE_PENDING, AI_JOB_STATUS_RELEASED) is True

    def test_reserved_cancel_release_path_is_allowed(self) -> None:
        assert can_transition_ai_job_status(AI_JOB_STATUS_RESERVED, AI_JOB_STATUS_CANCEL_REQUESTED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_CANCEL_REQUESTED, AI_JOB_STATUS_CANCELLED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_CANCELLED, AI_JOB_STATUS_RELEASE_PENDING) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_RELEASE_PENDING, AI_JOB_STATUS_RELEASED) is True

    def test_queued_cancel_release_path_is_allowed(self) -> None:
        assert can_transition_ai_job_status(AI_JOB_STATUS_QUEUED, AI_JOB_STATUS_CANCEL_REQUESTED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_CANCEL_REQUESTED, AI_JOB_STATUS_CANCELLED) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_CANCELLED, AI_JOB_STATUS_RELEASE_PENDING) is True
        assert can_transition_ai_job_status(AI_JOB_STATUS_RELEASE_PENDING, AI_JOB_STATUS_RELEASED) is True
