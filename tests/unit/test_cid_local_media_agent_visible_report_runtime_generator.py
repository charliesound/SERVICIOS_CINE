from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "local_media_agent" / "visible_report_runtime_generator.py"
OUTPUT_FILENAME = "cid_local_media_agent_visible_report_v1.md"


def _load_module():
    spec = importlib.util.spec_from_file_location("visible_report_runtime_generator_under_test", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _valid_scanner_result() -> dict[str, object]:
    return {
        "report_identity": {
            "report_family": "05_reports",
            "report_filename": OUTPUT_FILENAME,
            "audience": "internal_demo_only",
            "generator_module": "visible_report_runtime_generator",
        },
        "privacy_evidence": {
            "original_media_left_client_system": False,
            "saas_upload_performed": False,
            "network_call_performed": False,
            "database_write_performed": False,
        },
        "scanner_summary": {
            "status": "completed_with_warnings",
            "candidate_media_count": 5,
            "accepted_media_count": 4,
            "rejected_non_media_count": 3,
            "human_review_required_count": 1,
            "warnings_count": 1,
            "ffprobe_preflight": "skipped",
        },
        "accepted_media": [
            {"clip_id": "CONTROLLED_MEDIA_003", "media_type": "audio", "review_status": "accepted"},
            {"clip_id": "CONTROLLED_MEDIA_001", "media_type": "video", "review_status": "accepted"},
            {"clip_id": "CONTROLLED_MEDIA_004", "media_type": "video", "review_status": "accepted"},
            {"clip_id": "CONTROLLED_MEDIA_002", "media_type": "video", "review_status": "accepted"},
        ],
        "rejected_non_media": [
            {"item_id": "CONTROLLED_NON_MEDIA_003", "reason": "unsupported_control_file"},
            {"item_id": "CONTROLLED_NON_MEDIA_001", "reason": "text_document"},
            {"item_id": "CONTROLLED_NON_MEDIA_002", "reason": "still_image"},
        ],
        "human_review": [
            {"clip_id": "CONTROLLED_MEDIA_005", "reason": "requires_manual_classification"},
        ],
        "warnings": [
            {"warning_id": "CONTROLLED_WARNING_001", "message": "one_candidate_requires_human_review"},
        ],
        "created_output_artifacts": {
            "allowed_report_family": "05_reports",
            "report_filename": OUTPUT_FILENAME,
            "existing_runtime_artifacts_before_render": [],
        },
        "roadmap_modules_not_generated": {
            "audio_sync": "not_generated",
            "transcription": "not_generated",
            "subtitles": "not_generated",
            "timeline_exports": "not_generated",
            "saas_upload": "not_generated",
            "database_records": "not_generated",
        },
    }


def test_generate_visible_report_creates_one_authorized_local_artifact(tmp_path: Path) -> None:
    module = _load_module()

    report_path = module.generate_visible_report(_valid_scanner_result(), tmp_path)

    assert report_path == tmp_path / "05_reports" / OUTPUT_FILENAME
    assert report_path.exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == ["05_reports"]
    assert sorted(path.name for path in (tmp_path / "05_reports").iterdir()) == [OUTPUT_FILENAME]


def test_report_sections_are_preserved_in_required_order(tmp_path: Path) -> None:
    module = _load_module()

    report_path = module.generate_visible_report(_valid_scanner_result(), tmp_path)
    text = report_path.read_text(encoding="utf-8")

    sections = [
        "Executive Summary",
        "Local-Only Privacy Confirmation",
        "Controlled Demo Input Summary",
        "Scanner Result Summary",
        "Accepted Media",
        "Rejected Non-Media",
        "Human Review Required",
        "Warnings",
        "Created Output Artifacts",
        "Roadmap Modules Not Yet Generated",
        "Producer Interpretation",
        "Next Technical Actions",
    ]

    cursor = -1
    for section in sections:
        position = text.index(f"## {section}")
        assert position > cursor
        cursor = position


def test_report_preserves_privacy_warnings_and_truthful_roadmap_boundaries(tmp_path: Path) -> None:
    module = _load_module()

    report_path = module.generate_visible_report(_valid_scanner_result(), tmp_path)
    text = report_path.read_text(encoding="utf-8")

    assert "original media left client system: false" in text
    assert "SaaS upload performed: false" in text
    assert "network call performed: false" in text
    assert "database write performed: false" in text
    assert "Warnings count: 1" in text
    assert "CONTROLLED_WARNING_001" in text
    assert "audio sync: not_generated" in text
    assert "transcription: not_generated" in text
    assert "subtitles: not_generated" in text
    assert "timeline exports: not_generated" in text
    assert "The report must not be presented as sync, transcription, subtitle, or export output." in text


def test_generation_is_deterministic_for_same_controlled_input(tmp_path: Path) -> None:
    module = _load_module()

    result_a = module.generate_visible_report(_valid_scanner_result(), tmp_path / "a")
    result_b = module.generate_visible_report(_valid_scanner_result(), tmp_path / "b")

    assert result_a.read_text(encoding="utf-8") == result_b.read_text(encoding="utf-8")


def test_missing_required_group_fails_closed_without_output(tmp_path: Path) -> None:
    module = _load_module()
    scanner_result = _valid_scanner_result()
    scanner_result.pop("warnings")

    with pytest.raises(module.VisibleReportRuntimeGeneratorError):
        module.generate_visible_report(scanner_result, tmp_path)

    assert not (tmp_path / "05_reports").exists()


def test_inconsistent_counts_fail_closed_without_output(tmp_path: Path) -> None:
    module = _load_module()
    scanner_result = _valid_scanner_result()
    scanner_result["accepted_media"] = scanner_result["accepted_media"][:-1]

    with pytest.raises(module.VisibleReportRuntimeGeneratorError):
        module.generate_visible_report(scanner_result, tmp_path)

    assert not (tmp_path / "05_reports").exists()


def test_privacy_violation_fails_closed_without_output(tmp_path: Path) -> None:
    module = _load_module()
    scanner_result = _valid_scanner_result()
    scanner_result["privacy_evidence"]["network_call_performed"] = True

    with pytest.raises(module.VisibleReportRuntimeGeneratorError):
        module.generate_visible_report(scanner_result, tmp_path)

    assert not (tmp_path / "05_reports").exists()


def test_unsafe_local_marker_fails_closed_without_output(tmp_path: Path) -> None:
    module = _load_module()
    scanner_result = _valid_scanner_result()
    scanner_result["accepted_media"][0]["clip_id"] = "/mnt/c/private_real_shoot.mov"

    with pytest.raises(module.VisibleReportRuntimeGeneratorError):
        module.generate_visible_report(scanner_result, tmp_path)

    assert not (tmp_path / "05_reports").exists()


def test_protected_output_family_fails_closed_without_output(tmp_path: Path) -> None:
    module = _load_module()
    output_root = tmp_path / "02_audio_sync"

    with pytest.raises(module.VisibleReportRuntimeGeneratorError):
        module.generate_visible_report(_valid_scanner_result(), output_root)

    assert not output_root.exists()


def test_source_does_not_import_external_runtime_services() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    forbidden_runtime_imports = [
        "subprocess",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "sqlalchemy",
        "psycopg",
        "sqli" + "te3",
        "fastapi",
    ]

    for forbidden in forbidden_runtime_imports:
        assert forbidden not in source

    assert "generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path" in source
    assert "write_text" in source
    assert "mkdir" in source
