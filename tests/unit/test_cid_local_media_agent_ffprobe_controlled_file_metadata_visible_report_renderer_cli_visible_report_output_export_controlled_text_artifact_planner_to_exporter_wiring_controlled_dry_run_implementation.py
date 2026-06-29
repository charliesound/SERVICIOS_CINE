from hashlib import sha256
from pathlib import Path

import pytest

from scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run import (
    CONTROLLED_VISIBLE_REPORT_SUFFIX,
    ControlledTextArtifactPlannerToExporterDryRunError,
    plan_controlled_text_artifact_exporter_dry_run_from_planner_result,
)


ROOT = Path(__file__).resolve().parents[2]

MODULE_PATH = ROOT / (
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_planner_to_exporter_dry_run.py"
)

THIS_TEST_PATH = ROOT / (
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_"
    "controlled_text_artifact_planner_to_exporter_wiring_controlled_dry_run_implementation.py"
)


def _hash_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _valid_visible_report_text() -> str:
    return "CONTROLLED VISIBLE REPORT\n\nClip count: 1\nDry-run only.\n"


def _valid_planner_result() -> dict:
    text = _valid_visible_report_text()
    return {
        "controlled_export_root": "/controlled_exports",
        "suggested_filename": f"visible_report{CONTROLLED_VISIBLE_REPORT_SUFFIX}",
        "planned_artifact_path": (
            "/controlled_exports/visible_report.controlled_visible_report.txt"
        ),
        "artifact_format": "controlled_visible_report_text",
        "content_sha256": _hash_text(text),
        "write_performed": False,
        "artifact_created_on_disk": False,
        "path_boundary": {
            "controlled_export_root_boundary": "CONTROLLED_EXPORT_ROOT_BOUNDARY_OK"
        },
        "safety_flags": {
            "file_write_performed": False,
            "directory_creation_performed": False,
            "artifact_creation_performed": False,
            "media_execution_performed": False,
            "network_access_performed": False,
        },
    }


def test_module_exists() -> None:
    assert MODULE_PATH.is_file()


def test_test_file_exists() -> None:
    assert THIS_TEST_PATH.is_file()


def test_controlled_dry_run_accepts_valid_planner_result() -> None:
    result = plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
        visible_report_text=_valid_visible_report_text(),
        planner_result=_valid_planner_result(),
        caller_context={"phase": "controlled_dry_run", "attempt": 1},
    )

    assert result["exporter_decision"] == "CONTROLLED_DRY_RUN_ACCEPTED"
    assert result["dry_run"] is True
    assert result["write_requested"] is False
    assert result["write_performed"] is False
    assert result["artifact_created_on_disk"] is False
    assert result["planned_artifact_path"].endswith(CONTROLLED_VISIBLE_REPORT_SUFFIX)
    assert result["suggested_filename"].endswith(CONTROLLED_VISIBLE_REPORT_SUFFIX)
    assert result["content_sha256"] == _hash_text(_valid_visible_report_text())
    assert result["caller_context"] == {
        "phase": "controlled_dry_run",
        "attempt": "1",
    }


def test_controlled_dry_run_has_human_visible_summary_without_creation_claim() -> None:
    result = plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
        visible_report_text=_valid_visible_report_text(),
        planner_result=_valid_planner_result(),
    )

    assert "human review" in result["human_visible_summary"]
    assert "No file was written" in result["human_visible_summary"]
    assert "no artifact was created on disk" in result["human_visible_summary"]


@pytest.mark.parametrize(
    "field_name",
    [
        "controlled_export_root",
        "suggested_filename",
        "planned_artifact_path",
        "artifact_format",
        "content_sha256",
        "write_performed",
        "artifact_created_on_disk",
        "path_boundary",
        "safety_flags",
    ],
)
def test_rejects_missing_planner_result_required_fields(field_name: str) -> None:
    planner_result = _valid_planner_result()
    planner_result.pop(field_name)

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="missing required fields",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


@pytest.mark.parametrize(
    "bad_text",
    ["", "   ", "\n\t"],
)
def test_rejects_empty_visible_report_text(bad_text: str) -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="visible_report_text must not be empty",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=bad_text,
            planner_result=_valid_planner_result(),
        )


def test_rejects_non_mapping_planner_result() -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="planner_result must be a mapping",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result="not-a-mapping",
        )


def test_rejects_non_dry_run_mode() -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="Only dry-run mode is supported",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=_valid_planner_result(),
            dry_run=False,
        )


def test_rejects_write_requested_in_controlled_dry_run() -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="write_requested must remain false",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=_valid_planner_result(),
            write_requested=True,
        )


def test_rejects_wrong_suggested_filename_suffix() -> None:
    planner_result = _valid_planner_result()
    planner_result["suggested_filename"] = "visible_report.txt"

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="controlled visible report suffix",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


def test_rejects_planned_artifact_path_missing_suggested_filename() -> None:
    planner_result = _valid_planner_result()
    planner_result["planned_artifact_path"] = "/controlled_exports/other.controlled_visible_report.txt"

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="must include the suggested filename",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


def test_rejects_content_hash_mismatch() -> None:
    planner_result = _valid_planner_result()
    planner_result["content_sha256"] = "0" * 64

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="content hash does not match",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


def test_rejects_planner_result_claiming_prior_write_execution() -> None:
    planner_result = _valid_planner_result()
    planner_result["write_performed"] = True

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="prior write execution",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


def test_rejects_planner_result_claiming_prior_artifact_creation() -> None:
    planner_result = _valid_planner_result()
    planner_result["artifact_created_on_disk"] = True

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="prior artifact creation",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


@pytest.mark.parametrize(
    "bad_boundary",
    [
        {},
        {"controlled_export_root_boundary": False},
        {"controlled_export_root_boundary": "unsafe"},
        "unsafe",
        None,
    ],
)
def test_rejects_unsafe_path_boundary(bad_boundary) -> None:
    planner_result = _valid_planner_result()
    planner_result["path_boundary"] = bad_boundary

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="path_boundary is not accepted as safe",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


@pytest.mark.parametrize(
    "bad_safety_flags",
    [
        {},
        {"file_write_performed": True},
        {"directory_creation_performed": True},
        {"artifact_creation_performed": True},
        None,
    ],
)
def test_rejects_unsafe_safety_flags(bad_safety_flags) -> None:
    planner_result = _valid_planner_result()
    planner_result["safety_flags"] = bad_safety_flags

    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="safety_flags must all be false",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=planner_result,
        )


def test_accepts_string_safe_path_boundary() -> None:
    planner_result = _valid_planner_result()
    planner_result["path_boundary"] = "CONTROLLED_EXPORT_ROOT_BOUNDARY_OK"

    result = plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
        visible_report_text=_valid_visible_report_text(),
        planner_result=planner_result,
    )

    assert result["path_boundary"] == "CONTROLLED_EXPORT_ROOT_BOUNDARY_OK"


def test_rejects_non_scalar_caller_context_values() -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="caller_context values must be scalar",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=_valid_planner_result(),
            caller_context={"nested": {"not": "allowed"}},
        )


def test_rejects_empty_caller_context_key() -> None:
    with pytest.raises(
        ControlledTextArtifactPlannerToExporterDryRunError,
        match="caller_context keys must be non-empty strings",
    ):
        plan_controlled_text_artifact_exporter_dry_run_from_planner_result(
            visible_report_text=_valid_visible_report_text(),
            planner_result=_valid_planner_result(),
            caller_context={"": "bad"},
        )


def test_source_contains_no_disk_creation_or_write_calls() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    forbidden_markers = [
        ".write_text(",
        ".write_bytes(",
        ".mkdir(",
        ".touch(",
        "Path(",
    ]

    for marker in forbidden_markers:
        assert marker not in source


def test_source_contains_no_media_execution_or_network_runtime_imports() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    forbidden_markers = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "Popen",
        "import " + "socket",
        "import " + "http",
        "requests",
    ]

    for marker in forbidden_markers:
        assert marker not in source


def test_source_does_not_import_existing_planner_or_exporter_runtime() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")

    forbidden_markers = [
        "from scripts" + ".local_media_agent",
        "import scripts" + ".local_media_agent",
    ]

    for marker in forbidden_markers:
        assert marker not in source
