"""CID Local Media Agent — dedicated transcription worker subprocess.

Spawned by the batch controller for each active media item so cancellation
can always force-terminate an owned process tree (worker + child ffmpeg)
without ever risking unrelated python/ffmpeg/cmd processes.

Protocol:
    python -m scripts.local_media_agent.cid_transcription_worker <task.json>

``task.json`` carries the media item plus controller-owned paths: the output
WAV location, the result JSON path, a JSONL progress log, and a file-backed
cancel sentinel. The worker performs decode + transcription with the standard
LMA pipeline and writes the per-file result JSON for the controller to reap.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


class CancelSentinel:
    """File-backed cooperative cancellation observable across processes."""

    def __init__(self, sentinel_path: str | Path) -> None:
        self._sentinel = Path(sentinel_path)

    def is_set(self) -> bool:
        return self._sentinel.is_file()


def _load_task(task_json_path: str) -> dict[str, Any]:
    with open(task_json_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_result(result_path: str | Path, payload: dict[str, Any]) -> None:
    """Atomically publish the per-file result JSON (write-then-replace)."""
    result_path = Path(result_path)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = result_path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    tmp.replace(result_path)


def _progress_writer(progress_log: str | Path) -> Any:
    """Return a segment callback that appends JSONL lines for the controller."""
    path = Path(progress_log)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = (
        "source_start_seconds",
        "source_end_seconds",
        "start_seconds",
        "end_seconds",
    )

    def _write(segment: dict[str, Any]) -> None:
        try:
            payload = {k: v for k, v in segment.items() if k in fields}
            with path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
                fh.flush()
        except Exception:
            pass

    return _write


def _transcribe_task(task: dict[str, Any]) -> dict[str, Any]:
    from scripts.local_media_agent.local_transcription import transcribe_media_file

    return transcribe_media_file(
        task["media_path"],
        task["model_dir"],
        asset_id=task.get("asset_id"),
        language_hint=task.get("language_hint"),
        device=task.get("device", "cpu"),
        compute_type=task.get("compute_type", "int8"),
        ffmpeg_path=task.get("ffmpeg_path"),
        temp_dir=task.get("temp_dir"),
        output_wav_path=task.get("output_wav"),
        cancel_event=CancelSentinel(task["cancel_sentinel"]),
        segment_callback=_progress_writer(task["progress_log"]),
    )


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        return 2
    task = _load_task(argv[0])
    try:
        result = _transcribe_task(task)
        _write_result(task["result_json"], result)
        return 0
    except Exception as exc:
        _write_result(
            task["result_json"],
            {
                "schema_version": "cid.local_media_agent.local_transcription.v1",
                "status": "TRANSCRIPTION_FAILED",
                "relative_path": task.get("media_path"),
                "asset_id": task.get("asset_id"),
                "error": {"message": str(exc)[:300]},
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))