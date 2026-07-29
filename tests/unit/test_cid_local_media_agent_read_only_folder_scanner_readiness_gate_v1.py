from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.md"
TEST = ROOT / "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.py"

PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.READINESS.GATE.V1"
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_READINESS_GATE_V1_CLOSED"
NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1"

VIDEO_EXTENSIONS = [
    ".mp4",
    ".mov",
    ".mxf",
    ".mkv",
    ".avi",
    ".mts",
    ".m2ts",
    ".webm",
]
AUDIO_EXTENSIONS = [
    ".wav",
    ".bwf",
    ".aif",
    ".aiff",
    ".mp3",
    ".m4a",
    ".aac",
    ".flac",
    ".ogg",
]
IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".dng",
    ".cr2",
    ".cr3",
    ".arw",
    ".nef",
    ".orf",
    ".raf",
]

AUTHORIZED_FILES = {
    "docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.md",
    "tests/unit/test_cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.py",
}


def _text() -> str:
    assert DOC.exists(), f"missing document: {DOC}"
    return DOC.read_text(encoding="utf-8")


def _assert_all_present(text: str, required: list[str]) -> None:
    for value in required:
        assert value in text, f"Expected string not found: {value!r}"


def test_phase_identity_and_document_exist() -> None:
    text = _text()

    assert DOC.exists()
    assert TEST.exists()
    _assert_all_present(text, [PHASE, EXPECTED_RESULT])


def test_scope_is_limited_to_two_authorized_files() -> None:
    text = _text()

    _assert_all_present(text, [
        "This phase is documentation-only and test-only.",
        "This phase does not implement scanner runtime.",
        "This phase does not create CLI commands.",
        "This phase does not modify package entrypoints.",
        "This phase does not execute scans.",
        "This phase does not create runtime scripts.",
    ])
    for path in AUTHORIZED_FILES:
        assert path in text


def test_future_input_contract_rejects_unsafe_roots() -> None:
    text = _text()

    _assert_all_present(text, [
        "one local Linux absolute folder path",
        "must already exist",
        "reject an individual file as the input root",
        "reject a symlink as the input root",
        "reject URL-like inputs",
        "reject Windows drive paths",
        "reject UNC paths",
        "reject `/mnt` paths",
        "reject `wsl.localhost` paths",
        "reject `/opt/SERVICIOS_CINE` as the input root",
        "reject every descendant of `/opt/SERVICIOS_CINE` as the input root",
        "fail closed when input validation is ambiguous",
    ])


def test_read_only_traversal_and_privacy_boundaries_are_fixed() -> None:
    text = _text()

    _assert_all_present(text, [
        "strictly read-only",
        "controlled recursive traversal only",
        "must not follow symlinks",
        "superficial metadata based on `stat`",
        "must not open file contents",
        "must not read media bytes",
        "must not compute content hashes",
        "must not execute `ffprobe`",
        "must not execute `ffmpeg`",
        "must not use subprocess",
        "must not use shell execution",
        "must not use network access",
        "must not use a database",
        "must not use SaaS",
        "must not transcribe audio",
        "must not generate subtitles",
        "must not copy, move, rename, delete, overwrite, transcode, proxy, or modify any original material",
    ])


def test_stdout_only_sanitized_manifest_contract_is_present() -> None:
    text = _text()

    _assert_all_present(text, [
        "must not write artifacts to disk",
        "emit a sanitized JSON manifest to stdout",
        "must not contain absolute paths",
        "must not contain real filenames",
        "must not contain private folder names",
        "must not contain hostnames, usernames, machine names, credentials, tokens, or raw environment values",
    ])


def test_manifest_top_level_fields_are_required() -> None:
    text = _text()

    for field in [
        "schema_version",
        "status",
        "input_label",
        "privacy",
        "scanner_summary",
        "extension_summary",
        "warnings",
        "errors",
    ]:
        assert f"`{field}`" in text


def test_scanner_summary_fields_are_required() -> None:
    text = _text()

    for field in [
        "files_seen",
        "directories_seen",
        "media_candidates",
        "non_media_files",
        "symlinks_rejected",
        "total_bytes",
        "truncated",
    ]:
        assert f"`{field}`" in text


def test_initial_limits_and_controlled_termination_are_required() -> None:
    text = _text()

    _assert_all_present(text, [
        "`max_files = 5000`",
        "`max_depth = 8`",
        "`max_errors = 100`",
        "When `max_files` is reached",
        "When `max_depth` is reached",
        "When `max_errors` is reached",
        "set `truncated=true`",
        "terminate in a controlled way when a configured limit is reached",
    ])


def test_depth_semantics_are_defined() -> None:
    text = _text()

    _assert_all_present(text, [
        "`depth = 0` to the validated input root folder",
        "`depth = 1` to direct descendants of the validated input root folder",
        "Each deeper descendant must increment depth by one relative to its parent.",
        "must not descend into entries whose depth would exceed `max_depth`",
        "record a sanitized warning when traversal is stopped by `max_depth`",
    ])


def test_directories_seen_semantics_are_defined() -> None:
    text = _text()

    _assert_all_present(text, [
        "`directories_seen` value must include the validated input root folder",
        "`directories_seen` value must include only real directories actually visited",
        "`directories_seen` value must not include symlinks rejected during root validation or traversal",
        "`directories_seen` value must not include entries that are not directories",
        "`directories_seen` value must not include directories skipped because descending into them would exceed `max_depth`",
    ])


def test_total_bytes_semantics_are_defined() -> None:
    text = _text()

    _assert_all_present(text, [
        "`total_bytes` value must sum only `st_size` from regular files processed successfully",
        "`total_bytes` value must not include directory sizes",
        "`total_bytes` value must not include symlink sizes",
        "`total_bytes` value must not include rejected entries",
        "`total_bytes` value must not include files whose `stat` call fails",
        "`total_bytes` value must not require opening file contents",
    ])


def test_media_classification_rules_are_defined() -> None:
    text = _text()

    _assert_all_present(text, [
        "based exclusively on the fixed V1 extension allowlist",
        "compare extensions case-insensitively",
        "must not inspect file contents",
        "must not use MIME detection",
        "must not use magic-byte inspection",
        "must not use `ffprobe`",
        "must not use `ffmpeg`",
        "Files with no extension must count as `non_media_files`.",
        "Files with extensions outside the V1 allowlist must count as `non_media_files`.",
    ])


def test_v1_media_extension_allowlist_is_complete() -> None:
    text = _text()

    _assert_all_present(text, [
        "Video extensions:",
        "Audio extensions:",
        "Image extensions:",
    ])
    for extension in VIDEO_EXTENSIONS + AUDIO_EXTENSIONS + IMAGE_EXTENSIONS:
        assert f"`{extension}`" in text


def test_fail_closed_behavior_is_required() -> None:
    text = _text()

    _assert_all_present(text, [
        "## Fail-closed behavior",
        "invalid input root",
        "unreadable input root",
        "file root instead of folder root",
        "symlink root",
        "unsafe path policy",
        "repository path input",
        "traversal limit exhaustion",
        "repeated filesystem errors",
        "forbidden runtime capabilities",
        "A failed result must still be sanitized.",
        "A failed result must not include the rejected path.",
        "A failed result must not create artifacts.",
    ])


def test_runtime_cli_and_packaging_are_not_authorized() -> None:
    text = _text()

    _assert_all_present(text, [
        "scanner runtime implementation",
        "`cid scan` implementation",
        "CLI entrypoint creation",
        "packaging changes",
        "`pyproject.toml` changes",
        "runtime scripts",
        "real scan execution",
        "customer material processing",
        "public demo",
        "production use",
        "paid pilot",
    ])


def test_forbidden_dependencies_and_product_areas_are_blocked() -> None:
    text = _text()

    _assert_all_present(text, [
        "backend work",
        "frontend work",
        "database work",
        "SaaS integration",
        "Docker changes",
        "Alembic migrations",
        "Stripe changes",
        "authentication changes",
        "AI Jobs changes",
        "ledger changes",
        "ffprobe or ffmpeg execution",
        "subprocess, shell, or network use",
    ])


def test_next_allowed_phase_is_exact() -> None:
    text = _text()

    _assert_all_present(text, [
        "The only next runtime phase allowed by this readiness gate is:",
        NEXT_PHASE,
        "minimal, isolated, reversible, read-only, stdout-only",
    ])


def test_document_does_not_authorize_existing_runtime_files() -> None:
    text = _text()

    forbidden = [
        "scripts/local_media_agent/read_only_folder_scanner.py",
        "scripts/local_media_agent/cid_cli.py",
        "[project.scripts]",
        "cid =",
        "cid-local-media-agent-read-only-folder-scanner",
    ]
    for value in forbidden:
        assert value not in text
