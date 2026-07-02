"""Pure local gate generator for CID Local Media Agent.

This module is intentionally deterministic and non-writing. It returns strings
and structured plans only. It does not write files, execute commands, inspect
media, or couple to SaaS/runtime infrastructure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


GATE_GENERATOR_RECORD_ID = "gate_generator_001"
GATE_GENERATOR_HANDLE = "LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001"


@dataclass(frozen=True)
class GateDefinition:
    """Input definition for a controlled CID Local Media Agent gate."""

    phase_identifier: str
    phase_slug: str
    title: str
    expected_closure_result: str
    starting_state: str
    target_next_state: str
    gate_purpose: str
    doc_artifact_path: str
    test_artifact_path: str
    created_artifacts: tuple[str, ...]
    required_checks: tuple[str, ...]
    forbidden_changes: tuple[str, ...]


@dataclass(frozen=True)
class GateArtifactPlan:
    """Generated text artifacts for a controlled gate."""

    phase_identifier: str
    phase_slug: str
    doc_artifact_path: str
    test_artifact_path: str
    document_text: str
    test_stub_text: str
    validation_plan: Mapping[str, tuple[str, ...]]


def _bullet_lines(items: Sequence[str]) -> str:
    return "\n".join(f"{index}. {item}" for index, item in enumerate(items, start=1))


def build_gate_document(definition: GateDefinition) -> str:
    """Build a deterministic Markdown gate document as text."""

    created_artifacts = _bullet_lines(definition.created_artifacts)
    required_checks = _bullet_lines(definition.required_checks)
    forbidden_changes = _bullet_lines(definition.forbidden_changes)

    return "\n".join(
        [
            f"# {definition.title}",
            "",
            "## Phase",
            "",
            f"`{definition.phase_identifier}`",
            "",
            "## Expected closure result",
            "",
            f"`{definition.expected_closure_result}`",
            "",
            "## Starting state",
            "",
            f"`{definition.starting_state}`",
            "",
            "## Target next state",
            "",
            f"`{definition.target_next_state}`",
            "",
            "## Gate purpose",
            "",
            definition.gate_purpose,
            "",
            "## Created artifacts",
            "",
            created_artifacts,
            "",
            "## Required checks",
            "",
            required_checks,
            "",
            "## Explicitly forbidden changes",
            "",
            forbidden_changes,
            "",
            "## Closure",
            "",
            f"`{definition.expected_closure_result}`",
            "",
            "## Closing state",
            "",
            f"`{definition.target_next_state}`",
            "",
        ]
    )


def build_gate_test_stub(definition: GateDefinition) -> str:
    """Build a deterministic pytest test stub as text."""

    return "\n".join(
        [
            "from pathlib import Path",
            "",
            "",
            "ROOT = Path(__file__).resolve().parents[2]",
            f'DOC = ROOT / "{definition.doc_artifact_path}"',
            f'TEST = ROOT / "{definition.test_artifact_path}"',
            "",
            "",
            "def _doc_text() -> str:",
            '    return DOC.read_text(encoding="utf-8")',
            "",
            "",
            "def test_gate_document_exists():",
            "    assert DOC.exists()",
            "",
            "",
            "def test_phase_identifier_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.phase_identifier}" in text',
            "",
            "",
            "def test_expected_closure_result_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.expected_closure_result}" in text',
            "",
            "",
            "def test_starting_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.starting_state}" in text',
            "",
            "",
            "def test_target_next_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.target_next_state}" in text',
            "",
        ]
    )


def build_validation_plan(definition: GateDefinition) -> Mapping[str, tuple[str, ...]]:
    """Build a structured validation plan for a controlled gate."""

    return {
        "required_checks": definition.required_checks,
        "created_artifacts": definition.created_artifacts,
        "forbidden_changes": definition.forbidden_changes,
    }


def build_gate_artifact_plan(definition: GateDefinition) -> GateArtifactPlan:
    """Build all generated gate artifacts without writing them."""

    return GateArtifactPlan(
        phase_identifier=definition.phase_identifier,
        phase_slug=definition.phase_slug,
        doc_artifact_path=definition.doc_artifact_path,
        test_artifact_path=definition.test_artifact_path,
        document_text=build_gate_document(definition),
        test_stub_text=build_gate_test_stub(definition),
        validation_plan=build_validation_plan(definition),
    )


def describe_gate_generator_boundary() -> Mapping[str, str]:
    """Describe the static safety boundary for this pure generator."""

    return {
        "record_id": GATE_GENERATOR_RECORD_ID,
        "handle": GATE_GENERATOR_HANDLE,
        "filesystem_write": "not_performed",
        "existing_file_modification": "not_performed",
        "command_execution": "not_performed",
        "subprocess_execution": "not_performed",
        "media_access": "not_performed",
        "folder_scan": "not_performed",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
        "database": "not_touched",
        "docker": "not_touched",
        "alembic": "not_touched",
        "stripe": "not_touched",
        "ai_jobs": "not_touched",
        "credits_ledger": "not_touched",
    }


GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID = "gate_generator_rich_template_implementation_001"


@dataclass(frozen=True)
class RichGateDefinition:
    """Input definition for a rich controlled CID Local Media Agent gate."""

    phase_identifier: str
    phase_slug: str
    title: str
    expected_closure_result: str
    starting_state: str
    target_next_state: str
    gate_purpose: str
    source_phase_identifier: str
    source_closure_result: str
    source_state: str
    record_id: str
    record_handle: str
    source_record_id: str
    source_record_handle: str
    doc_artifact_path: str
    test_artifact_path: str
    implementation_artifact_paths: tuple[str, ...]
    created_artifacts: tuple[str, ...]
    required_checks: tuple[str, ...]
    forbidden_changes: tuple[str, ...]
    safety_boundaries: tuple[str, ...]
    positive_assertions: tuple[str, ...]
    closure_criteria: tuple[str, ...]
    recommended_next_phase: str
    commit_message: str
    tag_name: str


@dataclass(frozen=True)
class RichGateArtifactPlan:
    """Generated rich text artifacts for a controlled CID gate."""

    phase_identifier: str
    phase_slug: str
    doc_artifact_path: str
    test_artifact_path: str
    implementation_artifact_paths: tuple[str, ...]
    document_text: str
    test_stub_text: str
    validation_plan: Mapping[str, tuple[str, ...]]


def _rich_record_table(definition: RichGateDefinition) -> str:
    return "\n".join(
        [
            "| Field | Value |",
            "| --- | --- |",
            f"| `RECORD_ID` | `{definition.record_id}` |",
            f"| `RECORD_HANDLE` | `{definition.record_handle}` |",
            f"| `SOURCE_RECORD_ID` | `{definition.source_record_id}` |",
            f"| `SOURCE_RECORD_HANDLE` | `{definition.source_record_handle}` |",
            f"| `PHASE_SLUG` | `{definition.phase_slug}` |",
        ]
    )


def build_rich_gate_document(definition: RichGateDefinition) -> str:
    """Build a deterministic rich Markdown gate document as text."""

    created_artifacts = _bullet_lines(definition.created_artifacts)
    implementation_artifacts = _bullet_lines(definition.implementation_artifact_paths)
    required_checks = _bullet_lines(definition.required_checks)
    forbidden_changes = _bullet_lines(definition.forbidden_changes)
    safety_boundaries = _bullet_lines(definition.safety_boundaries)
    positive_assertions = _bullet_lines(definition.positive_assertions)
    closure_criteria = _bullet_lines(definition.closure_criteria)

    return "\n".join(
        [
            f"# {definition.title}",
            "",
            "## Phase",
            "",
            f"`{definition.phase_identifier}`",
            "",
            "## Expected closure result",
            "",
            f"`{definition.expected_closure_result}`",
            "",
            "## Starting state",
            "",
            f"`{definition.starting_state}`",
            "",
            "## Target next state",
            "",
            f"`{definition.target_next_state}`",
            "",
            "## Gate purpose",
            "",
            definition.gate_purpose,
            "",
            "## Source phase",
            "",
            f"`{definition.source_phase_identifier}`",
            "",
            "## Source result",
            "",
            f"`{definition.source_closure_result}`",
            "",
            "## Source state",
            "",
            f"`{definition.source_state}`",
            "",
            "## Created artifacts",
            "",
            created_artifacts,
            "",
            "## Implementation artifact paths",
            "",
            implementation_artifacts,
            "",
            "## Record table",
            "",
            _rich_record_table(definition),
            "",
            "## Safety boundary",
            "",
            safety_boundaries,
            "",
            "## Positive assertions",
            "",
            positive_assertions,
            "",
            "## Explicitly forbidden changes",
            "",
            forbidden_changes,
            "",
            "## Closure criteria",
            "",
            closure_criteria,
            "",
            "## Required checks before closing",
            "",
            required_checks,
            "",
            "## Closure",
            "",
            f"`{definition.expected_closure_result}`",
            "",
            "## Closing state",
            "",
            f"`{definition.target_next_state}`",
            "",
            "## Recommended next phase",
            "",
            f"`{definition.recommended_next_phase}`",
            "",
            "## Commit message",
            "",
            f"`{definition.commit_message}`",
            "",
            "## Tag name",
            "",
            f"`{definition.tag_name}`",
            "",
        ]
    )


def build_rich_gate_test_stub(definition: RichGateDefinition) -> str:
    """Build a deterministic rich pytest test stub as text."""

    return "\n".join(
        [
            "from pathlib import Path",
            "",
            "",
            "ROOT = Path(__file__).resolve().parents[2]",
            f'DOC = ROOT / "{definition.doc_artifact_path}"',
            f'TEST = ROOT / "{definition.test_artifact_path}"',
            "",
            "",
            "def _doc_text() -> str:",
            '    return DOC.read_text(encoding="utf-8")',
            "",
            "",
            "def test_gate_document_exists():",
            "    assert DOC.exists()",
            "",
            "",
            "def test_phase_identifier_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.phase_identifier}" in text',
            "",
            "",
            "def test_expected_closure_result_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.expected_closure_result}" in text',
            "",
            "",
            "def test_starting_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.starting_state}" in text',
            "",
            "",
            "def test_target_next_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.target_next_state}" in text',
            "",
            "",
            "def test_source_phase_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.source_phase_identifier}" in text',
            "",
            "",
            "def test_source_result_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.source_closure_result}" in text',
            "",
            "",
            "def test_source_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.source_state}" in text',
            "",
            "",
            "def test_record_id_and_handle_are_present():",
            "    text = _doc_text()",
            f'    assert "{definition.record_id}" in text',
            f'    assert "{definition.record_handle}" in text',
            "",
            "",
            "def test_closing_state_is_present():",
            "    text = _doc_text()",
            f'    assert "{definition.target_next_state}" in text',
            "",
        ]
    )


def build_rich_validation_plan(definition: RichGateDefinition) -> Mapping[str, tuple[str, ...]]:
    """Build a structured validation plan for a rich controlled gate."""

    return {
        "created_artifacts": definition.created_artifacts,
        "implementation_artifact_paths": definition.implementation_artifact_paths,
        "required_checks": definition.required_checks,
        "forbidden_changes": definition.forbidden_changes,
        "safety_boundaries": definition.safety_boundaries,
        "positive_assertions": definition.positive_assertions,
        "closure_criteria": definition.closure_criteria,
    }


def build_rich_gate_artifact_plan(definition: RichGateDefinition) -> RichGateArtifactPlan:
    """Build all rich generated gate artifacts without writing them."""

    return RichGateArtifactPlan(
        phase_identifier=definition.phase_identifier,
        phase_slug=definition.phase_slug,
        doc_artifact_path=definition.doc_artifact_path,
        test_artifact_path=definition.test_artifact_path,
        implementation_artifact_paths=definition.implementation_artifact_paths,
        document_text=build_rich_gate_document(definition),
        test_stub_text=build_rich_gate_test_stub(definition),
        validation_plan=build_rich_validation_plan(definition),
    )


def describe_rich_gate_template_contract() -> Mapping[str, str]:
    """Describe the static safety boundary for the rich gate template extension."""

    return {
        "record_id": GATE_GENERATOR_RICH_TEMPLATE_IMPLEMENTATION_RECORD_ID,
        "source_record_id": GATE_GENERATOR_RECORD_ID,
        "source_handle": GATE_GENERATOR_HANDLE,
        "determinism": "required",
        "output_mode": "text_and_structured_plans_only",
        "filesystem_write": "not_performed",
        "existing_file_modification": "not_performed",
        "command_execution": "not_performed",
        "subprocess_execution": "not_performed",
        "media_access": "not_performed",
        "folder_scan": "not_performed",
        "ffmpeg": "not_executed",
        "ffprobe": "not_executed",
        "scanner": "not_executed",
        "saas": "no_saas_integration",
        "database": "not_touched",
        "docker": "not_touched",
        "alembic": "not_touched",
        "stripe": "not_touched",
        "ai_jobs": "not_touched",
        "credits_ledger": "not_touched",
    }
