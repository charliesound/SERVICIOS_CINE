from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_preflight_contract_qa_gate_v1.md"
)
PREFLIGHT_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_preflight_contract_v1.md"
)
PREFLIGHT_TEST = REPO_ROOT / "tests" / "unit" / (
    "test_cid_local_media_agent_real_preflight_contract.py"
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


def test_preflight_qa_gate_declares_phase_baseline_and_decision() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1" in text
    assert "Stable HEAD before this phase: `45ce7b6`." in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1" in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_PREFLIGHT_CONTRACT_QA_GATE_READY_FOR_IMPLEMENTATION_CONTRACT_WITH_RESTRICTIONS" in text


def test_preflight_qa_gate_blocks_real_execution_and_runtime_changes() -> None:
    text = _read(QA_DOC)

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


def test_preflight_qa_gate_references_target_contract_test_and_prior_gates() -> None:
    text = _read(QA_DOC)

    assert "docs/product/local_media_agent/cid_local_media_agent_real_preflight_contract_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_preflight_contract.py" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md" in text
    assert PREFLIGHT_DOC.exists()
    assert PREFLIGHT_TEST.exists()
    assert INPUT_FOLDER_QA_DOC.exists()
    assert PRIVACY_DOC.exists()


def test_preflight_qa_gate_allowed_files_are_limited() -> None:
    text = _read(QA_DOC)

    assert "Allowed files for this phase:" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_preflight_contract_qa_gate_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_preflight_contract_qa_gate.py" in text
    assert "Runtime files may be audited by tests but must not be modified." in text


def test_preflight_qa_gate_audits_required_contract_assertions() -> None:
    text = _read(QA_DOC)

    required = [
        "declares the correct phase and stable baseline;",
        "references the completed input folder contract QA gate;",
        "references the completed privacy safety gate;",
        "declares documentation/test-only status;",
        "blocks real media execution;",
        "blocks real media stream inspection;",
        "blocks ffprobe/ffmpeg execution on real files;",
        "blocks real preflight implementation;",
        "blocks scanner integration;",
        "blocks real report generation;",
        "blocks runtime implementation;",
        "defines the future preflight as a fail-closed safety check;",
        "limits the future preflight to local filesystem, counts, sizes, extensions, output separation and privacy-safe reporting readiness;",
        "forbids media decoding, media stream probing, frame extraction, thumbnails, waveforms, transcription, translation, sync, subtitles, NLE export and upload.",
    ]

    for item in required:
        assert item in text


def test_preflight_qa_gate_audits_inputs_and_acknowledgements() -> None:
    text = _read(QA_DOC)

    required = [
        "input folder path;",
        "output folder path;",
        "local-only execution mode;",
        "explicit acknowledgement that selected media is internal test media owned or authorized by the developer;",
        "explicit acknowledgement that client material, confidential productions, original camera masters and whole-drive material are excluded;",
        "missing acknowledgements fail closed.",
    ]

    for item in required:
        assert item in text


def test_preflight_qa_gate_audits_folder_and_inventory_checks() -> None:
    text = _read(QA_DOC)

    required = [
        "input folder is manually selected, existing, directory-based, local, readable and read-only;",
        "input folder is not drive root, user home root, system directory, hidden application/cache/temp directory, cloud-sync root or network share by default;",
        "input folder does not require elevated privileges;",
        "input folder does not contain symlink traversal by default;",
        "output folder is manually selected, local, existing unless later safe creation is authorized, writable and separated from input;",
        "output folder is not inside input and is not the same path as input;",
        "output folder does not require overwriting or copying source media;",
        "maximum file count: 25 media files;",
        "maximum total selected media size: 10 GB;",
        "maximum scan depth: 3 directory levels;",
        "no whole-disk, user-profile, media-library or project-archive scan;",
        "no batch processing of multiple unrelated projects;",
        "no recursive traversal beyond configured depth;",
        "no following symlinks by default.",
        "Any failed mandatory folder or inventory check must produce `PREFLIGHT_FAIL`.",
    ]

    for item in required:
        assert item in text


def test_preflight_qa_gate_audits_format_and_privacy_checks() -> None:
    text = _read(QA_DOC)

    required = [
        "video allowlist: `.mov`, `.mp4`, `.mxf`;",
        "audio allowlist: `.wav`, `.aif`, `.aiff`;",
        "all other extensions are ignored or rejected until a later explicit format-support gate exists;",
        "format support is never inferred by decoding media content in the first-test path;",
        "no full private paths in user-facing reports by default;",
        "no user home directory exposure by default;",
        "no client names or project names in logs by default;",
        "no telemetry containing file names, full paths, client names or project names;",
        "no upload, cloud sync or external API transmission;",
        "errors fail closed when path privacy cannot be guaranteed.",
    ]

    for item in required:
        assert item in text


def test_preflight_qa_gate_audits_result_statuses_and_payload() -> None:
    text = _read(QA_DOC)

    required = [
        "`PREFLIGHT_PASS` only when every mandatory check passes;",
        "`PREFLIGHT_FAIL` when any mandatory check fails;",
        "`PREFLIGHT_BLOCKED` when the operation is outside the authorized first-test scope.",
        "sanitized input folder label;",
        "sanitized output folder label;",
        "media file count;",
        "total selected media size bucket;",
        "maximum detected scan depth;",
        "accepted extension counts;",
        "ignored or rejected extension counts;",
        "failed check identifiers;",
        "human-readable remediation guidance without private full paths.",
        "excludes full private paths, raw filenames, client names, project names, media hashes and media content.",
    ]

    for item in required:
        assert item in text


def test_target_preflight_contract_still_contains_fail_closed_scope() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "The future real preflight must be a fail-closed safety check that runs before any real scan or report generation.",
        "may only validate local filesystem conditions, counts, sizes, extensions, output separation and privacy-safe reporting readiness.",
        "must not decode media, probe media streams, extract frames, create thumbnails, create waveforms, transcribe, translate, sync, subtitle, export to NLE or upload anything.",
    ]

    for item in required:
        assert item in text


def test_target_preflight_contract_still_contains_required_inputs_and_checks() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "input folder path;",
        "output folder path;",
        "local-only execution mode;",
        "explicit acknowledgement that the selected media is internal test media owned or authorized by the developer;",
        "explicit acknowledgement that client material, confidential productions, original camera masters and whole-drive material are excluded.",
        "Missing acknowledgements must fail closed.",
        "Any failed input folder check must produce `PREFLIGHT_FAIL`.",
        "Any failed output folder check must produce `PREFLIGHT_FAIL`.",
        "Any failed inventory check must produce `PREFLIGHT_FAIL`.",
    ]

    for item in required:
        assert item in text


def test_target_preflight_contract_still_contains_limits_formats_and_privacy() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "maximum file count: 25 media files;",
        "maximum total selected media size: 10 GB;",
        "maximum scan depth: 3 directory levels;",
        "no recursive traversal beyond the configured depth;",
        "no following symlinks by default.",
        "video: `.mov`, `.mp4`, `.mxf`;",
        "audio: `.wav`, `.aif`, `.aiff`.",
        "All other extensions must be ignored or rejected until a later explicit format-support gate exists.",
        "no full private paths in user-facing reports by default;",
        "no upload, cloud sync or external API transmission;",
        "errors must fail closed when path privacy cannot be guaranteed.",
    ]

    for item in required:
        assert item in text


def test_target_preflight_contract_still_contains_result_contract() -> None:
    text = _read(PREFLIGHT_DOC)

    required = [
        "`PREFLIGHT_PASS` only when every mandatory check passes;",
        "`PREFLIGHT_FAIL` when any mandatory check fails;",
        "`PREFLIGHT_BLOCKED` when the operation is outside the authorized first-test scope.",
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


def test_target_preflight_contract_test_covers_required_assertions() -> None:
    text = _read(PREFLIGHT_TEST)

    required_tests = [
        "test_real_preflight_contract_defines_fail_closed_contract_scope",
        "test_real_preflight_contract_requires_explicit_user_inputs_and_acknowledgements",
        "test_real_preflight_contract_requires_input_folder_checks",
        "test_real_preflight_contract_requires_output_folder_checks",
        "test_real_preflight_contract_requires_file_inventory_limits",
        "test_real_preflight_contract_requires_extension_allowlist_without_decoding",
        "test_real_preflight_contract_defines_result_statuses",
        "test_runtime_sources_are_not_modified_for_real_preflight_contract",
    ]

    for name in required_tests:
        assert name in text


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


def test_preflight_qa_gate_requires_next_gates_before_real_execution() -> None:
    text = _read(QA_DOC)

    required_gates = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1",
    ]

    for gate in required_gates:
        assert gate in text


def test_preflight_qa_gate_explicitly_blocks_current_phase_actions() -> None:
    text = _read(QA_DOC)

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


def test_preflight_qa_gate_does_not_authorize_real_execution_by_language() -> None:
    text = _read(QA_DOC)

    assert "A future phase may define implementation boundaries." in text
    assert "No real media execution is authorized by this QA gate." in text


def test_runtime_sources_are_not_modified_for_real_preflight_qa_gate() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.PREFLIGHT.CONTRACT.QA.GATE",
        "REAL_PREFLIGHT_CONTRACT_QA_GATE_READY",
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
