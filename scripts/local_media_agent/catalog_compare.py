"""CID Local Media Agent — pure incremental catalog comparison.

Compares a previous persistent catalog against a current filesystem scan
snapshot and classifies each media item deterministically:

- NEW        identity not in the previous catalog, root online
- UNCHANGED  same identity, same cheap fingerprint
- MODIFIED   same identity, size or mtime changed
- MISSING    identity in previous catalog, root online, absent from scan
- OFFLINE    identity in previous catalog, root unavailable (never MISSING)

``ERROR`` is intentionally NOT derived from the filesystem fingerprint; it is
produced during technical analysis and stored on the media item
(see ``media_catalog``). This module is pure: no ffprobe, no media I/O, no
filesystem access, so it is fully unit-testable without real media.
"""

from __future__ import annotations

from typing import Any

CLASSIFICATION_NEW = "NEW"
CLASSIFICATION_UNCHANGED = "UNCHANGED"
CLASSIFICATION_MODIFIED = "MODIFIED"
CLASSIFICATION_MISSING = "MISSING"
CLASSIFICATION_OFFLINE = "OFFLINE"

CLASSIFICATIONS = (
    CLASSIFICATION_NEW,
    CLASSIFICATION_UNCHANGED,
    CLASSIFICATION_MODIFIED,
    CLASSIFICATION_MISSING,
    CLASSIFICATION_OFFLINE,
)

# Cheap fingerprint: size + mtime_ns. No full media hashing during scan/compare.
FINGERPRINT_CONTRACT = "size+mtime_ns"


def _root_online(catalog: dict[str, Any], source_root_id: str, online_root_ids: set[str]) -> bool:
    return source_root_id in online_root_ids


def _fingerprint(item: dict[str, Any]) -> tuple[int | None, int | None]:
    size = item.get("size")
    mtime_ns = item.get("mtime_ns")
    if not isinstance(size, int) or isinstance(size, bool):
        size = None
    if not isinstance(mtime_ns, int) or isinstance(mtime_ns, bool):
        mtime_ns = None
    return (size, mtime_ns)


def _current_lookup(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map identity key -> current file entry for online roots only."""
    files = snapshot.get("files", [])
    result: dict[str, dict[str, Any]] = {}
    for file_entry in files if isinstance(files, list) else []:
        if not isinstance(file_entry, dict):
            continue
        source_root_id = file_entry.get("source_root_id")
        relative_path = file_entry.get("relative_path")
        if not isinstance(source_root_id, str) or not isinstance(relative_path, str):
            continue
        key = f"{source_root_id}::{relative_path}"
        result[key] = file_entry
    return result


def classify_previous_item(
    item: dict[str, Any],
    *,
    online_root_ids: set[str],
    current: dict[str, dict[str, Any]],
) -> str:
    """Classify a single previous-catalog item.

    ``current`` is the online-root lookup map produced by ``_current_lookup``.
    A previous item whose root is offline is always OFFLINE, never MISSING.
    """
    source_root_id = item.get("source_root_id")
    relative_path = item.get("relative_path")
    if not isinstance(source_root_id, str) or not isinstance(relative_path, str):
        return CLASSIFICATION_MISSING

    key = f"{source_root_id}::{relative_path}"
    if not _root_online(item, source_root_id, online_root_ids):
        return CLASSIFICATION_OFFLINE

    current_entry = current.get(key)
    if current_entry is None:
        return CLASSIFICATION_MISSING

    prev = _fingerprint(item)
    now = _fingerprint(current_entry)
    if prev == now:
        return CLASSIFICATION_UNCHANGED
    return CLASSIFICATION_MODIFIED


def compare_catalogs(
    previous: dict[str, Any],
    snapshot: dict[str, Any],
) -> dict[str, Any]:
    """Compare a previous catalog against a current scan snapshot.

    Snapshot contract::

        {
          "online_root_ids": ["root-id", ...],
          "files": [
            {"source_root_id": "...", "relative_path": "...",
             "size": int, "mtime_ns": int},
             ...
          ]
        }

    Returns a deterministic dict with per-classification ordered lists and
    counts.
    """
    online_root_ids = {str(r) for r in snapshot.get("online_root_ids", [])}
    current = _current_lookup(snapshot)

    classified: dict[str, list[str]] = {c: [] for c in CLASSIFICATIONS}
    previous_items = previous.get("media_items", {})
    if isinstance(previous_items, dict):
        for key, item in previous_items.items():
            if not isinstance(item, dict):
                continue
            classification = classify_previous_item(
                item, online_root_ids=online_root_ids, current=current
            )
            classified[classification].append(key)

    # NEW items: current files whose identity is not present in the previous
    # catalog (only counting online roots; a root that disappeared cannot be
    # scanned, so its files are not classified here).
    seen_previous = set(previous_items.keys()) if isinstance(previous_items, dict) else set()
    for key in current:
        if key not in seen_previous:
            classified[CLASSIFICATION_NEW].append(key)

    for classification in CLASSIFICATIONS:
        classified[classification].sort()

    return {
        "schema_version": 1,
        "classification": classified,
        "counters": {c: len(classified[c]) for c in CLASSIFICATIONS},
        "total_previous": len(previous_items) if isinstance(previous_items, dict) else 0,
        "total_current_online": len(current),
    }
