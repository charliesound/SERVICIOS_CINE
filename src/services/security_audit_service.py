from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("servicios_cine.security_audit")


def _log(event: str, detail: Optional[dict[str, Any]] = None) -> None:
    msg = f"SECURITY_AUDIT event={event}"
    if detail:
        safe = {k: v for k, v in detail.items() if k not in ("password", "secret", "token", "key")}
        msg += f" detail={safe}"
    logger.info(msg)


def auth_success(user_id: str, method: str = "jwt") -> None:
    _log("auth_success", {"user_id": user_id, "method": method})


def auth_failed(reason: str, identity: Optional[str] = None) -> None:
    _log("auth_failed", {"reason": reason, "identity": identity})


def token_expired(user_id: Optional[str] = None) -> None:
    _log("token_expired", {"user_id": user_id})


def token_invalid(reason: str, token_hint: Optional[str] = None) -> None:
    _log("token_invalid", {"reason": reason, "token_hint": token_hint})


def missing_scope(user_id: Optional[str], scope: str) -> None:
    _log("missing_scope", {"user_id": user_id, "scope": scope})


def missing_role(user_id: Optional[str], role: str) -> None:
    _log("missing_role", {"user_id": user_id, "role": role})


def internal_api_key_used(key_name: Optional[str] = None) -> None:
    _log("internal_api_key_used", {"key_name": key_name})


def auth_disabled_dev_bypass(path: str) -> None:
    _log("auth_disabled_dev_bypass", {"path": path})
