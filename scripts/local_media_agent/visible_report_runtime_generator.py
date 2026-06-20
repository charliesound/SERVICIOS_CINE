from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
import re
from typing import Any


OUTPUT_FILENAME = "cid_local_media_agent_visible_report_v1.md"
REPORT_FAMILY = "05_reports"

_REQUIRED_GROUPS = (
    "report_identity",
    "privacy_evidence",
    "scanner_summary",
    "accepted_media",
    "rejected_non_media",
    "human_review",
    "warnings",
    "created_output_artifacts",
    "roadmap_modules_not_generated",
)

_EXPECTED_SCANNER_FACTS = {
    "status": "completed_with_warnings",
    "candidate_media_count": 5,
    "accepted_media_count": 4,
    "rejected_non_media_count": 3,
    "human_review_required_count": 1,
    "warnings_count": 1,
    "ffprobe_preflight": "skipped",
}

_REQUIRED_PRIVACY_FALSE_FLAGS = (
    "original_media_left_client_system",
    "saas_upload_performed",
    "network_call_performed",
    "database_write_performed",
)

_FORBIDDEN_OUTPUT_FAMILIES = {
    "00_project",
    "01_media_catalog",
    "02_audio_sync",
    "03_transcription",
    "04_subtitles",
    "06_exports",
}

_FORBIDDEN_TEXT_MARKERS = (
    "/mnt/",
    "DESKTOP-",
    "harliesound",
    "SERVICIOS_CINE",
    "file://",
)

_REQUIRED_ROADMAP_NOT_GENERATED = (
    "audio_sync",
    "transcription",
    "subtitles",
    "timeline_exports",
    "saas_upload",
    "database_records",
)

_SECTION_ORDER = (
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
)


class VisibleReportRuntimeGeneratorError(ValueError):
    """Raised when controlled visible report rendering is not authorized."""


def generate_visible_report(scanner_result: Mapping[str, object], output_root: Path) -> Path:
    """Render one deterministic local-only visible report from validated scanner facts.

    This function is intentionally narrow. It does not scan, probe, sync, transcribe,
    subtitle, export, upload, call network services, or write to a database.
    """

    data = _validate_scanner_result(scanner_result)
    report_path = _validate_output_root(output_root)

    markdown = _render_markdown(data)
    _ensure_no_unsafe_text(markdown, "rendered visible report")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(markdown, encoding="utf-8")
    return report_path


def _validate_scanner_result(scanner_result: Mapping[str, object]) -> Mapping[str, object]:
    # 1. input object type
    if not isinstance(scanner_result, Mapping):
        raise VisibleReportRuntimeGeneratorError("scanner_result must be a mapping.")

    # 2. required top-level groups
    missing = [group for group in _REQUIRED_GROUPS if group not in scanner_result]
    if missing:
        joined = ", ".join(missing)
        raise VisibleReportRuntimeGeneratorError(f"Missing required input groups: {joined}")

    data = scanner_result

    # 3. report identity values
    _validate_report_identity(_required_mapping(data["report_identity"], "report_identity"))

    # 4. local-only privacy evidence
    _validate_privacy_evidence(_required_mapping(data["privacy_evidence"], "privacy_evidence"))

    # 5. forbidden local-environment markers
    _ensure_no_unsafe_text(data, "scanner_result")

    # 6. scanner fact completeness
    scanner_summary = _required_mapping(data["scanner_summary"], "scanner_summary")
    _validate_scanner_summary(scanner_summary)

    # 7. accepted and rejected media count consistency
    accepted_media = _required_mapping_list(data["accepted_media"], "accepted_media")
    rejected_non_media = _required_mapping_list(data["rejected_non_media"], "rejected_non_media")
    human_review = _required_mapping_list(data["human_review"], "human_review")
    warnings = _required_mapping_list(data["warnings"], "warnings")
    _validate_count_consistency(scanner_summary, accepted_media, rejected_non_media, human_review, warnings)

    # 8. human review and warning visibility
    _validate_required_item_keys(accepted_media, "accepted_media", ("clip_id", "media_type", "review_status"))
    _validate_required_item_keys(rejected_non_media, "rejected_non_media", ("item_id", "reason"))
    _validate_required_item_keys(human_review, "human_review", ("clip_id", "reason"))
    _validate_required_item_keys(warnings, "warnings", ("warning_id", "message"))

    # 9. current-output versus roadmap-output separation
    _validate_created_output_artifacts(
        _required_mapping(data["created_output_artifacts"], "created_output_artifacts")
    )
    _validate_roadmap_modules(
        _required_mapping(data["roadmap_modules_not_generated"], "roadmap_modules_not_generated")
    )

    # 10. deterministic rendering safety
    _validate_no_volatile_identity(_required_mapping(data["report_identity"], "report_identity"))

    return data


def _validate_report_identity(report_identity: Mapping[str, object]) -> None:
    expected = {
        "report_family": REPORT_FAMILY,
        "report_filename": OUTPUT_FILENAME,
        "audience": "internal_demo_only",
        "generator_module": "visible_report_runtime_generator",
    }
    for key, expected_value in expected.items():
        if report_identity.get(key) != expected_value:
            raise VisibleReportRuntimeGeneratorError(
                f"Invalid report_identity.{key}: expected {expected_value!r}."
            )


def _validate_privacy_evidence(privacy_evidence: Mapping[str, object]) -> None:
    for key in _REQUIRED_PRIVACY_FALSE_FLAGS:
        if privacy_evidence.get(key) is not False:
            raise VisibleReportRuntimeGeneratorError(
                f"Privacy evidence must prove {key} is false."
            )


def _validate_scanner_summary(scanner_summary: Mapping[str, object]) -> None:
    for key, expected_value in _EXPECTED_SCANNER_FACTS.items():
        if key not in scanner_summary:
            raise VisibleReportRuntimeGeneratorError(f"Missing scanner_summary.{key}.")
        actual = scanner_summary[key]
        if isinstance(expected_value, int):
            if not isinstance(actual, int) or isinstance(actual, bool):
                raise VisibleReportRuntimeGeneratorError(f"scanner_summary.{key} must be an integer.")
        if actual != expected_value:
            raise VisibleReportRuntimeGeneratorError(
                f"Invalid scanner_summary.{key}: expected {expected_value!r}, got {actual!r}."
            )


def _validate_count_consistency(
    scanner_summary: Mapping[str, object],
    accepted_media: Sequence[Mapping[str, object]],
    rejected_non_media: Sequence[Mapping[str, object]],
    human_review: Sequence[Mapping[str, object]],
    warnings: Sequence[Mapping[str, object]],
) -> None:
    accepted_count = _expected_int(scanner_summary, "accepted_media_count")
    rejected_count = _expected_int(scanner_summary, "rejected_non_media_count")
    human_review_count = _expected_int(scanner_summary, "human_review_required_count")
    warnings_count = _expected_int(scanner_summary, "warnings_count")
    candidate_count = _expected_int(scanner_summary, "candidate_media_count")

    if len(accepted_media) != accepted_count:
        raise VisibleReportRuntimeGeneratorError("Accepted media count is inconsistent.")
    if len(rejected_non_media) != rejected_count:
        raise VisibleReportRuntimeGeneratorError("Rejected non-media count is inconsistent.")
    if len(human_review) != human_review_count:
        raise VisibleReportRuntimeGeneratorError("Human review count is inconsistent.")
    if len(warnings) != warnings_count:
        raise VisibleReportRuntimeGeneratorError("Warnings count is inconsistent.")
    if len(accepted_media) + len(human_review) != candidate_count:
        raise VisibleReportRuntimeGeneratorError("Candidate media count is inconsistent.")


def _validate_required_item_keys(
    items: Sequence[Mapping[str, object]],
    group_name: str,
    required_keys: Sequence[str],
) -> None:
    for index, item in enumerate(items, start=1):
        for key in required_keys:
            value = item.get(key)
            if not isinstance(value, str) or not value.strip():
                raise VisibleReportRuntimeGeneratorError(
                    f"{group_name}[{index}].{key} must be a non-empty string."
                )


def _validate_created_output_artifacts(created_output_artifacts: Mapping[str, object]) -> None:
    if created_output_artifacts.get("allowed_report_family") != REPORT_FAMILY:
        raise VisibleReportRuntimeGeneratorError("created_output_artifacts must authorize only 05_reports.")
    if created_output_artifacts.get("report_filename") != OUTPUT_FILENAME:
        raise VisibleReportRuntimeGeneratorError("created_output_artifacts report filename is not authorized.")

    pre_existing = created_output_artifacts.get("existing_runtime_artifacts_before_render")
    if not isinstance(pre_existing, Sequence) or isinstance(pre_existing, (str, bytes)):
        raise VisibleReportRuntimeGeneratorError(
            "created_output_artifacts.existing_runtime_artifacts_before_render must be a list."
        )

    for text in _iter_text(created_output_artifacts):
        stripped = text.strip().strip("/\\")
        first_part = re.split(r"[/\\]", stripped)[0]
        if first_part in _FORBIDDEN_OUTPUT_FAMILIES:
            raise VisibleReportRuntimeGeneratorError(
                f"Forbidden output family in created_output_artifacts: {first_part}"
            )


def _validate_roadmap_modules(roadmap_modules: Mapping[str, object]) -> None:
    for key in _REQUIRED_ROADMAP_NOT_GENERATED:
        if roadmap_modules.get(key) != "not_generated":
            raise VisibleReportRuntimeGeneratorError(
                f"roadmap_modules_not_generated.{key} must be not_generated."
            )


def _validate_no_volatile_identity(report_identity: Mapping[str, object]) -> None:
    volatile_keys = {"created_at", "updated_at", "timestamp", "machine", "hostname", "user", "absolute_path"}
    present = sorted(volatile_keys.intersection(report_identity.keys()))
    if present:
        joined = ", ".join(present)
        raise VisibleReportRuntimeGeneratorError(f"Volatile report identity fields are not allowed: {joined}")


def _validate_output_root(output_root: Path) -> Path:
    # 11. final output path authorization
    if not isinstance(output_root, Path):
        raise VisibleReportRuntimeGeneratorError("output_root must be a pathlib.Path.")

    raw_output_root = str(output_root)
    normalized_raw_output_root = raw_output_root.replace("\\\\", "/")

    if raw_output_root.strip().startswith("\\\\"):
        raise VisibleReportRuntimeGeneratorError("UNC output path is not allowed.")
    if re.search(r"\b[A-Za-z]:[\\/]", raw_output_root.strip()):
        raise VisibleReportRuntimeGeneratorError("Windows drive output path is not allowed.")
    if "/mnt/" in normalized_raw_output_root:
        raise VisibleReportRuntimeGeneratorError("Mounted Windows output path is not allowed.")

    resolved_root = output_root.expanduser().resolve()

    if resolved_root == Path(resolved_root.anchor):
        raise VisibleReportRuntimeGeneratorError("Refusing to write to filesystem root.")

    if any(part in _FORBIDDEN_OUTPUT_FAMILIES for part in resolved_root.parts):
        raise VisibleReportRuntimeGeneratorError("Refusing to write inside a protected project output family.")

    repo_root = Path.cwd().resolve()
    try:
        resolved_root.relative_to(repo_root)
    except ValueError:
        pass
    else:
        raise VisibleReportRuntimeGeneratorError("Refusing to write inside the repository.")

    report_path = resolved_root / REPORT_FAMILY / OUTPUT_FILENAME
    relative_parts = report_path.relative_to(resolved_root).parts

    if relative_parts != (REPORT_FAMILY, OUTPUT_FILENAME):
        raise VisibleReportRuntimeGeneratorError("Final output path is not authorized.")

    return report_path


def _render_markdown(data: Mapping[str, object]) -> str:
    scanner_summary = _required_mapping(data["scanner_summary"], "scanner_summary")
    privacy_evidence = _required_mapping(data["privacy_evidence"], "privacy_evidence")
    accepted_media = _required_mapping_list(data["accepted_media"], "accepted_media")
    rejected_non_media = _required_mapping_list(data["rejected_non_media"], "rejected_non_media")
    human_review = _required_mapping_list(data["human_review"], "human_review")
    warnings = _required_mapping_list(data["warnings"], "warnings")
    roadmap_modules = _required_mapping(data["roadmap_modules_not_generated"], "roadmap_modules_not_generated")

    lines: list[str] = [
        "# CID Local Media Agent - Controlled Visible Report",
        "",
        "Internal demo only. This report renders already-controlled scanner facts.",
        "",
    ]

    _append_section(lines, "Executive Summary", [
        "The controlled scanner result is completed_with_warnings.",
        "This generated artifact is a producer-readable local report only.",
        "No editorial deliverables are generated by this renderer.",
    ])

    _append_section(lines, "Local-Only Privacy Confirmation", [
        f"original media left client system: {_bool_text(privacy_evidence['original_media_left_client_system'])}",
        f"SaaS upload performed: {_bool_text(privacy_evidence['saas_upload_performed'])}",
        f"network call performed: {_bool_text(privacy_evidence['network_call_performed'])}",
        f"database write performed: {_bool_text(privacy_evidence['database_write_performed'])}",
    ])

    _append_section(lines, "Controlled Demo Input Summary", [
        "Input source: already-created controlled scanner result data.",
        "Scanner execution by this renderer: false.",
        "Media probing by this renderer: false.",
        "Client-facing readiness: false.",
    ])

    _append_section(lines, "Scanner Result Summary", [
        f"Scanner status: {scanner_summary['status']}",
        f"Candidate media count: {scanner_summary['candidate_media_count']}",
        f"Accepted media count: {scanner_summary['accepted_media_count']}",
        f"Rejected non-media count: {scanner_summary['rejected_non_media_count']}",
        f"Human review required count: {scanner_summary['human_review_required_count']}",
        f"Warnings count: {scanner_summary['warnings_count']}",
        f"ffprobe preflight: {scanner_summary['ffprobe_preflight']}",
    ])

    _append_section(lines, "Accepted Media", _media_lines(accepted_media))
    _append_section(lines, "Rejected Non-Media", _rejected_lines(rejected_non_media))
    _append_section(lines, "Human Review Required", _human_review_lines(human_review))
    _append_section(lines, "Warnings", _warning_lines(warnings))

    _append_section(lines, "Created Output Artifacts", [
        f"{REPORT_FAMILY}/{OUTPUT_FILENAME}",
        "No other output family is created by this renderer.",
    ])

    _append_section(lines, "Roadmap Modules Not Yet Generated", [
        f"audio sync: {roadmap_modules['audio_sync']}",
        f"transcription: {roadmap_modules['transcription']}",
        f"subtitles: {roadmap_modules['subtitles']}",
        f"timeline exports: {roadmap_modules['timeline_exports']}",
        f"SaaS upload: {roadmap_modules['saas_upload']}",
        f"database records: {roadmap_modules['database_records']}",
    ])

    _append_section(lines, "Producer Interpretation", [
        "The folder can be discussed as a controlled local media preflight demo.",
        "One warning and one human-review item remain visible and unresolved.",
        "The report must not be presented as sync, transcription, subtitle, or export output.",
    ])

    _append_section(lines, "Next Technical Actions", [
        "Validate this renderer through the controlled unit test only.",
        "Keep scanner execution and media probing in separate future phases.",
        "Keep client-facing demo authorization blocked until a later explicit gate.",
    ])

    _ensure_sections_in_order("\n".join(lines))
    return "\n".join(lines).rstrip() + "\n"


def _append_section(lines: list[str], title: str, body_lines: Sequence[str]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    for line in body_lines:
        lines.append(f"- {line}")
    lines.append("")


def _media_lines(items: Sequence[Mapping[str, object]]) -> list[str]:
    return [
        f"{item['clip_id']} — {item['media_type']} — {item['review_status']}"
        for item in sorted(items, key=lambda value: str(value["clip_id"]))
    ]


def _rejected_lines(items: Sequence[Mapping[str, object]]) -> list[str]:
    return [
        f"{item['item_id']} — {item['reason']}"
        for item in sorted(items, key=lambda value: str(value["item_id"]))
    ]


def _human_review_lines(items: Sequence[Mapping[str, object]]) -> list[str]:
    return [
        f"{item['clip_id']} — {item['reason']}"
        for item in sorted(items, key=lambda value: str(value["clip_id"]))
    ]


def _warning_lines(items: Sequence[Mapping[str, object]]) -> list[str]:
    return [
        f"{item['warning_id']} — {item['message']}"
        for item in sorted(items, key=lambda value: str(value["warning_id"]))
    ]


def _ensure_sections_in_order(markdown: str) -> None:
    cursor = -1
    for section in _SECTION_ORDER:
        marker = f"## {section}"
        position = markdown.find(marker)
        if position <= cursor:
            raise VisibleReportRuntimeGeneratorError(f"Missing or out-of-order section: {section}")
        cursor = position


def _required_mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise VisibleReportRuntimeGeneratorError(f"{name} must be a mapping.")
    return value


def _required_mapping_list(value: object, name: str) -> Sequence[Mapping[str, object]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise VisibleReportRuntimeGeneratorError(f"{name} must be a list.")
    for index, item in enumerate(value, start=1):
        if not isinstance(item, Mapping):
            raise VisibleReportRuntimeGeneratorError(f"{name}[{index}] must be a mapping.")
    return value


def _expected_int(mapping: Mapping[str, object], key: str) -> int:
    value = mapping[key]
    if not isinstance(value, int) or isinstance(value, bool):
        raise VisibleReportRuntimeGeneratorError(f"{key} must be an integer.")
    return value


def _bool_text(value: object) -> str:
    if value is False:
        return "false"
    if value is True:
        return "true"
    raise VisibleReportRuntimeGeneratorError("Privacy values must be booleans.")


def _ensure_no_unsafe_text(value: object, context: str) -> None:
    for text in _iter_text(value):
        _ensure_safe_path_text(text, context)


def _ensure_safe_path_text(text: str, context: str) -> None:
    for marker in _FORBIDDEN_TEXT_MARKERS:
        if marker in text:
            raise VisibleReportRuntimeGeneratorError(f"Unsafe marker in {context}: {marker}")

    stripped = text.strip()
    if stripped.startswith("\\\\"):
        raise VisibleReportRuntimeGeneratorError(f"UNC path is not allowed in {context}.")
    if re.search(r"\b[A-Za-z]:[\\/]", stripped):
        raise VisibleReportRuntimeGeneratorError(f"Windows drive path is not allowed in {context}.")
    if stripped.startswith("/"):
        raise VisibleReportRuntimeGeneratorError(f"Absolute system path is not allowed in {context}.")


def _iter_text(value: object) -> list[str]:
    found: list[str] = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, Mapping):
        for key, item in value.items():
            found.extend(_iter_text(key))
            found.extend(_iter_text(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            found.extend(_iter_text(item))
    return found
