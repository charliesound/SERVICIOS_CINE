"""Tests for the pure CID LMA incremental catalog comparison (Slice A)."""

from __future__ import annotations

from scripts.local_media_agent.catalog_compare import (
    CLASSIFICATION_MISSING,
    CLASSIFICATION_MODIFIED,
    CLASSIFICATION_NEW,
    CLASSIFICATION_OFFLINE,
    CLASSIFICATION_UNCHANGED,
    FINGERPRINT_CONTRACT,
    compare_catalogs,
)


ROOT_ON = "ROOT-on"
ROOT_OFF = "ROOT-off"
PROJECT_ID = "PRJ-11111111-1111-4111-8111-111111111111"


def _catalog(*items):
    return {
        "schema_version": 1,
        "project_id": PROJECT_ID,
        "media_items": {f"{i['source_root_id']}::{i['relative_path']}": i for i in items},
    }


def _item(rel, root=ROOT_ON, size=100, mtime_ns=1000, analysis_status="OK"):
    return {
        "source_root_id": root,
        "relative_path": rel,
        "size": size,
        "mtime_ns": mtime_ns,
        "analysis_status": analysis_status,
        "catalog_status": "PRESENT",
    }


def _snapshot(*files, online=None):
    return {
        "online_root_ids": list(online) if online is not None else [ROOT_ON],
        "files": [
            {
                "source_root_id": f[0],
                "relative_path": f[1],
                "size": f[2],
                "mtime_ns": f[3],
            }
            for f in files
        ],
    }


def _file(root, rel, size=100, mtime_ns=1000):
    return (root, rel, size, mtime_ns)


def test_new_item_classified_new() -> None:
    catalog = _catalog(_item("a.MP4"))
    snapshot = _snapshot(_file(ROOT_ON, "b.MP4"), _file(ROOT_ON, "a.MP4"))
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_NEW] == ["ROOT-on::b.MP4"]


def test_unchanged_classified_unchanged() -> None:
    catalog = _catalog(_item("a.MP4"))
    snapshot = _snapshot(_file(ROOT_ON, "a.MP4"))
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_UNCHANGED] == ["ROOT-on::a.MP4"]


def test_size_changed_classified_modified() -> None:
    catalog = _catalog(_item("a.MP4", size=100))
    snapshot = _snapshot(_file(ROOT_ON, "a.MP4", size=150))
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_MODIFIED] == ["ROOT-on::a.MP4"]


def test_mtime_changed_classified_modified() -> None:
    catalog = _catalog(_item("a.MP4", mtime_ns=1000))
    snapshot = _snapshot(_file(ROOT_ON, "a.MP4", mtime_ns=2000))
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_MODIFIED] == ["ROOT-on::a.MP4"]


def test_absent_online_item_classified_missing() -> None:
    catalog = _catalog(_item("a.MP4"), _item("b.MP4"))
    snapshot = _snapshot(_file(ROOT_ON, "a.MP4"))
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_MISSING] == ["ROOT-on::b.MP4"]


def test_offline_root_classified_offline_not_missing() -> None:
    catalog = _catalog(_item("a.MP4", root=ROOT_OFF))
    # root disappears entirely; only ROOT_ON is online
    snapshot = _snapshot(online=[ROOT_ON])
    result = compare_catalogs(catalog, snapshot)
    assert result["classification"][CLASSIFICATION_OFFLINE] == ["ROOT-off::a.MP4"]
    assert result["classification"][CLASSIFICATION_MISSING] == []


def test_deterministic_ordering() -> None:
    catalog = _catalog(_item("z.MP4"), _item("a.MP4"))
    snapshot = _snapshot(_file(ROOT_ON, "z.MP4"), _file(ROOT_ON, "a.MP4"))
    r1 = compare_catalogs(catalog, snapshot)
    r2 = compare_catalogs(catalog, snapshot)
    assert r1 == r2
    for key in ("NEW", "UNCHANGED", "MODIFIED", "MISSING", "OFFLINE"):
        assert r1["classification"][key] == sorted(r1["classification"][key])


def test_cheap_fingerprint_contract() -> None:
    assert FINGERPRINT_CONTRACT == "size+mtime_ns"


def test_counter_totals() -> None:
    catalog = _catalog(_item("a.MP4"), _item("b.MP4"))
    snapshot = _snapshot(_file(ROOT_ON, "a.MP4"), _file(ROOT_ON, "c.MP4"))
    result = compare_catalogs(catalog, snapshot)
    counters = result["counters"]
    assert counters["UNCHANGED"] == 1
    assert counters["MISSING"] == 1
    assert counters["NEW"] == 1
    assert counters["MODIFIED"] == 0
    assert counters["OFFLINE"] == 0
