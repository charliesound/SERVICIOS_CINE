"""CID Local Media Agent — coarse session/session-boundary identity.

Pure, read-only helper that derives a deterministic, portable *coarse*
recording/session identity from a **relative** media path. It is deliberately
ignorant of drive letters, UNC mounts, person names, and any vendor/color
metadata.

Why this exists
---------------
The historical grouping bucket key used only the immediate parent directory
name. Unrelated trees whose immediate parents happened to collide (``CLIP``,
``M4ROOT``, ``Tarjeta 1``, ``Campo``, ...) collapsed into one bucket for
pairwise comparison, merging material that belongs to different people/events.

This module replaces that single-level key with a *coarse* identity derived
from the meaningful upper lineage of the relative path, discarding generic
terminal media/container and camera-card components.

Important scope note
--------------------
This is a **bucket-boundary** improvement, **NOT** an editorial
"different directory = never related" rule. Distinct card numbers, camera
folders and external-audio folders that share the same logical event lineage
still map to the same coarse bucket, so legitimate multi-camera,
camera + external-WAV and multi-card relationships remain eligible for the
existing relationship/sync stage.

Contract
--------
- Input is a relative path string (POSIX ``/`` and Windows ``\\`` separators
  are both accepted). Input is by contract relative; a leading drive letter
  (``C:``, ``F:``) or UNC server/share prefix, when present, is stripped and is
  never part of the identity.
- Output is a deterministic string. Same input always yields the same output.
  No hashing, no randomness, no media I/O, no filesystem access.
- Generic/structural recognition is case-insensitive and non-destructive to
  the original display path.

Strategy
--------
- Split the relative path into components (dropping the trailing file name).
- Drop *generic* terminal components: structural container tokens
  (``M4ROOT``, ``CLIP``, ``PRIVATE``, ``AVCHD``, ``XDROOT``, ``CONTENTS``) and
  card-like labels (``Tarjeta``, ``Tarjeta 1``, ``Tarjeta2``, ``Tarjeta 01``).
- Retain the first ``MEANINGFUL_RETENTION_DEPTH`` meaningful components as the
  coarse identity. Two components recreate the logical *person/event* scope:
  they separate different people/events while collapsing card/camera/audio
  sub-folders below that scope into one compatible bucket.
"""

from __future__ import annotations

import re

# Structural media/container components that carry no session semantics.
# Conservative and deliberately small (not a manufacturer taxonomy).
GENERIC_CONTAINER_TOKENS = frozenset(
    {"m4root", "clip", "private", "avchd", "xdroot", "contents"}
)

# Card-like labels: "Tarjeta", "Tarjeta 1", "Tarjeta 01", "Tarjeta2", ...
_GENERIC_CARD_RE = re.compile(r"^tarjeta[\s_]*[0-9]*$", re.IGNORECASE)

# Number of meaningful lineage components retained as the coarse session id.
# This is the person+event scope; deeper card/camera/audio folders collapse
# into it, while different events/persons (which differ within this depth)
# remain separated.
MEANINGFUL_RETENTION_DEPTH = 2

_FALLBACK_SESSION = "session"


def _is_generic_component(component: str) -> bool:
    """Return True for non-semantic structural/card components (case-insensitive)."""
    token = component.strip()
    if token.lower() in GENERIC_CONTAINER_TOKENS:
        return True
    return bool(_GENERIC_CARD_RE.match(token))


def _relative_parts(relative_path: object) -> list[str]:
    """Split a path into components, stripping any root (drive/UNC) prefix."""
    raw = str(relative_path).replace("\\", "/")
    unc = raw.startswith("/")
    parts = [p for p in raw.split("/") if p != ""]

    # Strip a Windows drive letter token (e.g. "C:", "F:").
    if parts and len(parts[0]) == 2 and parts[0][0].isalpha() and parts[0][1] == ":":
        parts = parts[1:]
        unc = False
    # Strip a UNC server/share root (leading "//").
    if unc and len(parts) >= 2:
        parts = parts[2:]
    elif unc and len(parts) == 1:
        parts = []
    return parts


def meaningful_lineage(relative_path: object) -> list[str]:
    """Return the meaningful (non-generic) parent components, in path order."""
    parts = _relative_parts(relative_path)
    if not parts:
        return []
    parents = parts[:-1]
    return [c for c in parents if not _is_generic_component(c)]


def coarse_session_id(relative_path: object) -> str:
    """Return a deterministic, portable coarse session identity.

    Uses the meaningful upper lineage of the relative path, retaining at most
    ``MEANINGFUL_RETENTION_DEPTH`` meaningful components. Falls back to the
    full parent chain (or the file stem) when no meaningful ancestor remains,
    so the result is always a non-empty, deterministic, per-run-stable string.
    """
    parts = _relative_parts(relative_path)
    if not parts:
        return _FALLBACK_SESSION

    parents = parts[:-1]
    meaningful = [c for c in parents if not _is_generic_component(c)]
    if meaningful:
        retained = meaningful[:MEANINGFUL_RETENTION_DEPTH]
        return "/".join(retained)

    if parents:
        # No meaningful ancestor: use the full available parent context.
        return "/".join(parents)

    stem = parts[-1].rsplit(".", 1)[0]
    return stem or _FALLBACK_SESSION
