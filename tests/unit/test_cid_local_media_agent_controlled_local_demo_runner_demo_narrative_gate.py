from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_demo_narrative_gate_v1.md"
EVIDENCE_DOC_PATH = REPO_ROOT / "docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_operator_evidence_pack_gate_v1.md"
EVIDENCE_TEST_PATH = REPO_ROOT / "tests/unit/test_cid_local_media_agent_controlled_local_demo_runner_operator_evidence_pack_gate.py"

PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.NARRATIVE.GATE.V1"
)
PREVIOUS_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT."
    "VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED."
    "TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED."
    "CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.EVIDENCE.PACK.GATE.V1"
)
EXPECTED_RESULT = "LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_NARRATIVE_GATE_V1_CLOSED"
RECOMMENDED_TAG = "cid-dev-stable-local-media-agent-controlled-local-demo-runner-demo-narrative-gate-v1-20260630"
PREVIOUS_TAG = "cid-dev-stable-local-media-agent-controlled-local-demo-runner-operator-evidence-pack-gate-v1-20260630"
HEAD_COMMIT = "bf36b80c0eb945166bf62aa70aa28fffce4ce0f7"
RUNNER_COMMAND = "cid-local-media-agent-controlled-local-demo-runner"
EXPORT_COMMAND = "cid-local-media-agent-visible-report-write-enabled-export"
EXPECTED_STATUS = "CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED"
EXPECTED_BOUNDARY = "DEMO_TECNICA_LOCAL_CONTROLADA_ONLY"
EXPECTED_ARTIFACT_NAME = "controlled_visible_report.controlled.txt"
EXPECTED_ARTIFACT_SHA256 = "277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f"
EXPECTED_ARTIFACT_BYTES = "167"

REQUIRED_HEADINGS = [
    "Phase:",
    "Purpose:",
    "Baseline:",
    "Required previous evidence:",
    "Narrative goal:",
    "What to say first:",
    "Demo sequence:",
    "How to explain SHA and bytes:",
    "How to explain cleanup:",
    "Limits to repeat:",
    "What not to promise:",
    "Controlled demo versus final product:",
    "Anti-hype rule:",
    "Operator checklist:",
    "Closure requires:",
    "Expected result:",
]

REQUIRED_SEQUENCE = [
    f"1. Show command discovery with `{RUNNER_COMMAND} --help`.",
    "2. Explain that `--help` is the safe operator entry point and shows only `--result-json` and `--keep-output`.",
    f"3. Run `{RUNNER_COMMAND} --result-json`.",
    "4. Explain that the default JSON proves the demo can verify itself and clean the temporary output root automatically.",
    f"10. Run `{RUNNER_COMMAND} --result-json --keep-output` only when manual artifact inspection is needed.",
    "12. After inspection, remove the reported output root and confirm the artifact is gone.",
]

LIMIT_LINES = [
    "No client demo.",
    "No public demo.",
    "No sales demo.",
    "No production.",
    "No installer.",
    "No real media.",
    "No scanner.",
    "No ffprobe.",
    "No FFmpeg.",
    "No network.",
    "No SaaS.",
    "No database service.",
    "No repository write.",
    "No overwrite.",
    "No unattended execution.",
    "No pyproject change.",
    "No runner implementation change.",
    "No export command implementation change.",
]

FORBIDDEN_CLAIMS = [
    "customer-ready",
    "production-ready",
    "public demo approved",
    "client demo approved",
    "sales demo approved",
    "installer ready",
    "real footage supported",
    "real media supported",
    "scanner integration ready",
    "ffprobe execution ready",
    "ffmpeg execution ready",
    "saas upload ready",
    "timeline export ready",
    "subtitles ready",
    "transcription ready",
    "audio extraction ready",
    "security certified",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_contains_all(text: str, values: list[str]) -> None:
    for value in values:
        assert value in text


def test_demo_narrative_gate_doc_exists_and_declares_phase() -> None:
    assert DOC_PATH.exists()
    text = _read(DOC_PATH)

    assert PHASE in text
    assert EXPECTED_RESULT in text
    assert RECOMMENDED_TAG in text
    assert PREVIOUS_TAG in text
    assert HEAD_COMMIT in text


def test_demo_narrative_gate_has_required_sections() -> None:
    _assert_contains_all(_read(DOC_PATH), REQUIRED_HEADINGS)


def test_demo_narrative_gate_references_previous_evidence_artifacts() -> None:
    text = _read(DOC_PATH)

    assert EVIDENCE_DOC_PATH.exists()
    assert EVIDENCE_TEST_PATH.exists()
    assert str(EVIDENCE_DOC_PATH.relative_to(REPO_ROOT)) in text
    assert str(EVIDENCE_TEST_PATH.relative_to(REPO_ROOT)) in text
    assert PREVIOUS_PHASE in _read(EVIDENCE_DOC_PATH)


def test_demo_narrative_gate_freezes_command_identity_and_artifact_evidence() -> None:
    _assert_contains_all(_read(DOC_PATH), [
        RUNNER_COMMAND,
        EXPORT_COMMAND,
        EXPECTED_STATUS,
        EXPECTED_BOUNDARY,
        EXPECTED_ARTIFACT_NAME,
        EXPECTED_ARTIFACT_SHA256,
        f"Artifact bytes {EXPECTED_ARTIFACT_BYTES}",
    ])


def test_demo_narrative_gate_orders_help_json_and_keep_output() -> None:
    _assert_contains_all(_read(DOC_PATH), REQUIRED_SEQUENCE)


def test_demo_narrative_gate_explains_sha_bytes_and_cleanup_without_overclaiming() -> None:
    _assert_contains_all(_read(DOC_PATH), [
        "The SHA256 proves the bytes are exactly the same controlled text every time.",
        "The byte count is a simple cross-check that the artifact size did not drift.",
        "Do not describe the SHA as a watermark, signature, legal proof, content authenticity system, or customer delivery guarantee.",
        "Default `--result-json` removes the temporary output root after verification.",
        "Default JSON must show `output_root_removed true` and `artifact_available_after_runner false`.",
        "`--keep-output` must show `output_root_removed false` and `artifact_available_after_runner true`.",
        "The preserved path must be temporary, fixture-owned, and removed after inspection.",
        "The demo must not write inside the repository.",
    ])


def test_demo_narrative_gate_repeats_all_limits() -> None:
    _assert_contains_all(_read(DOC_PATH), LIMIT_LINES)


def test_demo_narrative_gate_declares_what_not_to_promise() -> None:
    _assert_contains_all(_read(DOC_PATH), [
        "Do not promise real footage ingestion.",
        "Do not promise scanner integration.",
        "Do not promise ffprobe or FFmpeg execution.",
        "Do not promise SaaS upload.",
        "Do not promise customer workspace integration.",
        "Do not promise installer packaging.",
        "Do not promise production monitoring.",
        "Do not promise timeline export.",
        "Do not promise subtitles, sync, transcription, or audio extraction.",
        "Do not promise security certification.",
        "Do not promise delivery dates.",
    ])


def test_demo_narrative_gate_separates_controlled_demo_from_final_product() -> None:
    _assert_contains_all(_read(DOC_PATH), [
        "Controlled demo means installed local commands, fixture-owned output roots, deterministic JSON, one controlled text artifact, automatic cleanup by default, and explicit manual cleanup when output is preserved.",
        "Final product still requires explicit future gates for packaging, installer, real operator onboarding, product support, customer data boundaries, deployment boundaries, and production release criteria.",
        "not yet; this is controlled local evidence that the internal command chain behaves safely and deterministically.",
        "not in this demo.",
        "only after a future explicit external-demo authorization gate.",
    ])


def test_demo_narrative_gate_contains_operator_checklist_and_closure_requirements() -> None:
    _assert_contains_all(_read(DOC_PATH), [
        "Confirm installed command path before presenting.",
        "Show `--help` before JSON.",
        "Show default JSON before `--keep-output`.",
        "Explain SHA256 and byte count together.",
        "Explain default cleanup before manual inspection.",
        "Clean preserved output roots after inspection.",
        "Close with limits and next gates, not with product-ready claims.",
        "demo narrative gate test PASS",
        "operator evidence pack gate test PASS",
        "WSL guard PASS",
        "database regression guard PASS",
        "only this demo narrative gate doc and test staged",
    ])


def test_demo_narrative_gate_avoids_forbidden_claims() -> None:
    text = _read(DOC_PATH).lower()

    for claim in FORBIDDEN_CLAIMS:
        assert claim not in text


def test_demo_narrative_gate_test_does_not_call_external_processes() -> None:
    source = _read(Path(__file__))

    assert "import " + "sub" + "process" not in source
    assert "from " + "sub" + "process" not in source
    assert "sub" + "process." not in source
    assert "import" + "lib" not in source
