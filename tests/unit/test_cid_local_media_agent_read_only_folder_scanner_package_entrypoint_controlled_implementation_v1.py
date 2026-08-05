from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path

from _cid_historical_contract_snapshot import snapshot_pyproject


REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
SCANNER_RUNTIME_PATH = REPO_ROOT / "scripts/local_media_agent/read_only_folder_scanner.py"
SCANNER_CLI_PATH = REPO_ROOT / "scripts/local_media_agent/read_only_folder_scanner_cli.py"

EXPECTED_SCRIPT_ENTRY_COUNT = 3

EXPECTED_SCRIPT_ENTRIES = {
    "cid-local-media-agent-visible-report-write-enabled-export": "scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main",
    "cid-local-media-agent-controlled-local-demo-runner": "scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main",
    "cid-local-media-agent-read-only-folder-scanner": "scripts.local_media_agent.read_only_folder_scanner_cli:main",
}

EXPECTED_SCANNER_RUNTIME_SHA256 = "16a4fc52f3fa57b6469bb36ed30400ec26468a9435aad244582a0892fa810a05"
EXPECTED_SCANNER_CLI_SHA256 = "ec9f4714597cd96d2f79640bff51110844bcb4c9106a07e58359e286a99cff6d"

PACKAGE_ENTRYPOINT_SOURCE_COMMIT = "46602631609558ba81eb7f00a1c0c15a435e17b2"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT_PATH.read_text(encoding="utf-8"))


def _sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_project_scripts_section_contains_exactly_three_entries() -> None:
    scripts = snapshot_pyproject(PACKAGE_ENTRYPOINT_SOURCE_COMMIT)["project"]["scripts"]

    assert isinstance(scripts, dict)
    assert len(scripts) == EXPECTED_SCRIPT_ENTRY_COUNT


def test_preexisting_entry_mappings_remain_exact() -> None:
    scripts = _load_pyproject()["project"]["scripts"]

    assert scripts["cid-local-media-agent-visible-report-write-enabled-export"] == EXPECTED_SCRIPT_ENTRIES[
        "cid-local-media-agent-visible-report-write-enabled-export"
    ]
    assert scripts["cid-local-media-agent-controlled-local-demo-runner"] == EXPECTED_SCRIPT_ENTRIES[
        "cid-local-media-agent-controlled-local-demo-runner"
    ]


def test_new_read_only_folder_scanner_entry_mapping_is_exact() -> None:
    scripts = _load_pyproject()["project"]["scripts"]

    assert scripts["cid-local-media-agent-read-only-folder-scanner"] == EXPECTED_SCRIPT_ENTRIES[
        "cid-local-media-agent-read-only-folder-scanner"
    ]


def test_project_scripts_entries_match_expected_exact_mapping() -> None:
    assert snapshot_pyproject(PACKAGE_ENTRYPOINT_SOURCE_COMMIT)["project"]["scripts"] == EXPECTED_SCRIPT_ENTRIES


def test_frozen_scanner_runtime_retains_exact_sha256() -> None:
    assert _sha256_of(SCANNER_RUNTIME_PATH) == EXPECTED_SCANNER_RUNTIME_SHA256


def test_frozen_scanner_cli_retains_exact_sha256() -> None:
    assert _sha256_of(SCANNER_CLI_PATH) == EXPECTED_SCANNER_CLI_SHA256
