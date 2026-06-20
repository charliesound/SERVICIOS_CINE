import importlib.util
import json
from pathlib import Path


SCRIPT = Path("scripts/cid_media_agent_scan.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_bounded_implementation_v1.md"
)
AUTH_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_"
    "product_semantics_implementation_authorization_gate_v1.md"
)

PHASE = "CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.PRODUCT.SEMANTICS.BOUNDED.IMPLEMENTATION.V1"


def _load_module():
    spec = importlib.util.spec_from_file_location("cid_media_agent_scan_bounded_semantics", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_scan(input_root: Path, output_root: Path, *extra: str):
    module = _load_module()
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        *extra,
    ])
    return module.scan(args)


def _make_second_controlled_shape(root: Path) -> None:
    (root / "camera").mkdir(parents=True)
    (root / "sound").mkdir(parents=True)
    (root / "non_media").mkdir(parents=True)
    (root / "camera" / "A001_SC001_TK001.mov").write_text("placeholder", encoding="utf-8")
    (root / "sound" / "A001_SC001_TK001.wav").write_text("placeholder", encoding="utf-8")
    (root / "non_media" / "notes.txt").write_text("placeholder", encoding="utf-8")
    (root / "non_media" / "tool.exe").write_text("placeholder", encoding="utf-8")


def test_doc_exists_and_names_phase():
    text = DOC.read_text(encoding="utf-8")
    assert PHASE in text
    assert "Product Semantics Bounded Implementation v1" in text


def test_prior_authorization_gate_is_present():
    doc_text = DOC.read_text(encoding="utf-8")
    auth_text = AUTH_DOC.read_text(encoding="utf-8")
    assert "PRODUCT.SEMANTICS.IMPLEMENTATION.AUTHORIZATION.GATE.V1" in doc_text
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_AUTHORIZATION_GATE_PASS_SEPARATE_BOUNDED_IMPLEMENTATION_PHASE_AUTHORIZED" in doc_text
    assert "PRODUCT_SEMANTICS_IMPLEMENTATION_AUTHORIZATION_GATE_PASS_SEPARATE_BOUNDED_IMPLEMENTATION_PHASE_AUTHORIZED" in auth_text


def test_script_defines_non_media_rejected_extensions():
    source = SCRIPT.read_text(encoding="utf-8")
    assert 'NON_MEDIA_REJECTED_EXTENSIONS = {".txt", ".exe"}' in source
    assert 'REPORT_EXTENSIONS = {".json", ".csv"}' in source


def test_dry_run_reports_non_media_rejected_counts_without_outputs(tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    _make_second_controlled_shape(input_root)

    exit_code, summary = _run_scan(input_root, output_root, "--dry-run")

    assert exit_code == 0
    assert summary["candidate_media_count"] == 2
    assert summary["accepted_extension_counts"] == {".mov": 1, ".wav": 1}
    assert summary["rejected_extension_counts"] == {".exe": 1, ".txt": 1}
    assert summary["ignored_extension_counts"] == {}
    assert summary["created_outputs"] == []
    assert not output_root.exists()


def test_written_processing_status_preserves_semantic_counts(tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    _make_second_controlled_shape(input_root)

    exit_code, summary = _run_scan(input_root, output_root)

    assert exit_code == 0
    assert summary["candidate_media_count"] == 2
    assert summary["accepted_extension_counts"] == {".mov": 1, ".wav": 1}
    assert summary["rejected_extension_counts"] == {".exe": 1, ".txt": 1}
    assert summary["ignored_extension_counts"] == {}

    status = json.loads((output_root / "00_project/processing_status.json").read_text())
    assert status["accepted_extension_counts"] == {".mov": 1, ".wav": 1}
    assert status["rejected_extension_counts"] == {".exe": 1, ".txt": 1}
    assert status["ignored_extension_counts"] == {}


def test_media_catalog_excludes_rejected_non_media_files(tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    _make_second_controlled_shape(input_root)

    exit_code, _summary = _run_scan(input_root, output_root)

    assert exit_code == 0
    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    extensions = {asset["extension"] for asset in catalog["assets"]}
    file_names = {asset["file_name"] for asset in catalog["assets"]}

    assert extensions == {".mov", ".wav"}
    assert "notes.txt" not in file_names
    assert "tool.exe" not in file_names


def test_implementation_does_not_emit_client_facing_or_clean_pass_claims():
    source = SCRIPT.read_text(encoding="utf-8").lower()
    assert "clean classification pass" not in source
    assert "client-facing classification" not in source


def test_implementation_does_not_introduce_forbidden_runtime_dependencies():
    source = SCRIPT.read_text(encoding="utf-8").lower()

    for forbidden in [
        "subprocess",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "sqlalchemy",
        "alembic",
        "stripe",
        "ffmpeg",
        "fastapi",
        "docker",
    ]:
        assert forbidden not in source


def test_ffprobe_remains_preflight_only_and_not_required_by_default(tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    _make_second_controlled_shape(input_root)

    exit_code, summary = _run_scan(input_root, output_root, "--dry-run")

    assert exit_code == 0
    assert summary["ffprobe_preflight"]["requested"] is False
    assert summary["ffprobe_preflight"]["status"] == "skipped"

def test_unknown_synthetic_placeholder_txt_still_requires_human_review(tmp_path):
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    (input_root / "UNKNOWN").mkdir(parents=True)
    (input_root / "UNKNOWN" / "UNKNOWN_ASSET.txt").write_text("placeholder", encoding="utf-8")

    exit_code, summary = _run_scan(input_root, output_root, "--dry-run")

    assert exit_code == 1
    assert summary["candidate_media_count"] == 1
    assert summary["human_review_required_count"] == 1
    assert summary["warnings"] == ["unknown synthetic placeholder"]
    assert summary["rejected_extension_counts"] == {".txt": 1}
    assert summary["ignored_extension_counts"] == {}
