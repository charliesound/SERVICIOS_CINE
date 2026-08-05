from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures/local_media_agent/historical_contracts"
)


def load_manifest(commit_sha: str) -> dict[str, object]:
    manifest_path = FIXTURE_ROOT / commit_sha / "manifest.json"
    assert manifest_path.exists(), f"missing historical manifest: {manifest_path}"
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def snapshot_pyproject_bytes(commit_sha: str) -> bytes:
    snapshot_path = FIXTURE_ROOT / commit_sha / "pyproject.toml"
    assert snapshot_path.exists(), f"missing historical pyproject snapshot: {snapshot_path}"
    return snapshot_path.read_bytes()


def snapshot_pyproject_text(commit_sha: str) -> str:
    return snapshot_pyproject_bytes(commit_sha).decode(encoding="utf-8")


def snapshot_pyproject(commit_sha: str) -> dict:
    return tomllib.loads(snapshot_pyproject_text(commit_sha))


def snapshot_sha256(commit_sha: str) -> str:
    return hashlib.sha256(snapshot_pyproject_bytes(commit_sha)).hexdigest()


def assert_snapshot_integrity(commit_sha: str) -> None:
    manifest = load_manifest(commit_sha)
    assert manifest["source_commit"] == commit_sha
    if manifest.get("source_path") == "pyproject.toml":
        expected_sha = manifest["snapshot_sha256"]
        assert expected_sha is not None
        assert snapshot_sha256(commit_sha) == expected_sha
    assert isinstance(manifest["expected_present_paths"], list)
    assert isinstance(manifest["expected_absent_paths"], list)


def expected_absent_paths(commit_sha: str) -> list[str]:
    manifest = load_manifest(commit_sha)
    return list(manifest["expected_absent_paths"])
