from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_standalone_product_blueprint_v1.md"
)


def read_doc() -> str:
    return DOC.read_text(encoding="utf-8")


def test_blueprint_document_exists():
    assert DOC.exists()


def test_phase_identity_is_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1" in text
    assert "CID Local Media Agent — Standalone Product Blueprint v1" in text


def test_blueprint_is_documentation_and_test_only():
    text = read_doc()
    required = [
        "documentation/test-only",
        "does not implement application runtime",
        "does not implement scanner runtime",
        "does not implement SaaS integration",
        "does not implement installer logic",
        "does not implement licensing or activation logic",
        "does not execute ffprobe",
        "does not execute ffmpeg",
        "does not process client media",
        "does not upload video files",
        "does not upload audio files",
        "does not create payment flows",
    ]
    for item in required:
        assert item in text


def test_current_baseline_and_product_decision_are_recorded():
    text = read_doc()
    assert "38fde44" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.V1" in text
    assert "CID_LOCAL_MEDIA_AGENT_IS_A_STANDALONE_PRODUCT_INSIDE_CID" in text


def test_product_identity_is_standalone_inside_cid():
    text = read_doc()
    required = [
        "CID Local Media Agent",
        "CID — Cinematic Intelligence Direction",
        "local-first audiovisual media analysis and postproduction preparation tool",
        "standalone CID product",
        "individual product",
    ]
    for item in required:
        assert item in text


def test_relationship_with_cid_saas_is_optional_not_dependent():
    text = read_doc()
    required = [
        "related but not dependent",
        "works locally by default",
        "can produce local reports",
        "licensed as an individual product",
        "authorized metadata or reports to CID SaaS",
        "must never require CID SaaS to scan local material",
        "must never upload raw client video by default",
        "must never upload raw client audio by default",
        "must allow offline work under controlled license rules",
    ]
    for item in required:
        assert item in text


def test_product_promise_is_present_and_human_centered():
    text = read_doc()
    assert "analiza carpetas locales de material audiovisual sin subir vídeos ni audios a la nube" in text
    assert "radiografía técnica y editorial" in text
    assert "does not replace the editor" in text
    assert "post supervisor" in text
    assert "producer" in text


def test_target_users_are_defined():
    text = read_doc()
    users = [
        "editor",
        "assistant editor",
        "DIT",
        "postproduction supervisor",
        "sound editor",
        "documentary editor",
        "production company",
        "film school",
        "audiovisual training center",
        "producer",
        "director",
        "archive coordinator",
        "subtitle coordinator",
    ]
    for user in users:
        assert user in text


def test_core_use_cases_are_defined():
    text = read_doc()
    use_cases = [
        "Scan a local audiovisual folder",
        "Detect media-like files and production documents",
        "Build a safe inventory",
        "Extract or simulate technical metadata",
        "Identify warnings and review needs",
        "Group likely camera and sound candidates",
        "Prepare editor-friendly reports",
        "Prepare sound-friendly reports",
        "subtitle and transcription readiness notes",
        "DaVinci Resolve export readiness",
        "Keep all media local",
        "Export local JSON, Markdown, and HTML reports",
        "approved metadata with CID SaaS",
    ]
    for item in use_cases:
        assert item in text


def test_product_tiers_are_defined():
    text = read_doc()
    tiers = [
        "Demo tier",
        "Individual professional tier",
        "Studio or production company tier",
        "Education tier",
        "show product value",
        "per-seat licensing",
        "organization licensing",
        "institutional licensing",
    ]
    for tier in tiers:
        assert tier in text


def test_platform_support_and_packaging_are_defined():
    text = read_doc()
    required = [
        "Windows",
        "macOS",
        "Linux",
        "installer or package per platform",
        "dependency checks",
        "ffmpeg and ffprobe strategy",
        "local model strategy",
        "update strategy",
        "rollback strategy",
        "support diagnostics",
        "code signing or notarization",
    ]
    for item in required:
        assert item in text


def test_local_first_architecture_is_defined():
    text = read_doc()
    required = [
        "local project input",
        "local processing",
        "local reports",
        "local logs",
        "local configuration",
        "local cache",
        "redacted support bundle",
        "optional future CID SaaS connection",
        "Network access must be optional",
    ]
    for item in required:
        assert item in text


def test_privacy_requirements_are_explicit():
    text = read_doc()
    privacy = [
        "no video upload by default",
        "no audio upload by default",
        "no raw file upload by default",
        "no private path upload by default",
        "no client title upload by default",
        "no script content upload by default",
        "no dialogue upload by default",
        "no transcription upload by default",
        "no automatic cloud analysis by default",
        "safe labels and redaction by default",
        "customer authorization required before any sync",
    ]
    for item in privacy:
        assert item in text


def test_future_cid_saas_connection_principles_are_defined():
    text = read_doc()
    allowed = [
        "license status",
        "organization seats",
        "update entitlement",
        "customer-approved report upload",
        "customer-approved metadata upload",
        "support bundle upload after explicit approval",
        "project dashboard linking",
    ]
    blocked = [
        "raw video upload",
        "raw audio upload",
        "raw folder path upload",
        "raw filename upload",
        "raw transcription upload",
        "script upload",
        "dialogue upload",
        "automatic background media sync",
        "unapproved surveillance behavior",
    ]
    for item in allowed + blocked:
        assert item in text


def test_licensing_and_activation_direction_is_defined():
    text = read_doc()
    items = [
        "monthly subscription",
        "yearly subscription",
        "per-seat licensing",
        "organization licensing",
        "device activation",
        "device deactivation",
        "offline grace period",
        "license renewal",
        "license expiry behavior",
        "trial mode",
        "education mode",
        "studio mode",
        "anti-piracy protections without spyware or rootkit behavior",
    ]
    for item in items:
        assert item in text


def test_product_modules_are_defined():
    text = read_doc()
    modules = [
        "Local Scanner",
        "Technical Metadata",
        "Demo Report",
        "Editing Preparation",
        "Sound Preparation",
        "Subtitle and Transcription Preparation",
        "Export Preparation",
    ]
    for module in modules:
        assert module in text


def test_mvp_scope_is_defined_and_constrained():
    text = read_doc()
    included = [
        "local project input folder selection or CLI argument",
        "safe inventory",
        "synthetic or controlled metadata",
        "warning model",
        "review model",
        "suggested organization",
        "local JSON report",
        "local Markdown report",
        "local HTML report",
        "privacy statement",
        "limitations section",
        "no cloud media upload",
        "no file mutation",
    ]
    excluded = [
        "real waveform sync",
        "real transcription",
        "real subtitle translation",
        "real DaVinci timeline export",
        "real SaaS synchronization",
        "installer automation",
        "payment integration",
    ]
    for item in included + excluded:
        assert item in text


def test_commercial_demo_path_is_defined():
    text = read_doc()
    items = [
        "Synthetic End-to-End Local Demo Report",
        "10 synthetic media-like items",
        "safe technical metadata hints",
        "warning codes",
        "camera/audio candidate groups",
        "department review recommendations",
        "suggested folder organization",
        "local-only privacy confirmation",
        "human review requirements",
        "next recommended actions",
    ]
    for item in items:
        assert item in text


def test_roadmap_stages_are_defined():
    text = read_doc()
    stages = [
        "Stage 1 — Standalone product definition",
        "Stage 2 — Synthetic visible demo",
        "Stage 3 — Local scanner demo",
        "Stage 4 — Controlled ffprobe metadata",
        "Stage 5 — Editing intelligence",
        "Stage 6 — Speech and subtitles",
        "Stage 7 — Packaging and licensing",
        "Stage 8 — Private beta",
    ]
    for stage in stages:
        assert stage in text


def test_product_risks_and_mitigations_are_defined():
    text = read_doc()
    risks = [
        "Overbuilding contracts without visible demo",
        "Weakening local-only promise",
        "Trying to build full product before MVP",
        "Confusing demo with real media analysis",
        "Licensing complexity too early",
        "prioritize synthetic visible demo report",
        "require explicit authorization for SaaS sync",
        "defer sync, transcription, and installer automation",
    ]
    for risk in risks:
        assert risk in text


def test_non_goals_are_explicit():
    text = read_doc()
    non_goals = [
        "runtime code",
        "scanner changes",
        "report generation",
        "fixture JSON creation",
        "ffprobe execution",
        "ffmpeg execution",
        "transcription",
        "translation",
        "DaVinci export",
        "SaaS integration",
        "installer creation",
        "license server integration",
        "payment integration",
        "client media processing",
    ]
    for item in non_goals:
        assert item in text


def test_acceptance_criteria_are_complete():
    text = read_doc()
    criteria = [
        "CID Local Media Agent is defined as standalone product",
        "CID SaaS connection is optional and future-only",
        "local-first operation is mandatory",
        "video and audio uploads are prohibited by default",
        "product audience is defined",
        "MVP scope is defined",
        "packaging direction is defined",
        "licensing direction is defined",
        "privacy requirements are explicit",
        "product modules are defined",
        "roadmap is defined",
        "non-goals are explicit",
        "implementation remains blocked",
        "next phase remains gated",
    ]
    for criterion in criteria:
        assert criterion in text


def test_next_phase_and_return_to_demo_line_are_declared():
    text = read_doc()
    assert "CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.QA.GATE.V1" in text
    assert "CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.FIXTURE.CONTRACT.QA.GATE.V1" in text
    assert "built as a product demo" in text


def test_final_product_decision_is_clear():
    text = read_doc()
    assert "CID_LOCAL_MEDIA_AGENT_STANDALONE_PRODUCT_BLUEPRINT_READY_FOR_QA" in text
    assert "standalone local-first product within CID" in text
    assert "may connect to CID SaaS later with customer authorization" in text
    assert "must not depend on CID SaaS to work" in text
    assert "must not upload customer video or audio by default" in text


def test_test_file_does_not_import_external_command_modules():
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = [
        "import " + "sub" + "process",
        "from " + "sub" + "process",
        "import " + "o" + "s",
        "from " + "o" + "s",
        "P" + "open(",
        "shell" + "=",
    ]
    for item in forbidden:
        assert item not in source
