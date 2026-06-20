from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.local_media_agent import visible_report_runtime_cli as cli


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_cli_module_is_import_safe() -> None:
    assert callable(cli.main)
    assert "--scan" in cli.FORBIDDEN_FLAGS
    assert "--database-write" in cli.FORBIDDEN_FLAGS


def test_missing_required_arguments_return_non_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = cli.main([])

    captured = capsys.readouterr()
    assert code != 0
    assert "ERROR:" in captured.err
    assert "scanner-result-json" in captured.err


def test_forbidden_flag_is_rejected_before_file_loading(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "out"

    code = cli.main(
        [
            "--scan",
            "--scanner-result-json",
            str(tmp_path / "missing.json"),
            "--output-root",
            str(output_root),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "unsupported flag" in captured.err
    assert "--scan" in captured.err


@pytest.mark.parametrize(
    "raw_path, expected",
    [
        ("https://example.test/input.json", "URL-like"),
        ("C:\\media\\input.json", "Windows drive"),
        ("\\\\server\\share\\input.json", "UNC"),
        ("/mnt/c/input.json", "mounted Windows"),
    ],
)
def test_unsafe_input_paths_are_rejected(
    tmp_path: Path,
    raw_path: str,
    expected: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = cli.main(
        [
            "--scanner-result-json",
            raw_path,
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert expected in captured.err


def test_repository_input_path_is_rejected(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    code = cli.main(
        [
            "--scanner-result-json",
            "pyproject.toml",
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "repository" in captured.err


def test_missing_json_file_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = cli.main(
        [
            "--scanner-result-json",
            str(tmp_path / "missing.json"),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "does not exist" in captured.err


def test_directory_json_path_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_dir = tmp_path / "input_dir"
    input_dir.mkdir()

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_dir),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "not a directory" in captured.err


def test_invalid_json_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_json = tmp_path / "scanner_result.json"
    input_json.write_text("{invalid json", encoding="utf-8")

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "invalid" in captured.err


def test_json_root_must_be_object(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", ["not", "object"])

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "root must be an object" in captured.err


def test_unsafe_output_root_is_rejected(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"ok": True})

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            "/mnt/c/out",
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "mounted Windows" in captured.err


def test_success_delegates_to_runtime_renderer_and_prints_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_json = _write_json(
        tmp_path / "scanner_result.json",
        {"project": "controlled", "warnings": ["visible"]},
    )
    output_root = tmp_path / "out"
    calls: list[tuple[dict[str, object], Path]] = []

    def fake_generate_visible_report(scanner_result: dict[str, object], root: Path) -> Path:
        calls.append((scanner_result, root))
        report = root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text("# controlled report\n", encoding="utf-8")
        return report

    monkeypatch.setattr(cli, "generate_visible_report", fake_generate_visible_report)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ]
    )

    captured = capsys.readouterr()
    expected_report = output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"

    assert code == 0
    assert calls == [({"project": "controlled", "warnings": ["visible"]}, output_root.resolve())]
    assert expected_report.exists()
    assert str(expected_report) in captured.out


def test_dry_run_validates_json_but_does_not_render(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"ok": True})
    output_root = tmp_path / "out"

    def fail_if_called(scanner_result: dict[str, object], root: Path) -> Path:
        raise AssertionError("renderer must not be called during dry-run")

    monkeypatch.setattr(cli, "generate_visible_report", fail_if_called)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--dry-run",
            "--strict",
        ]
    )

    assert code == 0
    assert not (output_root / "05_reports").exists()


def test_runtime_validation_error_is_propagated_without_success(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"bad": True})
    output_root = tmp_path / "out"

    def fail_runtime(scanner_result: dict[str, object], root: Path) -> Path:
        raise ValueError("runtime validation failed")

    monkeypatch.setattr(cli, "generate_visible_report", fail_runtime)

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "runtime validation failed" in captured.err
    assert captured.out == ""
    assert not (output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md").exists()


def test_unknown_scope_creep_flag_is_rejected_by_parser(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    input_json = _write_json(tmp_path / "scanner_result.json", {"ok": True})

    code = cli.main(
        [
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(tmp_path / "out"),
            "--make-subtitles",
        ]
    )

    captured = capsys.readouterr()
    assert code != 0
    assert "unrecognized arguments" in captured.err



def test_cli_can_run_as_direct_script_from_repo_root(tmp_path: Path) -> None:
    from tests.unit.test_cid_local_media_agent_visible_report_runtime_generator import (
        _valid_scanner_result,
    )

    input_json = _write_json(
        tmp_path / "scanner_result.json",
        _valid_scanner_result(),
    )
    output_root = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/local_media_agent/visible_report_runtime_cli.py",
            "--scanner-result-json",
            str(input_json),
            "--output-root",
            str(output_root),
            "--print-output-path",
        ],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        check=False,
    )

    expected_report = output_root / "05_reports" / "cid_local_media_agent_visible_report_v1.md"

    assert result.returncode == 0, result.stderr
    assert expected_report.exists()
    assert str(expected_report) in result.stdout
    assert "ModuleNotFoundError" not in result.stderr
