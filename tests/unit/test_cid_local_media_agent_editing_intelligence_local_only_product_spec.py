from pathlib import Path


DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_editing_intelligence_local_only_product_spec_v1.md"
)


def _read_doc() -> str:
    assert DOC.exists(), f"Missing expected product spec: {DOC}"
    return DOC.read_text(encoding="utf-8")


def test_spec_declares_phase_and_scope():
    text = _read_doc()

    assert "CID.LOCAL_MEDIA_AGENT.EDITING_INTELLIGENCE.LOCAL_ONLY.PRODUCT.SPEC.V1" in text
    assert "This phase is product/specification only" in text
    assert "does not implement" in text
    assert "CID Local Media Agent" in text
    assert "CID Editing Intelligence" in text


def test_spec_enforces_media_never_leaves_client_system():
    text = _read_doc()

    required = [
        "media never leaves the client system",
        "original camera media",
        "original sound files",
        "videos",
        "audios",
        "proxies",
        "source transcripts, unless explicitly authorized",
        "original audiovisual media remains local",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_requires_cross_platform_installation_and_dependency_checks():
    text = _read_doc()

    required = [
        "Windows",
        "macOS",
        "Linux",
        "FFmpeg",
        "ffprobe",
        "DaVinci Resolve",
        "preflight check",
        "must not require the client to manually install Python",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_defines_local_scan_and_sync_order():
    text = _read_doc()

    required = [
        "Local scan requirements",
        "timecode",
        "scene/take/roll/name metadata",
        "waveform",
        "clap/slate detection",
        "manual review",
        "The system must never pretend that an uncertain sync is final",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_requires_multilingual_transcription_and_spanish_subtitles():
    text = _read_doc()

    required = [
        "Multilingual transcription",
        "detect language per clip, segment, or speaker",
        "preserve original-language transcript",
        "Spanish translated subtitles",
        "Spanish translated working subtitles",
        "original-language subtitles",
        "human validation",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_defines_davinci_rough_cut_as_assist_not_final_edit():
    text = _read_doc()

    required = [
        "DaVinci Resolve rough-cut package",
        "Spanish `.srt` subtitles",
        "marker CSV",
        "OpenTimelineIO timeline",
        "selects timeline / rough-cut assist",
        "It does not replace the editor",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_defines_organization_seat_license_and_antipiracy_limits():
    text = _read_doc()

    required = [
        "monthly subscription",
        "yearly subscription",
        "organization account",
        "named users",
        "device activation limit",
        "offline grace period",
        "Anti-piracy requirements",
        "Forbidden protections",
        "spyware behavior",
        "rootkit behavior",
        "copying client media",
        "uploading client media",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_tracks_ilok_pace_as_feasibility_not_implementation():
    text = _read_doc()

    required = [
        "iLok/PACE feasibility",
        "iLok USB hardware key",
        "iLok Cloud",
        "computer activation",
        "This phase does not implement iLok/PACE",
        "must not compromise the local-only media policy",
    ]

    for phrase in required:
        assert phrase in text


def test_spec_has_explicit_non_goals_to_protect_current_cid_runtime():
    text = _read_doc()

    forbidden_runtime_targets = [
        "touch database models",
        "touch Alembic",
        "touch Docker",
        "touch `.env`",
        "touch frontend",
        "commit or tag code",
    ]

    for phrase in forbidden_runtime_targets:
        assert phrase in text

def test_spec_enforces_local_media_agent_phase_isolation_from_saas():
    text = _read_doc()

    required = [
        "Local Media Agent phase isolation",
        "must remain separated by explicit phases",
        "must not touch CID SaaS runtime",
        "backend routes",
        "database models",
        "Alembic migrations",
        "Docker configuration",
        "frontend code",
        "Stripe/payment code",
        "AI Jobs runtime",
        "credits",
        "ledger",
        "workers",
        "until a future phase explicitly authorizes SaaS integration",
    ]

    for phrase in required:
        assert phrase in text
