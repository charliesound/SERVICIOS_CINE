from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

PREFLIGHT_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_preflight_contract_v1.md"
)
INPUT_FOLDER_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_input_folder_contract_v1.md"
)
INPUT_FOLDER_QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md"
)
PRIVACY_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_media_privacy_safety_gate_v1.md"
)

SYNTHETIC_CLI = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_cli.py"
SYNTHETIC_PREFLIGHT = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_preflight_check.py"
SYNTHETIC_RENDERER = REPO_ROOT / "scripts" / "cid_local_media_agent_synthetic_visible_report_renderer.py"
SCANNER_SCRIPT = REPO_ROOT / "scripts" / "cid_media_agent_scan.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_real_preflight_contract_declares_phase_baseline_and_decision() -> None:
    text = _read(PREFLIGHT_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1" in text
    assert "Stable HEAD before this phase: `e42c575`." in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1" in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_PREFLIGHT_CONTRACT_READY_FOR_QA_GATE_WITH_RESTRICTIONS" in text


def test_real_preflight_contract_blocks_execution_implementation_and_runtime_changes() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "It does not execute real media",
        "does not inspect real media streams",
        "does not call ffprobe/ffmpeg on real files",
        "does not implement the preflight",
        "does not integrate the scanner",
        "does not generate a real report",
        "does not modify runtime code",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_references_previous_gates_and_existing_docs() -> None:
    text = _read(PREFLIGHT_DOC)

    assert "docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md" in text
    assert INPUT_FOLDER_DOC.exists()
    assert INPUT_FOLDER_QA_DOC.exists()
    assert PRIVACY_DOC.exists()


def test_real_preflight_contract_defines_fail_closed_contract_scope() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "The future real preflight must be a fail-closed safety check that runs before any real scan or report generation.",
        "may only validate local filesystem conditions, counts, sizes, extensions, output separation and privacy-safe reporting readiness.",
        "must not decode media, probe media streams, extract frames, create thumbnails, create waveforms, transcribe, translate, sync, subtitle, export to NLE or upload anything.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_explicit_user_inputs_and_acknowledgements() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "input folder path;",
        "output folder path;",
        "local-only execution mode;",
        "explicit acknowledgement that the selected media is internal test media owned or authorized by the developer;",
        "explicit acknowledgement that client material, confidential productions, original camera masters and whole-drive material are excluded.",
        "Missing acknowledgements must fail closed.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_input_folder_checks() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "is manually selected by the user;",
        "exists before execution;",
        "is a directory, not a file;",
        "is local to the machine running the tool;",
        "is not a drive root;",
        "is not the user home directory root;",
        "is not a system directory;",
        "is not a hidden application/cache/temp directory;",
        "is not a cloud-sync root by default;",
        "is not a network share by default;",
        "is readable by the current user;",
        "is treated as read-only input by CID Local Media Agent;",
        "does not require elevated privileges;",
        "does not contain symlink traversal by default.",
        "Any failed input folder check must produce `PREFLIGHT_FAIL`.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_output_folder_checks() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "is manually selected by the user;",
        "is local to the machine running the tool;",
        "exists before execution unless a later explicit implementation phase authorizes safe creation;",
        "is writable by the current user;",
        "is separated from the input folder by default;",
        "is not inside the input folder by default;",
        "is not the same path as the input folder;",
        "does not require overwriting source media;",
        "does not require copying source media by default;",
        "is suitable for future metadata/report artifacts only.",
        "Any failed output folder check must produce `PREFLIGHT_FAIL`.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_file_inventory_limits() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "A future real preflight may enumerate files only far enough to validate limits and extensions.",
        "maximum file count: 25 media files;",
        "maximum total selected media size: 10 GB;",
        "maximum scan depth: 3 directory levels;",
        "no automatic scan of a whole disk, user profile, media library or project archive;",
        "no batch processing of multiple unrelated projects;",
        "no recursive traversal beyond the configured depth;",
        "no following symlinks by default.",
        "Any failed inventory check must produce `PREFLIGHT_FAIL`.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_extension_allowlist_without_decoding() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "video: `.mov`, `.mp4`, `.mxf`;",
        "audio: `.wav`, `.aif`, `.aiff`.",
        "All other extensions must be ignored or rejected until a later explicit format-support gate exists.",
        "A future real preflight must never infer format support by decoding media content in this first-test path.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_privacy_checks() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "no full private paths in user-facing reports by default;",
        "no user home directory exposure by default;",
        "no client names or project names in logs by default;",
        "no telemetry containing file names, full paths, client names or project names;",
        "no upload, cloud sync or external API transmission;",
        "errors must fail closed when path privacy cannot be guaranteed.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_defines_result_statuses() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "`PREFLIGHT_PASS` only when every mandatory check passes;",
        "`PREFLIGHT_FAIL` when any mandatory check fails;",
        "`PREFLIGHT_BLOCKED` when the operation is outside the authorized first-test scope.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_defines_sanitized_result_payload() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "sanitized input folder label;",
        "sanitized output folder label;",
        "media file count;",
        "total selected media size bucket;",
        "maximum detected scan depth;",
        "accepted extension counts;",
        "ignored or rejected extension counts;",
        "failed check identifiers;",
        "human-readable remediation guidance without private full paths.",
        "must not include full private paths, raw filenames, client names, project names, media hashes or media content.",
    ]

    for item in required:
        assert item in text


def test_real_preflight_contract_requires_future_gates_before_execution() -> None:
    text = _read(PREFLIGHT_DOC)

    required_gates = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1",
    ]

    for gate in required_gates:
        assert gate in text


def test_real_preflight_contract_explicitly_blocks_current_phase_actions() -> None:
    text = _read(PREFLIGHT_DOC)

    blocked = [
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "media stream probing;",
        "media decoding;",
        "real preflight implementation;",
        "scanner integration;",
        "real report generation;",
        "thumbnail, waveform or frame extraction;",
        "sync;",
        "transcription;",
        "translation;",
        "subtitle generation;",
        "NLE export;",
        "runtime implementation;",
        "packaging implementation;",
        "installable entry point;",
        "shell launcher;",
        "desktop app;",
        "licensing;",
        "client delivery;",
        "SaaS/backend/frontend/database/Docker/Alembic work;",
        "Stripe, AI Jobs, credits or ledger work.",
    ]

    for item in blocked:
        assert item in text


def test_real_preflight_contract_does_not_authorize_real_execution_by_language() -> None:
    text = _read(PREFLIGHT_DOC)

    assert "This real preflight contract does not authorize real execution." in text
    assert "A future phase may audit this preflight contract." in text
    assert "No real media execution is authorized by this document." in text


def test_previous_input_folder_qa_gate_still_blocks_execution() -> None:
    text = _read(INPUT_FOLDER_QA_DOC)

    required = [
        "No real media execution is authorized by this QA gate.",
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "real preflight implementation;",
        "scanner integration;",
        "REAL_INPUT_FOLDER_CONTRACT_QA_GATE_READY_FOR_REAL_PREFLIGHT_CONTRACT_WITH_RESTRICTIONS",
    ]

    for item in required:
        assert item in text


def test_previous_privacy_gate_still_blocks_upload_and_sensitive_output() -> None:
    text = _read(PRIVACY_DOC)

    required = [
        "media files remain on the local disk;",
        "media files are not uploaded;",
        "media files are not sent to cloud services;",
        "media files are not sent to external APIs;",
        "full private paths are not exposed in user-facing reports by default;",
        "no telemetry containing media names, full paths, client names or project names;",
        "No real media execution is authorized by this privacy safety gate.",
    ]

    for item in required:
        assert item in text


def test_runtime_sources_are_not_modified_for_real_preflight_contract() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.PREFLIGHT.CONTRACT",
        "REAL_PREFLIGHT_CONTRACT_READY",
        "PREFLIGHT_BLOCKED",
        "maximum file count: 25 media files",
        "maximum total selected media size: 10 GB",
        "real media execution",
        "client delivery",
    ]

    for source in sources:
        for term in forbidden_runtime_terms:
            assert term not in source

    cli_source = sources[0]
    renderer_source = sources[2]
    scanner_source = sources[3]

    assert "cid_media_agent_scan" not in cli_source
    assert "--real" not in cli_source
    assert "PREFLIGHT_BLOCKED" not in renderer_source
    assert "PREFLIGHT_BLOCKED" not in scanner_source
