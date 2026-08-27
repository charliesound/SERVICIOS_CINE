"""Unit tests for the WSL -> Windows ffprobe path adaptation bridge.

Covers the execution-time translation that lets the approved Windows
ffprobe.exe read /mnt/<drive>/... media from WSL, while leaving POSIX
paths (Linux ffprobe), non-WSL runtimes, and stored relative_path unchanged.
"""

from __future__ import annotations

from pathlib import Path

import scripts.local_media_agent.ffprobe_metadata_extraction as met


def _adapt(path: str, tool: str) -> str:
    return met._adapt_path_for_ffprobe(Path(path), tool)


class TestWslWindowsBridge:
    def test_wsl_exe_mnt_f_translates_to_f_colon(self, monkeypatch):
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
        result = _adapt(
            "/mnt/f/SIRUELA/Kiko Traza/Campo/C001.MP4",
            "/tmp/opencode/btbn_ffmpeg_bin/ffprobe.exe",
        )
        assert result == r"F:\SIRUELA\Kiko Traza\Campo\C001.MP4"

    def test_wsl_exe_path_with_spaces_translates(self, monkeypatch):
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
        result = _adapt(
            "/mnt/d/Material/Raw/Take 01/A001.wav",
            "ffprobe.exe",
        )
        assert result == r"D:\Material\Raw\Take 01\A001.wav"

    def test_wsl_linux_ffprobe_keeps_posix_path(self, monkeypatch):
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
        result = _adapt(
            "/mnt/f/SIRUELA/Kiko Traza/Campo/C001.MP4",
            "/usr/bin/ffprobe",
        )
        assert result == "/mnt/f/SIRUELA/Kiko Traza/Campo/C001.MP4"

    def test_non_wsl_runtime_keeps_path_unchanged(self, monkeypatch):
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
        result = _adapt(
            "/mnt/f/SIRUELA/Kiko Traza/Campo/C001.MP4",
            "ffprobe.exe",
        )
        assert result == "/mnt/f/SIRUELA/Kiko Traza/Campo/C001.MP4"

    def test_non_mnt_path_kept_unchanged(self, monkeypatch):
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")
        result = _adapt(
            "/home/user/media/C001.MP4",
            "ffprobe.exe",
        )
        assert result == "/home/user/media/C001.MP4"


class TestRelativePathPreserved:
    def test_collect_and_probe_do_not_change_relative_path(self, monkeypatch, tmp_path):
        # The adaptation only affects the ffprobe subprocess arg; here we
        # confirm _collect_media_files keeps relative_path POSIX despite the
        # Windows-bridge existing in the module (no abs_path adaptation in the
        # collected metadata at all).
        monkeypatch.setattr("os.name", "posix")
        monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu")

        (tmp_path / "C001.MP4").write_bytes(b"")
        files = met._collect_media_files(
            tmp_path,
            {".mp4": 1},
        )
        assert files[0]["relative_path"] == "C001.MP4"
        assert files[0]["abs_path"] == str(tmp_path / "C001.MP4")
