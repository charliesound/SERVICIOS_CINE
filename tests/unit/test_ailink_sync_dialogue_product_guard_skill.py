from pathlib import Path


SKILL_DIR = Path(".agents/skills/ailink-sync-dialogue-product-guard")
SKILL_PATH = SKILL_DIR / "SKILL.md"
SKILLS_ROOT = Path(".agents/skills")


def _skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def test_ailink_sync_dialogue_product_guard_skill_exists():
    assert SKILL_PATH.exists()
    assert "AILink Sync Dialogue Product Guard" in _skill()


def test_ailink_sync_dialogue_product_guard_has_front_matter():
    text = _skill()
    assert text.startswith("---\n")
    assert "name: ailink-sync-dialogue-product-guard" in text
    assert "description:" in text
    assert "\n---\n\n# AILink Sync Dialogue Product Guard" in text


def test_ailink_sync_dialogue_product_guard_product_boundaries():
    text = _skill()
    required = [
        "AILink Sync Dialogue",
        "local-first",
        "beta/demo controlada",
        "not a final product",
        "AILink Sync Dialogue is an independent tool, not CID SaaS",
        "does not turn AILink Sync Dialogue into proof of CID SaaS maturity",
        "Future integration inside CID",
        "Integral SaaS CID",
        "CID — Cinematic Intelligence Direction",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_claim_prohibitions():
    text = _skill()
    required = [
        "Do not promise:",
        "Final automatic synchronization",
        "Final automatic editing",
        "Real DaVinci/Avid/Premiere integration when it is not implemented",
        "Cloud processing",
        "Production public release",
        "Keep commercial claims prudent and evidence-based",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_privacy_and_no_cloud():
    text = _skill()
    required = [
        "Preserve privacy by default",
        "Do not upload real audiovisual material",
        "Do not promise cloud processing",
        "customer footage to leave the customer's local environment",
        "private footage, paths, exports, metadata dumps",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_allowed_scope_and_no_goals():
    text = _skill()
    required = [
        "Documentation",
        "Demo material",
        "Reports",
        "Scanner behavior",
        "Matching behavior",
        "Exports",
        "Tests for AILink Sync Dialogue",
        "require explicit no-goals",
        "allowed files",
        "validation commands",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_sensitive_area_separation():
    text = _skill()
    required = [
        "Do not mix AILink Sync Dialogue with:",
        "CRM",
        "Payments",
        "Public landing activation",
        "Productive VPS",
        "CID backend runtime",
        "does not authorize changes to backend runtime",
        "frontend runtime",
        "Docker",
        "Alembic",
        ".env",
        "models",
        "DB",
        "payments",
        "configuration",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_review_discipline():
    text = _skill()
    required = [
        "recommend OpenCode or another independent reviewer as an external auditor",
        "The auditor reviews claims, demo pública, and product risks",
        "the auditor does not need to edit the repo",
        "commercial claims",
        "demo-public wording",
        "Maintain the operating rule: un agente escribe, otro audita",
    ]

    for phrase in required:
        assert phrase in text


def test_ailink_sync_dialogue_product_guard_does_not_authorize_forbidden_work():
    text = _skill().lower()
    forbidden_authorizations = [
        "authorizes backend runtime",
        "authorizes frontend runtime",
        "authorizes docker",
        "authorizes alembic",
        "authorizes .env",
        "authorizes models",
        "authorizes db",
        "authorizes payments",
        "authorizes configuration",
        "autoriza tocar backend",
        "autoriza tocar frontend",
        "autoriza tocar docker",
        "autoriza tocar alembic",
        "autoriza tocar .env",
        "autoriza tocar modelos",
        "autoriza tocar db",
        "autoriza tocar pagos",
        "autoriza tocar configuración",
    ]

    for phrase in forbidden_authorizations:
        assert phrase not in text


def test_no_other_sync_dialogue_skill_created_by_this_phase():
    assert SKILL_PATH.exists()

    sync_dialogue_skill_dirs = [
        path
        for path in SKILLS_ROOT.iterdir()
        if path.is_dir()
        and (
            "sync-dialogue" in path.name
            or "sync_dialogue" in path.name
            or path.name.startswith("ailink-sync")
        )
    ]

    assert sync_dialogue_skill_dirs == [SKILL_DIR]

    unexpected_skill_dirs = [
        path
        for path in sync_dialogue_skill_dirs
        if path != SKILL_DIR
    ]
    assert unexpected_skill_dirs == []
    assert "Future AILink Sync Dialogue skills require their own explicit phase" in _skill()
