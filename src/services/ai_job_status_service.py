from __future__ import annotations


AI_JOB_STATUS_CREATED = "created"
AI_JOB_STATUS_ESTIMATED = "estimated"
AI_JOB_STATUS_CREDIT_CHECKED = "credit_checked"
AI_JOB_STATUS_RESERVED = "reserved"
AI_JOB_STATUS_QUEUED = "queued"
AI_JOB_STATUS_RUNNING = "running"
AI_JOB_STATUS_SUCCEEDED = "succeeded"
AI_JOB_STATUS_PARTIAL_SUCCEEDED = "partial_succeeded"
AI_JOB_STATUS_FAILED = "failed"
AI_JOB_STATUS_CANCEL_REQUESTED = "cancel_requested"
AI_JOB_STATUS_CANCELLED = "cancelled"
AI_JOB_STATUS_CONSUME_PENDING = "consume_pending"
AI_JOB_STATUS_CONSUMED = "consumed"
AI_JOB_STATUS_RELEASE_PENDING = "release_pending"
AI_JOB_STATUS_RELEASED = "released"
AI_JOB_STATUS_RETRY_PENDING = "retry_pending"
AI_JOB_STATUS_EXPIRED = "expired"


AI_JOB_STATUSES = (
    AI_JOB_STATUS_CREATED,
    AI_JOB_STATUS_ESTIMATED,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_QUEUED,
    AI_JOB_STATUS_RUNNING,
    AI_JOB_STATUS_SUCCEEDED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CONSUME_PENDING,
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_RELEASE_PENDING,
    AI_JOB_STATUS_RELEASED,
    AI_JOB_STATUS_RETRY_PENDING,
    AI_JOB_STATUS_EXPIRED,
)

AI_JOB_TERMINAL_STATUSES = (
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_RELEASED,
)

AI_JOB_RESERVED_ACCOUNTING_STATUSES = (
    AI_JOB_STATUS_RESERVED,
    AI_JOB_STATUS_QUEUED,
    AI_JOB_STATUS_RUNNING,
    AI_JOB_STATUS_CANCEL_REQUESTED,
    AI_JOB_STATUS_SUCCEEDED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_CONSUME_PENDING,
    AI_JOB_STATUS_RELEASE_PENDING,
    AI_JOB_STATUS_RETRY_PENDING,
    AI_JOB_STATUS_EXPIRED,
)

AI_JOB_CONSUMPTION_REQUIRED_STATUSES = (
    AI_JOB_STATUS_SUCCEEDED,
    AI_JOB_STATUS_PARTIAL_SUCCEEDED,
    AI_JOB_STATUS_CONSUME_PENDING,
)

AI_JOB_RELEASE_REQUIRED_STATUSES = (
    AI_JOB_STATUS_FAILED,
    AI_JOB_STATUS_CANCELLED,
    AI_JOB_STATUS_EXPIRED,
    AI_JOB_STATUS_RELEASE_PENDING,
)

AI_JOB_EXECUTABLE_STATUSES = (
    AI_JOB_STATUS_QUEUED,
)

AI_JOB_EXECUTION_BLOCKED_STATUSES = (
    AI_JOB_STATUS_CREATED,
    AI_JOB_STATUS_ESTIMATED,
    AI_JOB_STATUS_CREDIT_CHECKED,
    AI_JOB_STATUS_CONSUMED,
    AI_JOB_STATUS_RELEASED,
)

AI_JOB_ALLOWED_STATUS_TRANSITIONS: dict[str, tuple[str, ...]] = {
    AI_JOB_STATUS_CREATED: (
        AI_JOB_STATUS_ESTIMATED,
        AI_JOB_STATUS_CANCELLED,
    ),
    AI_JOB_STATUS_ESTIMATED: (
        AI_JOB_STATUS_CREDIT_CHECKED,
        AI_JOB_STATUS_CANCELLED,
    ),
    AI_JOB_STATUS_CREDIT_CHECKED: (
        AI_JOB_STATUS_RESERVED,
        AI_JOB_STATUS_CANCELLED,
    ),
    AI_JOB_STATUS_RESERVED: (
        AI_JOB_STATUS_QUEUED,
        AI_JOB_STATUS_CANCEL_REQUESTED,
        AI_JOB_STATUS_EXPIRED,
    ),
    AI_JOB_STATUS_QUEUED: (
        AI_JOB_STATUS_RUNNING,
        AI_JOB_STATUS_CANCEL_REQUESTED,
    ),
    AI_JOB_STATUS_RUNNING: (
        AI_JOB_STATUS_SUCCEEDED,
        AI_JOB_STATUS_PARTIAL_SUCCEEDED,
        AI_JOB_STATUS_FAILED,
        AI_JOB_STATUS_CANCEL_REQUESTED,
    ),
    AI_JOB_STATUS_SUCCEEDED: (
        AI_JOB_STATUS_CONSUME_PENDING,
    ),
    AI_JOB_STATUS_PARTIAL_SUCCEEDED: (
        AI_JOB_STATUS_CONSUME_PENDING,
    ),
    AI_JOB_STATUS_FAILED: (
        AI_JOB_STATUS_RELEASE_PENDING,
        AI_JOB_STATUS_RETRY_PENDING,
    ),
    AI_JOB_STATUS_CANCEL_REQUESTED: (
        AI_JOB_STATUS_CANCELLED,
    ),
    AI_JOB_STATUS_CANCELLED: (
        AI_JOB_STATUS_RELEASE_PENDING,
    ),
    AI_JOB_STATUS_CONSUME_PENDING: (
        AI_JOB_STATUS_CONSUMED,
    ),
    AI_JOB_STATUS_CONSUMED: (),
    AI_JOB_STATUS_RELEASE_PENDING: (
        AI_JOB_STATUS_RELEASED,
    ),
    AI_JOB_STATUS_RELEASED: (),
    AI_JOB_STATUS_RETRY_PENDING: (
        AI_JOB_STATUS_QUEUED,
    ),
    AI_JOB_STATUS_EXPIRED: (
        AI_JOB_STATUS_RELEASE_PENDING,
    ),
}


__all__ = [
    "AI_JOB_STATUS_CREATED",
    "AI_JOB_STATUS_ESTIMATED",
    "AI_JOB_STATUS_CREDIT_CHECKED",
    "AI_JOB_STATUS_RESERVED",
    "AI_JOB_STATUS_QUEUED",
    "AI_JOB_STATUS_RUNNING",
    "AI_JOB_STATUS_SUCCEEDED",
    "AI_JOB_STATUS_PARTIAL_SUCCEEDED",
    "AI_JOB_STATUS_FAILED",
    "AI_JOB_STATUS_CANCEL_REQUESTED",
    "AI_JOB_STATUS_CANCELLED",
    "AI_JOB_STATUS_CONSUME_PENDING",
    "AI_JOB_STATUS_CONSUMED",
    "AI_JOB_STATUS_RELEASE_PENDING",
    "AI_JOB_STATUS_RELEASED",
    "AI_JOB_STATUS_RETRY_PENDING",
    "AI_JOB_STATUS_EXPIRED",
    "AI_JOB_STATUSES",
    "AI_JOB_TERMINAL_STATUSES",
    "AI_JOB_RESERVED_ACCOUNTING_STATUSES",
    "AI_JOB_CONSUMPTION_REQUIRED_STATUSES",
    "AI_JOB_RELEASE_REQUIRED_STATUSES",
    "AI_JOB_EXECUTABLE_STATUSES",
    "AI_JOB_EXECUTION_BLOCKED_STATUSES",
    "AI_JOB_ALLOWED_STATUS_TRANSITIONS",
    "AIJobStatusError",
    "UnknownAIJobStatusError",
    "InvalidAIJobStatusTransitionError",
    "normalize_ai_job_status",
    "is_known_ai_job_status",
    "is_ai_job_terminal_status",
    "is_ai_job_reserved_accounting_status",
    "requires_ai_job_credit_consumption",
    "requires_ai_job_credit_release",
    "can_transition_ai_job_status",
    "validate_ai_job_status_transition",
    "get_allowed_ai_job_status_transitions",
]


class AIJobStatusError(Exception):
    """Base error for AI job status helpers."""


class UnknownAIJobStatusError(AIJobStatusError):
    """Raised when a job status is not canonical."""


class InvalidAIJobStatusTransitionError(AIJobStatusError):
    """Raised when a job status transition is not allowed."""


def normalize_ai_job_status(status: str) -> str:
    if not isinstance(status, str):
        raise UnknownAIJobStatusError("AI job status must be a non-empty string")
    normalized = status.strip()
    if not normalized:
        raise UnknownAIJobStatusError("AI job status must be a non-empty string")
    return normalized


def is_known_ai_job_status(status: str) -> bool:
    try:
        normalized = normalize_ai_job_status(status)
    except UnknownAIJobStatusError:
        return False
    return normalized in AI_JOB_STATUSES


def _require_known_ai_job_status(status: str) -> str:
    normalized = normalize_ai_job_status(status)
    if normalized not in AI_JOB_STATUSES:
        raise UnknownAIJobStatusError("Unknown AI job status: {0}".format(normalized))
    return normalized


def is_ai_job_terminal_status(status: str) -> bool:
    return _require_known_ai_job_status(status) in AI_JOB_TERMINAL_STATUSES


def is_ai_job_reserved_accounting_status(status: str) -> bool:
    return _require_known_ai_job_status(status) in AI_JOB_RESERVED_ACCOUNTING_STATUSES


def requires_ai_job_credit_consumption(status: str) -> bool:
    return _require_known_ai_job_status(status) in AI_JOB_CONSUMPTION_REQUIRED_STATUSES


def requires_ai_job_credit_release(status: str) -> bool:
    return _require_known_ai_job_status(status) in AI_JOB_RELEASE_REQUIRED_STATUSES


def get_allowed_ai_job_status_transitions(status: str) -> tuple[str, ...]:
    normalized = _require_known_ai_job_status(status)
    return AI_JOB_ALLOWED_STATUS_TRANSITIONS[normalized]


def can_transition_ai_job_status(from_status: str, to_status: str) -> bool:
    normalized_from = _require_known_ai_job_status(from_status)
    normalized_to = _require_known_ai_job_status(to_status)
    return normalized_to in AI_JOB_ALLOWED_STATUS_TRANSITIONS[normalized_from]


def validate_ai_job_status_transition(from_status: str, to_status: str) -> None:
    normalized_from = _require_known_ai_job_status(from_status)
    normalized_to = _require_known_ai_job_status(to_status)
    if normalized_to not in AI_JOB_ALLOWED_STATUS_TRANSITIONS[normalized_from]:
        raise InvalidAIJobStatusTransitionError(
            "Invalid AI job status transition: {0} -> {1}".format(
                normalized_from,
                normalized_to,
            )
        )
