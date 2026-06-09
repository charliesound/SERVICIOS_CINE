from __future__ import annotations

from dataclasses import dataclass

from services.ai_job_status_service import (
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_CONSUME_PENDING,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_ESTIMATED,
    AI_JOB_STATUS_EXPIRED,
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_QUEUED,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RELEASE_PENDING,
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_RUNNING,
    AI_JOB_STATUS_SUCCEEDED,
    AIJobStatusError,
    can_transition_ai_job_status,
    is_ai_job_terminal_status,
    normalize_ai_job_status,
    requires_ai_job_credit_consumption,
    requires_ai_job_credit_release,
    validate_ai_job_status_transition,
)


ACCOUNTING_ACTION_NONE = "none"
ACCOUNTING_ACTION_RESERVE = "reserve"
ACCOUNTING_ACTION_CONSUME = "consume"
ACCOUNTING_ACTION_RELEASE = "release"

TIMESTAMP_FIELD_BY_STATUS: dict[str, str] = {
    AI_JOB_STATUS_ESTIMATED: "estimated_at",
    AI_JOB_STATUS_CREDIT_CHECKED: "credit_checked_at",
    AI_JOB_STATUS_RESERVED: "reserved_at",
    AI_JOB_STATUS_QUEUED: "queued_at",
    AI_JOB_STATUS_RUNNING: "started_at",
    AI_JOB_STATUS_SUCCEEDED: "finished_at",
    AI_JOB_STATUS_PARTIAL_SUCCEEDED: "finished_at",
    AI_JOB_STATUS_FAILED: "finished_at",
    AI_JOB_STATUS_CANCEL_REQUESTED: "cancel_requested_at",
    AI_JOB_STATUS_CANCELLED: "cancelled_at",
    AI_JOB_STATUS_CONSUME_PENDING: "consume_pending_at",
    AI_JOB_STATUS_CONSUMED: "consumed_at",
    AI_JOB_STATUS_RELEASE_PENDING: "release_pending_at",
    AI_JOB_STATUS_RELEASED: "released_at",
    # Expiration is modeled as its own lifecycle boundary, so the recommended
    # field is `expires_at` rather than reusing `finished_at`.
    AI_JOB_STATUS_EXPIRED: "expires_at",
}


__all__ = [
    "ACCOUNTING_ACTION_NONE",
    "ACCOUNTING_ACTION_RESERVE",
    "ACCOUNTING_ACTION_CONSUME",
    "ACCOUNTING_ACTION_RELEASE",
    "AIJobTransitionError",
    "AIJobTransitionPlan",
    "build_ai_job_transition_plan",
    "validate_ai_job_transition",
    "get_ai_job_transition_accounting_action",
    "should_ai_job_transition_consume_credits",
    "should_ai_job_transition_release_credits",
    "is_ai_job_transition_terminal",
]


class AIJobTransitionError(Exception):
    """Raised when an AI job transition plan cannot be built safely."""


@dataclass(frozen=True)
class AIJobTransitionPlan:
    from_status: str
    to_status: str
    is_terminal: bool
    requires_consumption: bool
    requires_release: bool
    accounting_action: str
    timestamp_field: str | None
    requires_reservation_entry: bool
    requires_consume_entry: bool
    requires_release_entry: bool


def validate_ai_job_transition(from_status: str, to_status: str) -> None:
    _normalize_and_validate_transition(from_status, to_status)


def get_ai_job_transition_accounting_action(from_status: str, to_status: str) -> str:
    normalized_from, normalized_to = _normalize_and_validate_transition(from_status, to_status)
    if normalized_to == AI_JOB_STATUS_RESERVED:
        return ACCOUNTING_ACTION_RESERVE
    if normalized_to == AI_JOB_STATUS_CONSUMED:
        return ACCOUNTING_ACTION_CONSUME
    if normalized_to == AI_JOB_STATUS_RELEASED:
        return ACCOUNTING_ACTION_RELEASE
    return ACCOUNTING_ACTION_NONE


def should_ai_job_transition_consume_credits(from_status: str, to_status: str) -> bool:
    return (
        get_ai_job_transition_accounting_action(from_status, to_status)
        == ACCOUNTING_ACTION_CONSUME
    )


def should_ai_job_transition_release_credits(from_status: str, to_status: str) -> bool:
    return (
        get_ai_job_transition_accounting_action(from_status, to_status)
        == ACCOUNTING_ACTION_RELEASE
    )


def is_ai_job_transition_terminal(from_status: str, to_status: str) -> bool:
    _, normalized_to = _normalize_and_validate_transition(from_status, to_status)
    return is_ai_job_terminal_status(normalized_to)


def build_ai_job_transition_plan(from_status: str, to_status: str) -> AIJobTransitionPlan:
    normalized_from, normalized_to = _normalize_and_validate_transition(from_status, to_status)
    accounting_action = get_ai_job_transition_accounting_action(
        normalized_from,
        normalized_to,
    )
    return AIJobTransitionPlan(
        from_status=normalized_from,
        to_status=normalized_to,
        is_terminal=is_ai_job_terminal_status(normalized_to),
        requires_consumption=requires_ai_job_credit_consumption(normalized_to),
        requires_release=requires_ai_job_credit_release(normalized_to),
        accounting_action=accounting_action,
        timestamp_field=TIMESTAMP_FIELD_BY_STATUS.get(normalized_to),
        requires_reservation_entry=accounting_action == ACCOUNTING_ACTION_RESERVE,
        requires_consume_entry=accounting_action == ACCOUNTING_ACTION_CONSUME,
        requires_release_entry=accounting_action == ACCOUNTING_ACTION_RELEASE,
    )


def _normalize_and_validate_transition(from_status: str, to_status: str) -> tuple[str, str]:
    try:
        normalized_from = normalize_ai_job_status(from_status)
        normalized_to = normalize_ai_job_status(to_status)
        validate_ai_job_status_transition(normalized_from, normalized_to)
    except AIJobStatusError as exc:
        raise AIJobTransitionError(
            "Invalid AI job transition plan: {0!r} -> {1!r}".format(
                from_status,
                to_status,
            )
        ) from exc

    if not can_transition_ai_job_status(normalized_from, normalized_to):
        raise AIJobTransitionError(
            "Invalid AI job transition plan: {0} -> {1}".format(
                normalized_from,
                normalized_to,
            )
        )

    return normalized_from, normalized_to
