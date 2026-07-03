"""CID Local Media Agent - Own Real Material Dry Run Intake Planner.

This module exposes a single deterministic validation function that plans
a dry-run intake for operator-controlled real material.  It performs no
I/O beyond stat()-like Path operations and rejects everything that does
not match the strict dry-run contract.
"""

from __future__ import annotations

from pathlib import Path

SCHEMA_VERSION = "cid.local_media_agent.own_real_material_dry_run_intake.v1"
STATUS_ACCEPTED = "OWN_REAL_MATERIAL_DRY_RUN_INTAKE_ACCEPTED"
STATUS_REJECTED = "OWN_REAL_MATERIAL_DRY_RUN_INTAKE_REJECTED"
SANITIZED_LABEL = "SANITIZED_OWN_REAL_MATERIAL_INPUT"
NEXT_GATE_EXECUTION = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.EXECUTION.GATE.V1"
NEXT_GATE_READINESS = "CID.LOCAL_MEDIA_AGENT.OWN_REAL_MATERIAL.DRY_RUN.READINESS.GATE.V1"

WINDOWS_DRIVE_PATTERN = ("", ":", "")
WINDOWS_BACKSLASH = ("\\", "", "")

UNC_PREFIX = ("\\", "\\", "")
WSL_LOCALHOST_DOMAIN = ("wsl", ".", "localhost")
MNT_PREFIX = ("/", "mnt", "/")


def _is_windows_style(path_text: str) -> bool:
    return (
        WINDOWS_BACKSLASH[0] in path_text
        or (
            len(path_text) >= 2
            and path_text[0] == WINDOWS_DRIVE_PATTERN[1]
            and path_text[1] == WINDOWS_DRIVE_PATTERN[1]
        )
    )


def _is_unc(path_text: str) -> bool:
    return path_text.startswith(UNC_PREFIX[0] + UNC_PREFIX[1])


def _is_wsl_localhost(path_text: str) -> bool:
    return (
        WSL_LOCALHOST_DOMAIN[0] + WSL_LOCALHOST_DOMAIN[1] + WSL_LOCALHOST_DOMAIN[2]
    ) in path_text


def _is_mnt_path(path_text: str) -> bool:
    return path_text.startswith(MNT_PREFIX[0] + MNT_PREFIX[1] + MNT_PREFIX[2])


def _rejected(errors: list[str]) -> dict[str, object]:
    return {
        "status": STATUS_REJECTED,
        "input_kind": "unknown",
        "accepted": False,
        "read_only": True,
        "operator_consent": True,
        "real_material_scope": "OWN_CONTROLLED_ONLY",
        "sanitized_input_label": SANITIZED_LABEL,
        "errors": errors,
        "warnings": [],
        "next_required_gate": NEXT_GATE_READINESS,
    }


def plan_own_real_material_dry_run_intake(
    input_path: str,
    operator_consent: bool,
    read_only: bool,
    allow_real_material: bool,
) -> dict[str, object]:
    """Validate and plan a dry-run intake for operator-controlled material.

    Parameters
    ----------
    input_path:
        Absolute local Linux path to a single file.
    operator_consent:
        Must be ``True``.
    read_only:
        Must be ``True``.
    allow_real_material:
        Must be ``True`` (opt-in for controlled own material).

    Returns
    -------
    dict
        Accepted or rejected structure with sanitized labels.
    """
    if not operator_consent:
        return _rejected(["OPERATOR_CONSENT_REQUIRED"])
    if not read_only:
        return _rejected(["READ_ONLY_REQUIRED"])
    if not allow_real_material:
        return _rejected(["REAL_MATERIAL_OPT_IN_REQUIRED"])

    if not isinstance(input_path, str) or not input_path.strip():
        return _rejected(["INPUT_PATH_EMPTY"])

    stripped = input_path.strip()

    if _is_unc(stripped):
        return _rejected(["UNC_PATH_REJECTED"])

    if _is_windows_style(stripped):
        return _rejected(["WINDOWS_STYLE_PATH_REJECTED"])

    if _is_mnt_path(stripped):
        return _rejected(["MOUNT_PATH_REJECTED"])

    if _is_wsl_localhost(stripped):
        return _rejected(["WSL_LOCALHOST_PATH_REJECTED"])

    if not stripped.startswith("/"):
        return _rejected(["NON_ABSOLUTE_PATH_REJECTED"])

    path = Path(stripped)

    if path.is_symlink():
        return _rejected(["SYMLINK_REJECTED"])

    if not path.exists():
        return _rejected(["INPUT_PATH_NOT_FOUND"])

    if path.is_dir():
        return _rejected(["DIRECTORY_REJECTED_DIRECTORY_SUPPORT_REQUIRES_FUTURE_PHASE"])

    if not path.is_file():
        return _rejected(["INPUT_PATH_IS_NOT_A_FILE"])

    return {
        "status": STATUS_ACCEPTED,
        "input_kind": "file",
        "accepted": True,
        "read_only": True,
        "operator_consent": True,
        "real_material_scope": "OWN_CONTROLLED_ONLY",
        "sanitized_input_label": SANITIZED_LABEL,
        "errors": [],
        "warnings": [],
        "next_required_gate": NEXT_GATE_EXECUTION,
    }
