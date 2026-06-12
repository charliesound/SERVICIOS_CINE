from __future__ import annotations

import csv
import json
from pathlib import Path

from ailink_tools.sync_dialogue.schemas import SyncDialogueScanResult

CSV_COLUMNS = [
    "kind",
    "relative_path",
    "filename",
    "extension",
    "size_bytes",
    "probe_status",
    "duration_seconds",
    "timecode",
    "fps",
    "audio_channels",
    "codec_name",
    "format_name",
    "error_message",
]


def write_scan_json(result: SyncDialogueScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_media_csv(result: SyncDialogueScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for media_file in result.media_files:
            row = media_file.to_dict()
            writer.writerow({column: row.get(column) for column in CSV_COLUMNS})
    return path
