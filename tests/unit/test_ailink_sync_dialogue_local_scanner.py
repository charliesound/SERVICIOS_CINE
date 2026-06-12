from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ailink_tools.sync_dialogue import local_scanner
from ailink_tools.sync_dialogue.local_scanner import scan_folder


def _touch(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_detects_supported_video_extensions(tmp_path: Path) -> None:
    _touch(tmp_path / "a.mov")
    _touch(tmp_path / "b.mp4")
    _touch(tmp_path / "c.mxf")

    result = scan_folder(tmp_path, probe=False)

    assert result.video_count == 3
    assert {media_file.extension for media_file in result.media_files} == {
        ".mov",
        ".mp4",
        ".mxf",
    }
    assert all(media_file.kind == "video" for media_file in result.media_files)


def test_detects_supported_audio_extensions(tmp_path: Path) -> None:
    _touch(tmp_path / "a.wav")
    _touch(tmp_path / "b.bwf")
    _touch(tmp_path / "c.mp3")

    result = scan_folder(tmp_path, probe=False)

    assert result.audio_count == 3
    assert {media_file.extension for media_file in result.media_files} == {
        ".wav",
        ".bwf",
        ".mp3",
    }
    assert all(media_file.kind == "audio" for media_file in result.media_files)


def test_unsupported_extensions_are_counted_not_classified_as_media(tmp_path: Path) -> None:
    _touch(tmp_path / "clip.mov")
    _touch(tmp_path / "notes.txt")
    _touch(tmp_path / "image.jpg")

    result = scan_folder(tmp_path, probe=False)

    assert result.total_files == 3
    assert result.video_count == 1
    assert result.unsupported_count == 2
    assert [media_file.filename for media_file in result.media_files] == ["clip.mov"]


def test_scans_recursively_and_uses_posix_relative_path(tmp_path: Path) -> None:
    _touch(tmp_path / "day01" / "cam_a" / "clip.mov")

    result = scan_folder(tmp_path, probe=False)

    assert result.media_files[0].relative_path == "day01/cam_a/clip.mov"


def test_size_bytes_matches_file_size(tmp_path: Path) -> None:
    _touch(tmp_path / "clip.mov", b"12345")


    result = scan_folder(tmp_path, probe=False)

    assert result.media_files[0].size_bytes == 5


def test_scan_does_not_modify_files(tmp_path: Path) -> None:
    media_path = _touch(tmp_path / "clip.mov", b"original")
    before = media_path.read_bytes()

    scan_folder(tmp_path, probe=False)

    assert media_path.read_bytes() == before


def test_hidden_and_temp_files_are_ignored(tmp_path: Path) -> None:
    _touch(tmp_path / ".hidden.mov")
    _touch(tmp_path / ".hidden_dir" / "clip.mov")
    _touch(tmp_path / "clip.mov.tmp")
    _touch(tmp_path / "~$clip.mov")
    _touch(tmp_path / "visible.mov")

    result = scan_folder(tmp_path, probe=False)

    assert result.total_files == 1
    assert [media_file.filename for media_file in result.media_files] == ["visible.mov"]


def test_no_probe_marks_supported_media_not_run(tmp_path: Path) -> None:
    _touch(tmp_path / "clip.mov")
    _touch(tmp_path / "sound.wav")

    result = scan_folder(tmp_path, probe=False)

    assert {media_file.probe_status for media_file in result.media_files} == {"not_run"}


def test_ffprobe_missing_marks_supported_media_without_failing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch(tmp_path / "clip.mov")
    monkeypatch.setattr(local_scanner.shutil, "which", lambda name: None)

    result = scan_folder(tmp_path, probe=True)

    assert result.media_files[0].probe_status == "ffprobe_missing"
    assert result.media_files[0].duration_seconds is None


def test_ffprobe_ok_parses_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _touch(tmp_path / "clip.mov")
    payload = {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "prores",
                "duration": "12.5",
                "avg_frame_rate": "24000/1001",
                "tags": {"timecode": "01:00:00:00"},
            },
            {"codec_type": "audio", "codec_name": "pcm_s24le", "channels": 2},
        ],
        "format": {"format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
    }

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(local_scanner.shutil, "which", lambda name: "/usr/bin/ffprobe")
    monkeypatch.setattr(local_scanner.subprocess, "run", fake_run)

    result = scan_folder(tmp_path, probe=True)
    media_file = result.media_files[0]

    assert media_file.probe_status == "ok"
    assert media_file.duration_seconds == 12.5
    assert media_file.timecode == "01:00:00:00"
    assert round(media_file.fps or 0, 3) == 23.976
    assert media_file.audio_channels == 2
    assert media_file.codec_name == "prores"
    assert media_file.format_name == "mov,mp4,m4a,3gp,3g2,mj2"


def test_ffprobe_failed_marks_file_failed_and_continues(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch(tmp_path / "bad.mov")
    _touch(tmp_path / "good.wav")
    calls = iter([1, 0])

    def fake_run(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
        returncode = next(calls)
        if returncode:
            return subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="bad media")
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=json.dumps({"streams": [{"codec_type": "audio", "channels": 1}]}),
            stderr="",
        )

    monkeypatch.setattr(local_scanner.shutil, "which", lambda name: "/usr/bin/ffprobe")
    monkeypatch.setattr(local_scanner.subprocess, "run", fake_run)

    result = scan_folder(tmp_path, probe=True)

    assert [media_file.probe_status for media_file in result.media_files] == ["failed", "ok"]
    assert result.media_files[0].error_message == "bad media"


def test_invalid_input_path_raises_value_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        scan_folder(tmp_path / "missing", probe=False)


def test_file_input_path_raises_value_error(tmp_path: Path) -> None:
    media_path = _touch(tmp_path / "clip.mov")
    with pytest.raises(ValueError, match="must be a directory"):
        scan_folder(media_path, probe=False)
