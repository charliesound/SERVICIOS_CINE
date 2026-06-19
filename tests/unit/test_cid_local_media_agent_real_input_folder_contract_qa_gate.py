from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

QA_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md"
)
INPUT_FOLDER_DOC = REPO_ROOT / "docs" / "product" / "local_media_agent" / (
    "cid_local_media_agent_real_input_folder_contract_v1.md"
)
INPUT_FOLDER_TEST = REPO_ROOT / "tests" / "unit" / (
    "test_cid_local_media_agent_real_input_folder_contract.py"
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


def test_input_folder_qa_gate_declares_phase_baseline_and_decision() -> None:
    text = _read(QA_DOC)

    assert "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1" in text
    assert "Stable HEAD before this phase: `efd347f`." in text
    assert "CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1" in text
    assert "This phase is documentation/test-only." in text
    assert "REAL_INPUT_FOLDER_CONTRACT_QA_GATE_READY_FOR_REAL_PREFLIGHT_CONTRACT_WITH_RESTRICTIONS" in text


def test_input_folder_qa_gate_blocks_real_execution_and_runtime_changes() -> None:
    text = _read(QA_DOC)

    required = [
        "It does not execute real media",
        "does not call ffprobe/ffmpeg on real files",
        "does not implement real preflight",
        "does not implement scanner integration",
        "does not generate a real report",
        "does not modify runtime code",
    ]

    for item in required:
        assert item in text


def test_input_folder_qa_gate_references_target_contract_and_test() -> None:
    text = _read(QA_DOC)

    assert "docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_input_folder_contract.py" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md" in text
    assert INPUT_FOLDER_DOC.exists()
    assert INPUT_FOLDER_TEST.exists()
    assert PRIVACY_DOC.exists()


def test_input_folder_qa_gate_allowed_files_are_limited() -> None:
    text = _read(QA_DOC)

    assert "Allowed files for this phase:" in text
    assert "docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md" in text
    assert "tests/unit/test_cid_local_media_agent_real_input_folder_contract_qa_gate.py" in text
    assert "Runtime files may be audited by tests but must not be modified." in text


def test_input_folder_qa_gate_audits_required_contract_assertions() -> None:
    text = _read(QA_DOC)

    required = [
        "declares the correct phase and stable baseline;",
        "references the completed privacy safety gate;",
        "declares documentation/test-only status;",
        "blocks real media execution in the current phase;",
        "blocks ffprobe/ffmpeg execution on real files;",
        "blocks real preflight implementation;",
        "blocks scanner integration;",
        "blocks real report generation;",
        "blocks runtime implementation;",
        "defines the input folder as manually selected and local-only;",
        "requires copied test media owned or explicitly authorized by the developer;",
        "excludes client material, confidential productions, original camera masters and whole-drive material;",
        "requires the input folder to exist before execution;",
        "requires the input folder to be a directory, not a file;",
        "rejects drive roots, user home root, system directories and hidden application/cache/temp directories;",
        "rejects cloud-sync roots and network shares by default;",
        "treats input as read-only;",
        "requires path privacy by default.",
    ]

    for item in required:
        assert item in text


def test_input_folder_qa_gate_audits_required_limits() -> None:
    text = _read(QA_DOC)

    required = [
        "maximum file count: 25 media files;",
        "maximum total selected media size: 10 GB;",
        "maximum scan depth: 3 directory levels;",
        "no automatic scan of a whole disk, user profile, media library or project archive;",
        "no batch processing of multiple unrelated projects;",
        "limits may change only through a later explicit capacity gate.",
    ]

    for item in required:
        assert item in text


def test_input_folder_qa_gate_audits_required_format_allowlist() -> None:
    text = _read(QA_DOC)

    required = [
        "video: `.mov`, `.mp4`, `.mxf`;",
        "audio: `.wav`, `.aif`, `.aiff`;",
        "all other extensions are ignored or rejected until a later explicit format-support gate exists.",
    ]

    for item in required:
        assert item in text


def test_input_folder_qa_gate_audits_output_folder_separation() -> None:
    text = _read(QA_DOC)

    required = [
        "manually selected local output folder;",
        "separated from input folder by default;",
        "no overwrite of source media;",
        "no copy of source media by default;",
        "output contains only future metadata/report artifacts, never modified source media.",
    ]

    for item in required:
        assert item in text


def test_target_input_folder_contract_still_contains_required_folder_rules() -> None:
    text = _read(INPUT_FOLDER_DOC)

    required = [
        "The first real input folder must be a manually selected local directory created specifically for internal laboratory testing.",
        "The input folder must contain only copied test media owned or explicitly authorized by the developer.",
        "The input folder must not contain client material, confidential productions, original camera masters or whole-drive material.",
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
        "is treated as read-only input by CID Local Media Agent.",
    ]

    for item in required:
        assert item in text


def test_target_input_folder_contract_still_contains_limits_formats_and_output_rules() -> None:
    text = _read(INPUT_FOLDER_DOC)

    required = [
        "maximum file count: 25 media files;",
        "maximum total selected media size: 10 GB;",
        "maximum scan depth: 3 directory levels;",
        "video: `.mov`, `.mp4`, `.mxf`;",
        "audio: `.wav`, `.aif`, `.aiff`.",
        "All other extensions must be ignored or rejected by future preflight behavior until a later explicit format-support gate exists.",
        "A future real preflight must require a manually selected local output folder.",
        "be separated from the input folder by default;",
        "not overwrite source media;",
        "not copy source media by default;",
        "contain only future generated metadata/report artifacts, never modified source media.",
    ]

    for item in required:
        assert item in text


def test_target_input_folder_contract_still_preserves_path_privacy_and_blocks_execution() -> None:
    text = _read(INPUT_FOLDER_DOC)

    required = [
        "no full private paths in user-facing reports by default;",
        "no user home directory exposure by default;",
        "no client names or project names in logs by default;",
        "no telemetry containing file names, full paths, client names or project names;",
        "errors must fail closed when path privacy cannot be guaranteed.",
        "No real media execution is authorized by this document.",
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
        "real preflight implementation;",
        "scanner integration;",
    ]

    for item in required:
        assert item in text


def test_target_input_folder_contract_test_covers_required_assertions() -> None:
    text = _read(INPUT_FOLDER_TEST)

    required_tests = [
        "test_input_folder_contract_declares_phase_baseline_and_decision",
        "test_input_folder_contract_requires_local_only_folder_rules",
        "test_input_folder_contract_sets_first_real_test_size_limits",
        "test_input_folder_contract_sets_first_real_test_extension_allowlist",
        "test_input_folder_contract_requires_output_folder_separation",
        "test_input_folder_contract_preserves_path_privacy",
        "test_runtime_sources_are_not_modified_for_input_folder_contract",
    ]

    for name in required_tests:
        assert name in text


def test_privacy_gate_still_blocks_upload_cloud_and_sensitive_paths() -> None:
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


def test_input_folder_qa_gate_requires_next_gates_before_real_execution() -> None:
    text = _read(QA_DOC)

    required_gates = [
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1",
        "CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1",
    ]

    for gate in required_gates:
        assert gate in text


def test_input_folder_qa_gate_explicitly_blocks_current_phase_actions() -> None:
    text = _read(QA_DOC)

    blocked = [
        "real media execution;",
        "ffprobe or ffmpeg execution on real files;",
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


def test_input_folder_qa_gate_does_not_authorize_real_execution_by_language() -> None:
    text = _read(QA_DOC)

    assert "A future phase may define the real preflight contract." in text
    assert "No real media execution is authorized by this QA gate." in text


def test_runtime_sources_are_not_modified_for_input_folder_qa_gate() -> None:
    sources = [
        _read(SYNTHETIC_CLI),
        _read(SYNTHETIC_PREFLIGHT),
        _read(SYNTHETIC_RENDERER),
        _read(SCANNER_SCRIPT),
    ]

    forbidden_runtime_terms = [
        "REAL.INPUT.FOLDER.CONTRACT.QA.GATE",
        "REAL_INPUT_FOLDER_CONTRACT_QA_GATE_READY",
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
    assert "--preflight" not in renderer_source
    assert "PREFLIGHT_PASS" not in renderer_source
    assert "PREFLIGHT_FAIL" not in renderer_source
    assert "PREFLIGHT_PASS" not in scanner_source
    assert "PREFLIGHT_FAIL" not in scanner_source
