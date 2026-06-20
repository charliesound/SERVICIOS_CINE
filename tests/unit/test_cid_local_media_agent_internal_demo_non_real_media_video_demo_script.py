from pathlib import Path

DOC = Path("docs/product/local_media_agent/cid_local_media_agent_internal_demo_non_real_media_video_demo_script_v1.md")


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def assert_all_present(content: str, items: list[str]) -> None:
    for item in items:
        assert item in content


def test_phase_and_acceptance_result() -> None:
    content = read_doc()
    assert_all_present(content, [
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.NON_REAL_MEDIA.VIDEO_DEMO.SCRIPT.V1",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_NON_REAL_MEDIA_VIDEO_DEMO_SCRIPT_PASS_READY_FOR_QA_GATE",
    ])


def test_source_stable_state_is_declared() -> None:
    content = read_doc()
    assert_all_present(content, [
        "1db15e4893f94e3ec86711f662b6116a8ab42990",
        "test: add CID Local Media Agent internal demo checklist summary QA gate",
        "cid-dev-stable-local-media-agent-internal-demo-second-machine-setup-internal-demo-checklist-summary-qa-gate-v1-20260620",
        "LOCAL_MEDIA_AGENT_INTERNAL_DEMO_SECOND_MACHINE_SETUP_INTERNAL_DEMO_CHECKLIST_SUMMARY_QA_GATE_PASS_CLOSED",
    ])


def test_demo_classification_blocks_external_use() -> None:
    content = read_doc()
    assert_all_present(content, [
        "internal-only",
        "non-real-media",
        "controlled explanation only",
        "not public",
        "not sales-ready",
        "not client-facing",
        "not installer-ready",
        "not production-ready",
    ])


def test_required_disclaimer_and_marker_are_present() -> None:
    content = read_doc()
    assert_all_present(content, [
        "CID Local Media Agent is currently internal-only, controlled-fixture-only, local-only in product intent, not client-facing, not public, not sales-ready, not production-ready, not installer-ready, and not authorized for real media processing.",
        "INTERNAL CONTROLLED DEMO ONLY - NO REAL MEDIA - NO CLIENT MATERIAL - NO INSTALLER - NO PUBLIC OR SALES DEMO",
    ])


def test_script_contains_safe_story_sections() -> None:
    content = read_doc()
    assert_all_present(content, [
        "Opening",
        "Problem",
        "Product Direction",
        "Current Safe Status",
        "What Can Be Shown",
        "What Must Not Be Shown",
        "Future Path",
        "Closing",
    ])


def test_allowed_demo_items_are_non_real_media_only() -> None:
    content = read_doc()
    assert_all_present(content, [
        "documentation",
        "tests",
        "closed tags",
        "controlled reports",
        "checklist summary",
        "product boundary map",
        "CLI explanation without processing real media",
    ])


def test_prohibited_work_remains_blocked() -> None:
    content = read_doc()
    assert_all_present(content, [
        "real footage",
        "client files",
        "confidential script material",
        "real folder selection",
        "scanner execution on real media",
        "media probing on real files",
        "FFmpeg execution on real files",
        "sync generation",
        "transcription generation",
        "subtitle generation",
        "timeline export",
        "installer creation",
        "client installation",
        "SaaS upload",
        "database writes",
    ])


def test_future_path_requires_separate_gates() -> None:
    content = read_doc()
    assert_all_present(content, [
        "Before any real-folder or real-media use, a separate authorization gate must be closed.",
        "Before installer work, a separate installer readiness gate and installer build authorization gate must be closed.",
        "CID.LOCAL_MEDIA_AGENT.INTERNAL.DEMO.NON_REAL_MEDIA.VIDEO_DEMO.SCRIPT.QA.GATE.V1",
    ])
