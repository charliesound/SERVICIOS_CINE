from __future__ import annotations

import logging
import os

from fastapi import HTTPException

logger = logging.getLogger("cid_test_mode")

VALID_TEST_PLANS = {"demo", "free", "creator", "producer", "studio", "enterprise"}


def is_test_mode_enabled() -> bool:
    return os.getenv("CID_INTERNAL_TEST_MODE_ENABLED", "false").strip().lower() == "true"


def get_tester_emails() -> set[str]:
    raw = os.getenv("CID_INTERNAL_TESTER_EMAILS", "").strip()
    if not raw:
        return set()
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def is_internal_tester(email: str | None) -> bool:
    if not is_test_mode_enabled() or not email:
        return False
    return email.strip().lower() in get_tester_emails()


def get_internal_test_plan() -> str:
    requested_plan = os.getenv("CID_INTERNAL_TEST_PLAN", "enterprise").strip().lower()
    if requested_plan in VALID_TEST_PLANS:
        return requested_plan

    logger.warning(
        "CID internal test mode requested invalid plan '%s'; falling back to enterprise",
        requested_plan,
    )
    return "enterprise"


def require_test_mode_enabled() -> None:
    if not is_test_mode_enabled():
        raise HTTPException(status_code=404, detail="CID internal test mode is disabled")


def resolve_test_access(email: str | None, is_admin: bool) -> dict:
    enabled = is_test_mode_enabled()
    normalized_email = (email or "").strip().lower()
    whitelisted = enabled and normalized_email in get_tester_emails()
    can_access = enabled and (bool(is_admin) or whitelisted)
    test_plan = get_internal_test_plan()

    if can_access:
        logger.warning(
            "CID internal test mode used for email=%s admin=%s",
            normalized_email or "unknown",
            bool(is_admin),
        )

    return {
        "enabled": enabled,
        "is_real_admin": bool(is_admin),
        "is_email_whitelisted": whitelisted,
        "is_internal_tester": whitelisted,
        "can_access_as_test_user": can_access,
        "test_plan": test_plan,
    }
