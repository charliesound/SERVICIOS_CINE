import importlib.util
import json
from pathlib import Path


SCRIPT = Path("scripts/cid_media_agent_scan.py")
DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_scanner_cli_ffprobe_availability_preflight_v1.md"
)
FIXTURES = Path("tests/fixtures/local_media_agent/scanner_cli")


def _load_module():
    spec = importlib.util.spec_from_file_location("cid_media_agent_scan", SCRIPT)
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
    return module, module.scan(args)


def test_ffprobe_availability_preflight_doc_declares_scope_and_no_goals():
    text = DOC.read_text(encoding="utf-8")
    assert "CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.FFPROBE.AVAILABILITY.PREFLIGHT.V1" in text
    assert "--ffprobe-preflight" in text
    assert "must not run `ffprobe` against media files yet" in text
    assert "This phase does not implement media probing." in text
    assert "This phase does not call `ffprobe` on any media file." in text
    assert "This phase does not call `ffmpeg`." in text
    assert "does not touch SaaS runtime" in text
    assert "DB, models, Alembic, Docker, frontend, Stripe, AI Jobs, credits or ledger" in text


def test_scanner_exposes_explicit_ffprobe_preflight_flag():
    module = _load_module()
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        "input",
        "--output-root",
        "output",
        "--ffprobe-preflight",
    ])
    assert args.ffprobe_preflight is True


def test_default_scan_skips_ffprobe_preflight_and_preserves_baseline(tmp_path):
    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"

    _module, (exit_code, summary) = _run_scan(input_root, output_root)

    assert exit_code == 0
    assert summary["status"] == "completed"
    assert summary["ffprobe_preflight"] == {
        "requested": False,
        "status": "skipped",
        "available": None,
        "warning_code": None,
    }
    assert summary["warnings"] == []


def test_missing_ffprobe_returns_controlled_warning_without_traceback(tmp_path):
    module = _load_module()
    module.shutil.which = lambda name: None

    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--ffprobe-preflight",
        "--dry-run",
    ])

    exit_code, summary = module.scan(args)

    assert exit_code == 1
    assert summary["status"] == "completed_with_warnings"
    assert summary["ffprobe_preflight"]["requested"] is True
    assert summary["ffprobe_preflight"]["status"] == "missing"
    assert summary["ffprobe_preflight"]["available"] is False
    assert summary["ffprobe_preflight"]["warning_code"] == "ffprobe_missing"
    assert summary["warnings"] == ["ffprobe_missing"]


def test_available_ffprobe_does_not_expose_executable_path(tmp_path):
    module = _load_module()
    module.shutil.which = lambda name: "/usr/bin/ffprobe" if name == "ffprobe" else None

    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--ffprobe-preflight",
        "--dry-run",
    ])

    exit_code, summary = module.scan(args)
    serialized = json.dumps(summary, sort_keys=True)

    assert exit_code == 0
    assert summary["ffprobe_preflight"]["status"] == "available"
    assert summary["ffprobe_preflight"]["available"] is True
    assert summary["ffprobe_preflight"]["warning_code"] is None
    assert "/usr/bin/ffprobe" not in serialized


def test_ffprobe_preflight_checks_only_executable_name_not_media_paths(tmp_path):
    calls = []
    module = _load_module()

    def fake_which(name: str):
        calls.append(name)
        return None

    module.shutil.which = fake_which

    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--ffprobe-preflight",
        "--dry-run",
    ])

    module.scan(args)

    assert calls == ["ffprobe"]


def test_ffprobe_preflight_does_not_add_technical_metadata(tmp_path):
    module = _load_module()
    module.shutil.which = lambda name: None

    input_root = FIXTURES / "simple_camera_only/input"
    output_root = tmp_path / "out"
    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--ffprobe-preflight",
    ])

    exit_code, summary = module.scan(args)

    assert exit_code == 1
    assert summary["ffprobe_preflight"]["warning_code"] == "ffprobe_missing"

    catalog = json.loads((output_root / "01_media_catalog/media_catalog.json").read_text())
    asset = catalog["assets"][0]
    assert asset["technical_metadata"] == {}
    assert "duration_seconds" not in json.dumps(asset)
    assert "codec" not in json.dumps(asset).lower()
    assert "stream" not in json.dumps(asset).lower()


def test_ffprobe_preflight_outputs_do_not_leak_input_output_or_executable_paths(tmp_path):
    module = _load_module()
    module.shutil.which = lambda name: "/private/local/bin/ffprobe" if name == "ffprobe" else None

    input_root = tmp_path / "input with private name"
    media_file = input_root / "DIA 01" / "CAM A" / "SC001_PRIVATE_PLACEHOLDER.mov"
    media_file.parent.mkdir(parents=True)
    media_file.write_text("CID_LOCAL_MEDIA_AGENT_SYNTHETIC_PLACEHOLDER_NOT_MEDIA\n", encoding="utf-8")
    output_root = tmp_path / "output with private name"

    parser = module.build_parser()
    args = parser.parse_args([
        "--input-root",
        str(input_root),
        "--output-root",
        str(output_root),
        "--ffprobe-preflight",
    ])

    exit_code, summary = module.scan(args)
    output_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in output_root.rglob("*")
        if path.is_file()
    )
    serialized = json.dumps(summary, sort_keys=True) + "\n" + output_text

    assert exit_code == 0
    assert str(input_root.resolve()) not in serialized
    assert str(output_root.resolve()) not in serialized
    assert "/private/local/bin/ffprobe" not in serialized
    assert "INPUT_ROOT/" in serialized


def test_scanner_does_not_introduce_subprocess_or_ffmpeg_runtime():
    text = SCRIPT.read_text(encoding="utf-8").lower()
    assert "subprocess" not in text
    assert "ffmpeg" not in text
    assert "duration_seconds" not in text
    assert "format_name" not in text
    assert "codec_type" not in text
    assert "streams" not in text
