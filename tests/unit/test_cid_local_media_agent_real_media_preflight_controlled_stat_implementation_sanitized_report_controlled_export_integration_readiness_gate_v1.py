from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_controlled_export_integration_readiness_gate_v1.md"
RENDERER = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_sanitized_report_renderer.py"
RENDERER_QA_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.md"
RENDERER_QA_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_qa_gate_v1.py"
RENDERER_IMPL_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.md"
RENDERER_IMPL_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_renderer_implementation_gate_v1.py"
CONTRACT_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_contract_gate_v1.md"
CONTRACT_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_contract_gate_v1.py"
READINESS_DOC = ROOT / "docs/product/local_media_agent/cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_readiness_gate_v1.md"
READINESS_TEST = ROOT / "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_implementation_sanitized_report_readiness_gate_v1.py"
CONTROLLED_STAT_IMPL = ROOT / "scripts/local_media_agent/real_media_preflight_controlled_stat_implementation.py"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION."
    "SANITIZED_REPORT.CONTROLLED_EXPORT_INTEGRATION.READINESS.GATE.V1"
)
EXPECTED_RESULT = (
    "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_"
    "SANITIZED_REPORT_CONTROLLED_EXPORT_INTEGRATION_READINESS_GATE_V1_CLOSED"
)
STARTING_STATE = (
    "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_QA_PASSED_READY_FOR_"
    "CONTROLLED_EXPORT_INTEGRATION_READINESS_GATE"
)
TARGET_STATE = (
    "CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_CONTROLLED_EXPORT_INTEGRATION_"
    "READINESS_PASSED_READY_FOR_CONTROLLED_EXPORT_INTEGRATION_GATE"
)
EXPECTED_HEAD = "9fe1149d30adb72c445b42c2613e87db0ed350d7"
FIXED_TOKEN = "REDACTED_SANITIZED_LOCAL_SINGLE_VIDEO_SELECTION_TOKEN"
EXCLUDED_TEST = (
    "tests/unit/test_cid_local_media_agent_real_media_preflight_controlled_stat_"
    "implementation_sanitized_report_renderer_implementation_readiness_gate_v1.py"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_readiness_gate_document_exists_and_declares_identity() -> None:
    assert DOC.exists()
    text = _text(DOC)
    _assert_all_present(text, [
        PHASE,
        EXPECTED_RESULT,
        STARTING_STATE,
        TARGET_STATE,
        EXPECTED_HEAD,
    ])


def test_readiness_gate_declares_documental_test_only_scope() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This phase is a readiness gate.",
        "This phase is documentation-only and test-only.",
        "This phase does not implement export runtime.",
        "This phase does not write reports to disk.",
        "This phase does not create real export folders.",
        "This phase does not modify the renderer.",
        "This phase does not modify runtime code.",
        "This phase does not create output artifacts.",
    ])


def test_readiness_gate_requires_pure_renderer_protection() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The existing renderer must remain pure and intact.",
        "The existing renderer must keep returning deterministic sanitized Markdown text only.",
        "The existing renderer must not write files.",
        "The existing renderer must not execute commands.",
        "The existing renderer must not read real media.",
        "The existing renderer must not expose the operator token.",
        f"The operator token must remain redacted as `{FIXED_TOKEN}`.",
    ])


def test_readiness_gate_references_required_source_artifacts() -> None:
    required_paths = [
        RENDERER_QA_DOC,
        RENDERER_QA_TEST,
        RENDERER_IMPL_DOC,
        RENDERER_IMPL_TEST,
        CONTRACT_DOC,
        CONTRACT_TEST,
        READINESS_DOC,
        READINESS_TEST,
        RENDERER,
        CONTROLLED_STAT_IMPL,
    ]
    text = _text(DOC)
    for path in required_paths:
        assert path.exists(), path
        assert str(path.relative_to(ROOT)) in text


def test_future_export_requirements_are_explicit_and_controlled() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The future controlled export integration must be implemented in a later separate phase.",
        "The future controlled export integration must be explicit, opt-in, controlled, and validated.",
        "The future controlled export integration may accept only the sanitized Markdown generated by the validated renderer as its input.",
        "The future controlled export integration must reject any raw operator token, raw local path, raw filename, parent folder, real media path, or scanner output that has not already been sanitized by the validated renderer.",
        "The future output path must be validated, controlled, and safe before any later write-enabled implementation is considered.",
        "The future export must remain local-only unless a later explicit phase changes that boundary.",
    ])


def test_non_authorization_boundaries_are_complete() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "export runtime implementation",
        "real report writing",
        "real export folder creation",
        "write-enabled export behavior",
        "output artifact creation",
        "renderer modification",
        "scanner runtime changes",
        "real media reads",
        "real media probing",
        "real media scanning",
        "real media decoding",
        "transcription",
        "thumbnail generation",
        "waveform generation",
        "ffprobe execution",
        "FFmpeg execution",
        "external process execution",
        "backend SaaS changes",
        "frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits changes",
        "ledger changes",
    ])


def test_excluded_historical_renderer_readiness_test_is_declared() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "The historical renderer implementation readiness test is intentionally excluded from this phase:",
        EXCLUDED_TEST,
        "That test belongs to the pre-implementation renderer phase and is not applicable after the renderer has been created and validated.",
    ])


def test_required_validation_battery_is_declared() -> None:
    text = _text(DOC)
    _assert_all_present(text, [
        "This controlled export integration readiness gate test.",
        "The sanitized report renderer QA gate test.",
        "The sanitized report renderer implementation gate test.",
        "The sanitized report contract gate test.",
        "The sanitized report readiness gate test.",
        "The controlled stat implementation gate test.",
        "The WSL repo guard script.",
        "The database regression guard script.",
        "A final scope check confirming that only this readiness gate document and test changed.",
    ])


def test_document_contains_no_windows_or_mount_paths() -> None:
    text = _text(DOC)
    forbidden_fragments = [
        "C:" + "\\",
        "\\" + "\\" + "wsl.localhost",
        "/mnt/" + "c",
        "/mnt/" + "C",
    ]
    for fragment in forbidden_fragments:
        assert fragment not in text


def test_document_does_not_authorize_runtime_export_patterns() -> None:
    text = _text(DOC).lower()
    forbidden_claims = [
        "export runtime is authorized",
        "real report writing is authorized",
        "real export folder creation is authorized",
        "write-enabled export is authorized",
        "output artifact creation is authorized",
        "renderer modification is authorized",
        "scanner runtime is authorized",
        "real media reads are authorized",
        "ffprobe execution is authorized",
        "ffmpeg execution is authorized",
        "external process execution is authorized",
        "backend saas changes are authorized",
        "database changes are authorized",
        "docker changes are authorized",
    ]
    for claim in forbidden_claims:
        assert claim not in text


def test_renderer_source_remains_non_writing_and_non_executing() -> None:
    text = _text(RENDERER)
    forbidden_patterns = [
        "sub" + "process.run",
        "sub" + "process.Popen",
        "os.system",
        "shell=True",
        "open(",
        ".write(",
        ".unlink(",
        ".rename(",
        ".replace(",
        "ffmpeg -",
        "ffprobe -",
        "scanner_runtime",
        "backend_runtime",
        "Dockerfile",
    ]
    for pattern in forbidden_patterns:
        assert pattern not in text


def test_renderer_qa_gate_closing_state_feeds_this_readiness_gate() -> None:
    text = _text(RENDERER_QA_DOC)
    _assert_all_present(text, [
        "CID.LOCAL_MEDIA_AGENT.REAL_MEDIA_PREFLIGHT.CONTROLLED_STAT_IMPLEMENTATION.SANITIZED_REPORT.RENDERER_QA.GATE.V1",
        "LOCAL_MEDIA_AGENT_REAL_MEDIA_PREFLIGHT_CONTROLLED_STAT_IMPLEMENTATION_SANITIZED_REPORT_RENDERER_QA_GATE_V1_CLOSED",
        STARTING_STATE,
    ])


def test_this_test_does_not_call_external_processes() -> None:
    source = _text(Path(__file__))
    assert "import " + "sub" + "process" not in source
    assert "from " + "sub" + "process" not in source
    assert "sub" + "process." not in source
    assert "import" + "lib" not in source
