from pathlib import Path


SKILLS = {
    "cid-phase-guard": [
        "Required phase structure",
        "Default forbidden areas",
        "Final response requirements",
    ],
    "cid-docs-contract-phase": [
        "Documentation phases must not modify runtime behavior",
        "Document requirements",
        "Test requirements",
    ],
    "cid-release-checklist": [
        "Manual commit discipline",
        "Pre-commit inspection",
        "Final closing report",
    ],
}


def _skill_path(skill_name: str) -> Path:
    return Path(".agents") / "skills" / skill_name / "SKILL.md"


def test_codex_skills_base_files_exist_with_front_matter():
    for skill_name in SKILLS:
        path = _skill_path(skill_name)
        assert path.exists(), f"missing Codex skill: {path}"

        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert f"name: {skill_name}" in text
        assert "description:" in text
        assert "\n---\n\n# " in text


def test_codex_skills_base_contains_required_operational_contracts():
    for skill_name, required_phrases in SKILLS.items():
        text = _skill_path(skill_name).read_text(encoding="utf-8")

        for phrase in required_phrases:
            assert phrase in text, f"{skill_name} is missing required phrase: {phrase}"


def test_codex_skills_base_avoids_accidental_shell_artifacts():
    forbidden_fragments = [
        "EOF",
        "PYint",
        "EOFlain",
        "^C",
    ]

    for skill_name in SKILLS:
        text = _skill_path(skill_name).read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            assert fragment not in text, f"{skill_name} contains shell artifact: {fragment}"


def test_codex_skills_base_does_not_authorize_unsafe_changes_by_default():
    unsafe_authorizations = [
                        "modify .env",
        "edit .env",
        "run Docker",
        "create Alembic migration",
    ]

    for skill_name in SKILLS:
        text = _skill_path(skill_name).read_text(encoding="utf-8").lower()
        for fragment in unsafe_authorizations:
            assert fragment.lower() not in text, (
                f"{skill_name} appears to authorize unsafe default behavior: {fragment}"
            )
