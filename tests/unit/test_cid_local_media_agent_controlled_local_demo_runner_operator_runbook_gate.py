from pathlib import Path

DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_controlled_local_demo_runner_operator_runbook_gate_v1.md"
)

PHASE_ID = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.RUNBOOK.GATE.V1"
)

EXPECTED_CLOSE_TOKEN = (
    "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_RUNBOOK_GATE_V1_CLOSED"
)

EXPECTED_BASELINE = "c98fde139a28b464c2225f7bbea90b46aafd4117"
EXPECTED_PREVIOUS_RESULT = (
    "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_NARRATIVE_GATE_V1_CLOSED"
)
CONTROLLED_SHA256 = "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f"
CONTROLLED_BYTES = "167"
CONTROLLED_ARTIFACT = "controlled_visible_report.controlled.txt"


def _doc() -> str:
    assert DOC_PATH.exists(), f"Missing operator runbook gate document: {DOC_PATH}"
    return DOC_PATH.read_text(encoding="utf-8")


def test_operator_runbook_gate_document_exists_and_names_phase() -> None:
    text = _doc()

    assert "Controlled Local Demo Runner Operator Runbook Gate V1" in text
    assert PHASE_ID in text
    assert EXPECTED_CLOSE_TOKEN in text
    assert "INTERNAL_OPERATOR_RUNBOOK_DEFINED" in text


def test_operator_runbook_gate_preserves_stable_baseline_and_previous_gate() -> None:
    text = _doc()

    assert EXPECTED_BASELINE in text
    assert EXPECTED_PREVIOUS_RESULT in text
    assert "cid-dev-stable-local-media-agent-controlled-local-demo-runner-demo-narrative-gate-v1-20260630" in text


def test_operator_runbook_gate_is_documentation_and_qa_only() -> None:
    text = _doc()

    required_tokens = [
        "DOCUMENTATION_AND_QA_ONLY",
        "No implementation changes.",
        "No `pyproject.toml` change.",
        "No runtime change.",
        "No command entrypoint change.",
        "No scanner implementation.",
        "No SaaS integration.",
        "No database access.",
        "No installer.",
        "No backend change.",
        "No frontend change.",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_contains_pre_demo_checklist() -> None:
    text = _doc()

    required_tokens = [
        "WORKTREE_CLEAN_BEFORE_DEMO",
        "WSL_REPO_CONTEXT_CONFIRMED",
        "`.venv` is activated.",
        "No client media is present in the demo input path.",
        "No real camera, sound, subtitle, EDL, XML, AAF, or DaVinci Resolve project file is used.",
        "command -v cid-local-media-agent-visible-report-write-enabled-export",
        "command -v cid-local-media-agent-controlled-local-demo-runner",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_contains_ordered_live_demo_sequence() -> None:
    text = _doc()

    help_index = text.index("cid-local-media-agent-controlled-local-demo-runner --help")
    json_index = text.index("cid-local-media-agent-controlled-local-demo-runner --result-json")
    keep_index = text.index(
        "cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output"
    )
    cleanup_index = text.index("Manual cleanup after preserved-output inspection")

    assert help_index < json_index < keep_index < cleanup_index


def test_operator_runbook_gate_pins_controlled_artifact_identity() -> None:
    text = _doc()

    assert CONTROLLED_ARTIFACT in text
    assert CONTROLLED_SHA256 in text
    assert f"`{CONTROLLED_BYTES}`" in text
    assert "CONTROLLED_ARTIFACT_NAME_VERIFIED" in text
    assert "CONTROLLED_SHA256_VERIFIED" in text
    assert "CONTROLLED_BYTE_COUNT_VERIFIED" in text


def test_operator_runbook_gate_defines_evidence_pack_checklist() -> None:
    text = _doc()

    required_tokens = [
        "HELP_OUTPUT_CAPTURED",
        "RESULT_JSON_CAPTURED",
        "KEEP_OUTPUT_JSON_CAPTURED",
        "TEMP_OUTPUT_CLEANUP_BY_DEFAULT",
        "KEEP_OUTPUT_REQUIRES_EXPLICIT_OPERATOR_FLAG",
        "CONTROLLED_KEEP_OUTPUT_CLEANUP_PASS",
        "NO_REPO_WRITE_DURING_DEMO",
        "NO_NETWORK_USED",
        "NO_DATABASE_USED",
        "NO_REAL_MEDIA_USED",
        "NO_PUBLIC_DEMO_CLAIM",
        "NO_CLIENT_READY_CLAIM",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_defines_strict_failure_handling() -> None:
    text = _doc()

    required_tokens = [
        "STOP_DO_NOT_IMPROVISE",
        "COMMAND_ENTRYPOINT_MISSING_STOPPED",
        "HELP_OUTPUT_UNEXPECTED_STOPPED",
        "JSON_EVIDENCE_FAILURE_STOPPED",
        "CONTROLLED_SHA256_MISMATCH_STOPPED",
        "CONTROLLED_BYTE_COUNT_MISMATCH_STOPPED",
        "KEEP_OUTPUT_CLEANUP_FAILURE_STOPPED",
        "WORKTREE_NOT_CLEAN_STOPPED",
        "BOUNDARY_VIOLATION_STOPPED",
        "A stopped demo is a better outcome than an inflated claim.",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_defines_cleanup_discipline() -> None:
    text = _doc()

    required_tokens = [
        "Temporary output root path",
        "manual cleanup",
        "CONTROLLED_KEEP_OUTPUT_CLEANUP_PASS",
        "Confirmation that the preserved output root no longer exists after manual cleanup.",
        "Confirmation that nothing was written inside the repository.",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_contains_approved_commercial_framing_without_hype() -> None:
    text = _doc()

    required_tokens = [
        "For a producer, productora, school, or potential client",
        "Esta demo no enseña todavía una herramienta lista para producción",
        "no por promesas",
        "For an internal technical reviewer",
        "For a film school",
        "OPERATOR_NO_HYPE_BOUNDARY_DEFINED",
    ]

    for token in required_tokens:
        assert token in text


def test_operator_runbook_gate_blocks_forbidden_product_claims() -> None:
    text = _doc()

    red_line_tokens = [
        "PRODUCTO_FINAL_LISTO",
        "DEMO_PUBLICA_LISTA",
        "CLIENTE_REAL_VALIDADO",
        "MATERIAL_REAL_PROCESADO",
        "SCANNER_REAL_IMPLEMENTADO",
        "FFPROBE_REAL_EJECUTADO",
        "FFMPEG_REAL_EJECUTADO",
        "SINCRONIZACION_IMPLEMENTADA",
        "TRANSCRIPCION_IMPLEMENTADA",
        "SUBTITULOS_IMPLEMENTADOS",
        "DAVINCI_EXPORT_IMPLEMENTADO",
        "SAAS_INTEGRADO",
        "DATABASE_INTEGRATED",
        "INSTALLER_LISTO",
        "LICENSING_LISTO",
        "READY_FOR_PAID_CUSTOMER_USE",
        "READY_FOR_PUBLIC_LAUNCH",
    ]

    for token in red_line_tokens:
        assert token in text


def test_operator_runbook_gate_forbidden_natural_language_claims_are_not_used_as_claims() -> None:
    text = _doc().lower()

    forbidden_claim_phrases = [
        "ya está listo para vender",
        "producto final ya disponible",
        "demo pública disponible",
        "cliente real ya validado",
        "material real ya procesado",
        "scanner real ya implementado",
        "ffprobe real ya ejecutado",
        "ffmpeg real ya ejecutado",
        "sincronización ya implementada",
        "transcripción ya implementada",
        "subtítulos ya implementados",
        "davinci export ya implementado",
        "saas ya integrado",
        "installer ya listo",
        "licensing ya listo",
    ]

    # The document may list these phrases only under the forbidden-claims section.
    forbidden_section = text.split("## forbidden product claims", maxsplit=1)[1]
    preceding_claim_area = text.split("## forbidden product claims", maxsplit=1)[0]

    for phrase in forbidden_claim_phrases:
        assert phrase in forbidden_section
        assert phrase not in preceding_claim_area


def test_operator_runbook_gate_contains_closeout_and_acceptance_criteria() -> None:
    text = _doc()

    required_tokens = [
        "Operator closeout",
        "OPERATOR_RUNBOOK_SEQUENCE_COMPLETED",
        "OPERATOR_EVIDENCE_CAPTURED",
        "OPERATOR_FAILURE_POLICY_DEFINED",
        "OPERATOR_CLEANUP_DISCIPLINE_DEFINED",
        "NOT_PUBLIC_DEMO",
        "NOT_CLIENT_READY",
        "NOT_PRODUCT_FINAL",
        "Gate acceptance criteria",
        "repo scope is limited to this document and its QA test",
        "PostgreSQL-only regression guard passes",
    ]

    for token in required_tokens:
        assert token in text
