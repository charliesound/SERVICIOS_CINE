"""CID Local Media Agent — Windows Operator Experience.

Launches the read-only folder scanner, extracts metadata via ffprobe,
and presents a human-readable summary. Supports optional local transcription.
No backend, no database, no network.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.local_media_agent.read_only_folder_scanner import (
    scan_read_only_folder,
)
from scripts.local_media_agent.ffprobe_metadata_extraction import (
    extract_metadata,
    resolve_ffprobe_path,
)


HEADER = r"""
  ======================================================
   CID  Local Media Agent  V0.2
   Scan + Metadata + Batch Transcription + Subtitles
  ======================================================
"""

SEPARATOR = "  ------------------------------------------------------"

PREVIEW_COUNT = 8


def _category_counts(ext_summary: dict[str, int]) -> dict[str, int]:
    video_exts = {".mp4", ".mov", ".mxf", ".mkv", ".avi", ".mts", ".m2ts", ".webm"}
    audio_exts = {".wav", ".bwf", ".aif", ".aiff", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
    image_exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".cr3", ".arw", ".nef", ".orf", ".raf"}
    video = sum(v for ext, v in ext_summary.items() if ext in video_exts)
    audio = sum(v for ext, v in ext_summary.items() if ext in audio_exts)
    images = sum(v for ext, v in ext_summary.items() if ext in image_exts)
    other = sum(v for ext, v in ext_summary.items() if ext not in video_exts | audio_exts | image_exts)
    return {"video": video, "audio": audio, "images": images, "other": other}


def _display_scan_result(folder: str, result: dict) -> None:
    status = result.get("status", "UNKNOWN")
    summary = result.get("scanner_summary", {})
    ext_summary = result.get("extension_summary", {})
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])
    cats = _category_counts(ext_summary)

    print(SEPARATOR)
    print(f"  Folder:              {folder}")
    print(SEPARATOR)
    print(f"  Media files:         {summary.get('media_candidates', 0)}")
    print(f"  Video:               {cats['video']}")
    print(f"  Audio:               {cats['audio']}")
    print(f"  Images:              {cats['images']}")
    if cats["other"]:
        print(f"  Other files:         {cats['other']}")
    print(f"  Directories scanned: {summary.get('directories_seen', 0)}")
    print(f"  Errors:              {len(errors)}")
    print(f"  Warnings:            {len(warnings)}")
    print(SEPARATOR)
    print(f"  Status: {status}")
    print(SEPARATOR)

    if errors:
        print()
        print("  Errors:")
        for e in errors[:5]:
            print(f"    - {e}")
    if warnings:
        print()
        print("  Warnings:")
        for w in warnings[:5]:
            print(f"    - {w}")


def _display_metadata_result(meta: dict) -> None:
    attempted = meta.get("media_attempted", 0)
    success = meta.get("metadata_success_count", 0)
    errors_count = meta.get("metadata_error_count", 0)
    elapsed = meta.get("elapsed_seconds", 0)
    tool = meta.get("ffprobe_path", "?")

    print()
    print(SEPARATOR)
    print(f"  Metadata extraction")
    print(SEPARATOR)
    print(f"  ffprobe:              {tool}")
    print(f"  Media attempted:      {attempted}")
    print(f"  Metadata extracted:   {success}")
    print(f"  Metadata errors:      {errors_count}")
    print(f"  Elapsed:              {elapsed:.1f}s")
    print(SEPARATOR)

    results = meta.get("results", [])
    if not results:
        return

    cats = {"video": 0, "audio": 0, "image": 0}
    for r in results:
        cat = r.get("category", "")
        if cat in cats:
            cats[cat] += 1

    print(f"  Videos probed:        {cats['video']}")
    print(f"  Audio probed:         {cats['audio']}")
    print(f"  Images probed:        {cats['image']}")
    print(SEPARATOR)

    _show_codecs_summary(results)
    _show_resolutions_summary(results)
    _show_sample_rates_summary(results)
    _show_timecodes_summary(results)
    _show_creation_times_summary(results)

    print()
    print(f"  Preview (first {PREVIEW_COUNT} items):")
    print(SEPARATOR)
    for item in results[:PREVIEW_COUNT]:
        _display_preview_item(item)
    if len(results) > PREVIEW_COUNT:
        print(f"  ... and {len(results) - PREVIEW_COUNT} more")
    print(SEPARATOR)


def _show_codecs_summary(results: list[dict]) -> None:
    v_codecs = set()
    a_codecs = set()
    for r in results:
        v = r.get("video", {})
        a = r.get("audio", {})
        if v.get("codec"):
            v_codecs.add(v["codec"])
        if a.get("codec"):
            a_codecs.add(a["codec"])
    if v_codecs:
        print(f"  Video codecs:         {', '.join(sorted(v_codecs))}")
    if a_codecs:
        print(f"  Audio codecs:         {', '.join(sorted(a_codecs))}")


def _show_resolutions_summary(results: list[dict]) -> None:
    res = set()
    for r in results:
        v = r.get("video", {})
        w, h = v.get("width"), v.get("height")
        if w and h:
            res.add(f"{w}x{h}")
    if res:
        print(f"  Resolutions:          {', '.join(sorted(res))}")


def _show_sample_rates_summary(results: list[dict]) -> None:
    rates = set()
    for r in results:
        a = r.get("audio", {})
        sr = a.get("sample_rate")
        if sr:
            rates.add(str(sr))
    if rates:
        print(f"  Sample rates:         {', '.join(sorted(rates))} Hz")


def _show_timecodes_summary(results: list[dict]) -> None:
    tcs = [r.get("timecode") for r in results if r.get("timecode")]
    if tcs:
        print(f"  Timecodes found:      {len(tcs)}")


def _show_creation_times_summary(results: list[dict]) -> None:
    cts = [r.get("creation_time") for r in results if r.get("creation_time")]
    if cts:
        print(f"  Creation times found: {len(cts)}")


def _display_preview_item(item: dict) -> None:
    name = Path(item.get("relative_path", "?")).name
    cat = item.get("category", "?")
    dur = item.get("duration_seconds")
    dur_str = _format_duration(dur) if dur else None

    print()
    print(f"    {name}")
    print(f"    {cat.capitalize()}")

    v = item.get("video")
    if v:
        w, h = v.get("width"), v.get("height")
        if w and h:
            print(f"    {w} x {h}")
        fr = v.get("frame_rate", {})
        disp = fr.get("display") if isinstance(fr, dict) else None
        if disp:
            print(f"    {disp} fps")
        codec = v.get("codec")
        if codec:
            print(f"    {codec}")

    a = item.get("audio")
    if a:
        parts = []
        sr = a.get("sample_rate")
        ch = a.get("channel_count")
        if sr:
            parts.append(f"{sr} Hz")
        if ch:
            parts.append(f"{ch} ch")
        if parts:
            print(f"    Audio: {' / '.join(parts)}")
        codec = a.get("codec")
        if codec and not v:
            print(f"    {codec}")

    if v is None and a is None:
        w = item.get("width")
        h = item.get("height")
        if w and h:
            print(f"    {w} x {h}")

    if dur_str:
        print(f"    Duration: {dur_str}")

    tc = item.get("timecode")
    if tc:
        print(f"    Timecode: {tc}")

    ct = item.get("creation_time")
    if ct:
        print(f"    Created:  {ct}")


def _format_duration(seconds: float) -> str | None:
    if seconds is None or seconds <= 0:
        return None
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _write_json_result(meta: dict, folder: str, transcription: dict | None = None) -> str | None:
    try:
        tmp = Path(tempfile.gettempdir()) / "cid_lma_metadata"
        tmp.mkdir(parents=True, exist_ok=True)
        out = tmp / "metadata_result.json"
        payload = {
            "input_root": folder,
            "metadata": meta,
        }
        if transcription:
            payload["transcription"] = transcription
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(out)
    except Exception:
        return None


def _try_folder_dialog() -> str | None:
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select folder to scan")
        root.destroy()
        return folder if folder else None
    except Exception:
        return None


def _prompt_folder() -> str:
    print("  Enter a folder path to scan, or press Enter to browse.")
    print()
    raw = input("  Folder: ").strip().strip('"').strip("'")
    if not raw:
        print()
        print("  Opening folder browser...")
        folder = _try_folder_dialog()
        if folder:
            return folder
        print("  Folder browser unavailable. Please type a path.")
        return _prompt_folder()
    return raw


def _run(folder: str, *, do_transcribe: bool = False, model_dir: str | None = None) -> int:
    if not os.path.isdir(folder):
        print()
        print(f"  ERROR: Folder not found: {folder}")
        print()
        return 1

    result = scan_read_only_folder(folder)
    print()
    _display_scan_result(folder, result)

    meta = extract_metadata(folder, result)
    _display_metadata_result(meta)

    transcription_results = None
    if do_transcribe:
        if not model_dir or not Path(model_dir).is_dir():
            print()
            print(f"  ERROR: Transcription model directory not found: {model_dir}")
            print()
        else:
            transcription_results = _run_transcription(meta, model_dir, Path(folder))

    json_path = _write_json_result(meta, folder, transcription_results)
    if json_path:
        print()
        print(f"  JSON result: {json_path}")

    print()
    return 0


def _run_transcription(meta: dict, model_dir: str, source_folder: Path) -> dict:
    from scripts.local_media_agent.local_transcription import (
        select_transcription_samples,
        transcribe_media_file,
    )

    results = meta.get("results", [])

    samples = select_transcription_samples(results, max_video=1, max_audio=2)
    if not samples:
        print()
        print("  No audio/video samples found for transcription.")
        return {"samples_attempted": 0, "samples": []}

    print()
    print(SEPARATOR)
    print(f"  Transcription")
    print(SEPARATOR)
    print(f"  Model:               {model_dir}")
    print(f"  Samples selected:    {len(samples)}")
    print(SEPARATOR)

    transcription_samples = []
    start = time.monotonic()

    for item in samples:
        rel = item.get("relative_path", "")
        abs_path = source_folder / rel
        cat = item.get("category", "?")
        dur = item.get("duration_seconds")
        dur_str = f"{dur:.1f}s" if dur else "?"

        print(f"  Transcribing: {rel} ({cat}, {dur_str})")

        result = transcribe_media_file(
            abs_path,
            model_dir,
            asset_id=Path(rel).stem,
            device="cpu",
            compute_type="float32",
        )
        status = result.get("status", "?")
        lang = result.get("detected_language", "?")
        segs = len(result.get("segments", []))
        print(f"    Status: {status} | Language: {lang} | Segments: {segs}")
        transcription_samples.append(result)

    elapsed = time.monotonic() - start
    success = sum(1 for s in transcription_samples if s.get("status") == "TRANSCRIPTION_COMPLETED")
    print(SEPARATOR)
    print(f"  Transcription completed: {success}/{len(transcription_samples)}")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(SEPARATOR)

    return {
        "samples_attempted": len(transcription_samples),
        "samples_success": success,
        "elapsed_seconds": round(elapsed, 2),
        "model_directory": model_dir,
        "device": "cpu",
        "compute_type": "float32",
        "samples": transcription_samples,
    }


def _run_batch_transcription(folder: str, model_dir: str, *, max_files: int | None = None, filter_pattern: str | None = None, compute_type: str = "int8", language_hint: str | None = None) -> int:
    """Run the full batch transcription flow with DaVinci handoff."""
    from scripts.local_media_agent.batch_transcription import run_batch_transcription

    if not os.path.isdir(folder):
        print()
        print(f"  ERROR: Folder not found: {folder}")
        return 1

    if not model_dir or not Path(model_dir).is_dir():
        print()
        print(f"  ERROR: Transcription model directory not found: {model_dir}")
        return 1

    print()
    print(SEPARATOR)
    print(f"  Batch Transcription + DaVinci Handoff")
    print(SEPARATOR)
    print(f"  Folder:       {folder}")
    print(f"  Model:        {Path(model_dir).name}")
    print(f"  Compute:      {compute_type}")
    if max_files:
        print(f"  Max files:    {max_files}")
    if filter_pattern:
        print(f"  Filter:       {filter_pattern}")
    if language_hint:
        print(f"  Language:     {language_hint}")
    print(SEPARATOR)
    print()

    batch = run_batch_transcription(
        folder,
        model_dir,
        compute_type=compute_type,
        max_files=max_files,
        filter_pattern=filter_pattern,
        language_hint=language_hint,
    )

    dur = batch.get("total_source_duration_seconds", 0)
    proc = batch.get("total_processing_seconds", 0)
    rtf = batch.get("overall_rtf")
    lang = batch.get("primary_language")

    hours = int(dur // 3600)
    minutes = int((dur % 3600) // 60)
    seconds = int(dur % 60)
    dur_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if dur else "?"

    print()
    print(SEPARATOR)
    print(f"  CID Local Media Agent V0.2")
    print()
    print(f"  Full transcription completed")
    print(SEPARATOR)
    print(f"  Source duration:       {dur_str}")
    print(f"  Language:              {lang or '?'}")
    print(f"  Segments:              {sum(len(r.get('segments', [])) for r in batch.get('results', []))}")
    print(f"  Compute:               {compute_type}")
    print(f"  Processing time:       {proc:.1f}s")
    if rtf:
        print(f"  RTF:                   {rtf:.4f}")
    print()
    print(f"  Transcript:            ready")
    print(f"  SRT subtitles:         ready")
    print(f"  DaVinci handoff:       ready")
    print()
    results_dir = batch.get("results_directory", "?")
    print(f"  Results: {results_dir}")
    print()
    for r in batch.get("results", []):
        srt_name = r.get("srt_file")
        if srt_name:
            print(f"  DaVinci subtitle file: {srt_name}")
            break
    print(SEPARATOR)

    return 0


def _run_scan_and_sync(folder: str, model_dir: str) -> int:
    """Scan a folder, extract metadata, then run read-only sync."""
    if not os.path.isdir(folder):
        print()
        print(f"  ERROR: Folder not found: {folder}")
        return 1

    result = scan_read_only_folder(folder)
    print()
    _display_scan_result(folder, result)

    meta = extract_metadata(folder, result)
    _display_metadata_result(meta)

    return _run_sync(folder, meta, model_dir)


def _run_sync(folder: str, meta: dict, model_dir: str) -> int:
    """Run read-only automatic synchronization (informational only).

    Uses the automatic_media_sync engine on the metadata already extracted
    by the operator. Never modifies, moves, or retimes media. Results are
    reported as structured RESOLVED/UNRESOLVED informational output.
    """
    from scripts.local_media_agent.automatic_media_sync import (
        assemble_project_sessions,
    )

    if not os.path.isdir(folder):
        print()
        print(f"  ERROR: Folder not found: {folder}")
        return 1
    if not model_dir or not Path(model_dir).is_dir():
        print()
        print(f"  ERROR: Transcription model directory not found: {model_dir}")
        return 1

    results = meta.get("results", [])
    if not results:
        print()
        print("  No media metadata available to synchronize.")
        return 0

    source_root = Path(folder)
    for item in results:
        rel = item.get("relative_path")
        if rel:
            item["abs_path"] = str(source_root / rel)

    print()
    print(SEPARATOR)
    print(f"  Automatic Synchronization (informational)")
    print(SEPARATOR)
    print(f"  Model:               {model_dir}")
    print(f"  Media items:         {len(results)}")
    print(SEPARATOR)

    project = assemble_project_sessions(results, model_local_path=model_dir)

    resolved = 0
    unresolved = 0
    for session in project.sessions:
        for clip in session.synchronized_clips:
            if clip.unresolved:
                unresolved += 1
            else:
                resolved += 1
            _display_sync_clip(clip)
    for rel in project.unresolved_media:
        unresolved += 1
        print()
        print(f"    UNRESOLVED  {Path(rel).name}")

    print()
    print(SEPARATOR)
    print(f"  Sync summary")
    print(SEPARATOR)
    print(f"  Sessions:            {len(project.sessions)}")
    print(f"  Resolved clips:      {resolved}")
    print(f"  Unresolved clips:    {unresolved}")
    print(f"  Since sync is informational read-only, no media was modified.")
    print(SEPARATOR)

    return _write_sync_json(folder, project)


def _display_sync_clip(clip) -> None:
    if clip.unresolved:
        _display_unresolved_clip(clip)
        return
    status = "RESOLVED"
    offset_s = clip.intercept_a
    offset_ms = None
    if offset_s is not None:
        offset_ms = offset_s * 1000
    speed = clip.audio_speed_percent
    retime = clip.retime_recommended
    print()
    print(f"    {status}  {Path(clip.video_path).name}")
    print(f"      audio:            {Path(clip.audio_reference).name}")
    print(f"      confidence:       {clip.confidence}")
    if offset_ms is not None:
        print(f"      offset:           {offset_s:.6f} s ({offset_ms:.3f} ms)")
    if speed is not None:
        print(f"      audio speed:      {speed:.4f}%")
    print(f"      retime:           {'recommended' if retime else 'not recommended'}")


def _display_unresolved_clip(clip) -> None:
    print()
    print(f"    UNRESOLVED  {Path(clip.video_path).name}")
    print(f"      audio:            {Path(clip.audio_reference).name}")
    print(f"      confidence:       {clip.confidence}")
    reason = _unresolved_reason(clip)
    if reason:
        print(f"      reason:           {reason}")
    candidate = clip.intercept_a
    if candidate is not None:
        cand_ms = candidate * 1000
        print(f"      candidate_offset: {candidate:.6f} s ({cand_ms:.3f} ms)  [diagnostic_only]")
    print(f"      No safe synchronization was established.")


def _unresolved_reason(clip) -> str | None:
    evidence = getattr(clip, "evidence", None)
    if isinstance(evidence, list):
        for entry in evidence:
            if isinstance(entry, dict) and entry.get("reason"):
                return str(entry["reason"])
            root = entry.get("root_cause") if isinstance(entry, dict) else None
            if root:
                return str(root)
    return getattr(clip, "root_cause", None) or getattr(clip, "reason", None)


def _write_sync_json(folder: str, project) -> int:
    try:
        tmp = Path(tempfile.gettempdir()) / "cid_lma_sync"
        tmp.mkdir(parents=True, exist_ok=True)
        out = tmp / "sync_result.json"
        payload = {
            "input_root": folder,
            "informational_only": True,
            "source_media_modified": False,
            "project": project.to_dict(),
        }
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        print()
        print(f"  JSON result: {out}")
        return 0
    except Exception as exc:
        print()
        print(f"  WARNING: could not write JSON result: {exc}")
        return 0


def _prompt_menu() -> str:
    """Display the interactive menu and get user choice."""
    print()
    print(SEPARATOR)
    print(f"  Choose operation:")
    print()
    print(f"    1.  Scan only")
    print(f"    2.  Scan + metadata")
    print(f"    3.  Batch transcribe (select count)")
    print(f"    4.  Batch transcribe all valid candidates")
    print(f"    5.  Sync video to audio (informational, read-only)")
    print()
    print(SEPARATOR)
    choice = input("  Choice [1-5]: ").strip()
    return choice


def _resolve_packaged_model() -> str | None:
    """Check for a CID-packaged model relative to this file's location."""
    here = Path(__file__).resolve().parent
    for depth in (here, *here.parents):
        candidate = depth / "models" / "faster-whisper-small"
        if candidate.is_dir() and (candidate / "model.bin").is_file():
            return str(candidate)
    return None


def _prompt_model_dir() -> str | None:
    """Prompt for model directory path."""
    packaged = _resolve_packaged_model()
    default = packaged or ""
    print()
    if default:
        raw = input(f"  Model directory [{default}]: ").strip().strip('"').strip("'")
        return raw if raw else default
    raw = input("  Model directory: ").strip().strip('"').strip("'")
    return raw or None


def _prompt_max_files() -> int | None:
    """Prompt for max files to transcribe."""
    print()
    raw = input("  Max files to transcribe (Enter for all): ").strip()
    if not raw:
        return None
    try:
        val = int(raw)
        return val if val > 0 else None
    except ValueError:
        return None


def main() -> int:
    os.system("cls" if os.name == "nt" else "clear")
    print(HEADER)

    args = sys.argv[1:]

    if "--batch" in args:
        idx = args.index("--batch")
        args.pop(idx)
        batch_model = None
        batch_max = None
        batch_filter = None
        batch_lang = None
        batch_compute = "int8"
        while args and args[0].startswith("--"):
            if args[0] == "--model" and len(args) > 1:
                batch_model = args.pop(1)
                args.pop(0)
            elif args[0] == "--max" and len(args) > 1:
                batch_max = int(args.pop(1))
                args.pop(0)
            elif args[0] == "--filter" and len(args) > 1:
                batch_filter = args.pop(1)
                args.pop(0)
            elif args[0] == "--language" and len(args) > 1:
                batch_lang = args.pop(1)
                args.pop(0)
            elif args[0] == "--compute" and len(args) > 1:
                batch_compute = args.pop(1)
                args.pop(0)
            else:
                break
        folder = " ".join(args) if args else None
        if not folder:
            folder = _prompt_folder()
        if not batch_model:
            batch_model = _prompt_model_dir()
        return _run_batch_transcription(
            folder, batch_model,
            max_files=batch_max,
            filter_pattern=batch_filter,
            compute_type=batch_compute,
            language_hint=batch_lang,
        )

    do_transcribe = False
    model_dir = None

    if "--sync" in args:
        args.remove("--sync")
        if not args or args[0].startswith("-"):
            print("  Sync requires a model directory followed by a folder.")
            print("  Usage: python cid_local_media_agent_operator.py --sync <model_dir> <folder>")
            return 1
        sync_model = args.pop(0)
        folder = " ".join(args) if args else None
        if not folder:
            folder = _prompt_folder()
        return _run_scan_and_sync(folder, sync_model)

    if "--transcribe" in args:
        do_transcribe = True
        args.remove("--transcribe")
        if args and not args[0].startswith("-"):
            model_dir = args.pop(0)

    interactive = len(args) <= 1
    if interactive:
        folder = _prompt_folder()
        choice = _prompt_menu()

        if choice == "3":
            model_dir = _prompt_model_dir()
            max_files = _prompt_max_files()
            return _run_batch_transcription(folder, model_dir, max_files=max_files)

        if choice == "4":
            model_dir = _prompt_model_dir()
            return _run_batch_transcription(folder, model_dir)

        if choice == "5":
            model_dir = _prompt_model_dir()
            return _run_scan_and_sync(folder, model_dir)

        if choice == "2":
            exit_code = _run(folder, do_transcribe=False)
            print("  Press Enter to exit...")
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass
            return exit_code

        exit_code = _run(folder, do_transcribe=False)
        print("  Press Enter to exit...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass
        return exit_code
    else:
        folder = " ".join(args)

    if do_transcribe and not model_dir:
        print("  Transcription model directory required with --transcribe.")
        print("  Usage: python cid_local_media_agent_operator.py --transcribe <model_dir> <folder>")
        return 1

    exit_code = _run(folder, do_transcribe=do_transcribe, model_dir=model_dir)

    if interactive:
        print("  Press Enter to exit...")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass

    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
