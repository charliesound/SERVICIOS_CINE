from __future__ import annotations

import csv
import json
from pathlib import Path

from ailink_tools.sync_dialogue.exports import CSV_COLUMNS, write_media_csv, write_scan_json
from ailink_tools.sync_dialogue.schemas import SyncDialogueMediaFile, SyncDialogueScanResult


def _scan_result() -> SyncDialogueScanResult:
    return SyncDialogueScanResult(
        root_path="/project",
        total_files=2,
        video_count=1,
        audio_count=1,
        unsupported_count=0,
        media_files=[
            SyncDialogueMediaFile(
                path="/project/clip.mov",
                relative_path="clip.mov",
                filename="clip.mov",
                extension=".mov",
                kind="video",
                size_bytes=10,
                probe_status="ok",
                duration_seconds=12.5,
                timecode="01:00:00:00",
                fps=24.0,
                codec_name="prores",
                format_name="mov",
            ),
            SyncDialogueMediaFile(
                path="/project/audio/sound.wav",
                relative_path="audio/sound.wav",
                filename="sound.wav",
                extension=".wav",
                kind="audio",
                size_bytes=20,
                probe_status="not_run",
                audio_channels=2,
                codec_name="pcm_s24le",
                format_name="wav",
            ),
        ],
    )


def test_json_is_written_and_readable(tmp_path: Path) -> None:
    output_path = write_scan_json(_scan_result(), tmp_path / "out" / "scan.json")

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["summary"]["video_count"] == 1
    assert payload["summary"]["audio_count"] == 1
    assert len(payload["media_files"]) == 2


def test_json_output_is_utf8(tmp_path: Path) -> None:
    output_path = write_scan_json(_scan_result(), tmp_path / "scan.json")

    assert output_path.read_bytes().decode("utf-8")


def test_csv_is_written_with_expected_columns(tmp_path: Path) -> None:
    output_path = write_media_csv(_scan_result(), tmp_path / "media.csv")


    with output_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == CSV_COLUMNS


def test_csv_preserves_video_and_audio_rows(tmp_path: Path) -> None:
    output_path = write_media_csv(_scan_result(), tmp_path / "media.csv")

    with output_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert [row["kind"] for row in rows] == ["video", "audio"]
    assert [row["relative_path"] for row in rows] == ["clip.mov", "audio/sound.wav"]


def test_csv_output_is_utf8(tmp_path: Path) -> None:
    output_path = write_media_csv(_scan_result(), tmp_path / "media.csv")

    assert output_path.read_bytes().decode("utf-8")
