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
