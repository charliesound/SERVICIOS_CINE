from __future__ import annotations

import base64
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schemas.editorial_assembly_schema import (  # noqa: E402
    CameraReportEntry,
    DirectorNote,
    EditorialMediaAsset,
    NLEExportRequest,
    ScriptSupervisorNote,
    SoundReportEntry,
)
from services.editorial_assembly_core_service import editorial_assembly_core_service  # noqa: E402
from services.editorial_export_adapter_service import editorial_export_adapter_service  # noqa: E402

PROJECT_ID = "editorial-resolve-smoke-20260525"
FIXTURE_ROOT = ROOT / "docs" / "validation" / "production_real_20260428"
OUTPUT_DIR = ROOT / "docs" / "validation" / "editorial_assembly_resolve_smoke_20260525"
FPS_DEFAULT = 24.0


def run_smoke(
    *,
    fixture_root: Path = FIXTURE_ROOT,
    output_dir: Path = OUTPUT_DIR,
) -> dict[str, Any]:
    if not fixture_root.exists():
        raise RuntimeError(f"fixture_not_found:{fixture_root}")

    output_dir.mkdir(parents=True, exist_ok=True)
    media_roots = _media_roots(fixture_root)
    camera_reports = _load_camera_reports(fixture_root)
    sound_reports = _load_sound_reports(fixture_root)
    script_notes = _load_script_notes(fixture_root, camera_reports)
    director_notes = _load_director_notes(fixture_root, camera_reports)
    metadata = _load_metadata_manifest(fixture_root)

    scanned_assets, scan_warnings = editorial_assembly_core_service.scan_media_roots(
        project_id=PROJECT_ID,
        root_paths=[str(path) for path in media_roots],
        recursive=True,
        max_files=10000,
    )
    media_assets = _enrich_assets(scanned_assets, metadata)
    import_result = editorial_assembly_core_service.import_reports(
        project_id=PROJECT_ID,
        camera_reports=camera_reports,
        sound_reports=sound_reports,
        script_notes=script_notes,
        director_notes=director_notes,
    )
    slate_matches, take_decisions, sync_candidates, match_warnings = editorial_assembly_core_service.match_takes(
        project_id=PROJECT_ID,
        media_assets=media_assets,
        camera_reports=camera_reports,
        sound_reports=sound_reports,
        script_notes=script_notes,
        director_notes=director_notes,
    )
    timeline = editorial_assembly_core_service.build_neutral_assembly(
        project_id=PROJECT_ID,
        take_decisions=take_decisions,
        media_assets=media_assets,
        name="CID Editorial Resolve Smoke",
        fps=FPS_DEFAULT,
        allow_missing_audio=True,
    )

    if not timeline.sequences or not any(sequence.clips for sequence in timeline.sequences):
        raise RuntimeError("neutral_timeline_has_no_clips")

    export_request = NLEExportRequest(
        nle_type="resolve",
        target_platform="linux",
        destination_root_path=str(output_dir),
        include_relink_report=True,
        timeline=timeline,
        media_assets=media_assets,
    )
    export_result = editorial_export_adapter_service.export(export_request, timeline)
    fcpxml_bytes = base64.b64decode(export_result.file_bytes_b64)
    _validate_fcpxml_payload(fcpxml_bytes)

    fcpxml_path = output_dir / export_result.file_name
    relink_report_path = output_dir / "media_relink_report.json"
    manifest_path = output_dir / "manifest.json"
    timeline_path = output_dir / "neutral_timeline.json"

    fcpxml_path.write_bytes(fcpxml_bytes)
    relink_report = export_result.manifest.get("relink_report") or {}
    relink_report_path.write_text(json.dumps(relink_report, indent=2, sort_keys=True), encoding="utf-8")
    timeline_path.write_text(json.dumps(timeline.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")

    warnings = list(scan_warnings) + list(match_warnings) + list(export_result.warnings)
    manifest = {
        "status": "ok",
        "fixture_root": str(fixture_root),
        "output_dir": str(output_dir),
        "media_roots": [str(path) for path in media_roots],
        "camera_assets_count": _count_assets(media_assets, "video"),
        "sound_assets_count": _count_assets(media_assets, "audio"),
        "camera_reports_count": len(camera_reports),
        "sound_reports_count": len(sound_reports),
        "script_notes_count": len(script_notes),
        "director_notes_count": len(director_notes),
        "slate_matches_count": len(slate_matches),
        "take_decisions_count": len(take_decisions),
        "sync_candidates_count": len(sync_candidates),
        "sequence_count": len(timeline.sequences),
        "clip_count": sum(len(sequence.clips) for sequence in timeline.sequences),
        "total_duration_frames": timeline.total_duration_frames,
        "clips": _clip_summary(timeline),
        "fcpxml_path": str(fcpxml_path),
        "fcpxml_size_bytes": fcpxml_path.stat().st_size,
        "relink_report_path": str(relink_report_path),
        "manifest_path": str(manifest_path),
        "timeline_path": str(timeline_path),
        "import_report": import_result.model_dump(mode="json"),
        "export_manifest": export_result.manifest,
        "warnings": warnings,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def _media_roots(fixture_root: Path) -> list[Path]:
    roots = [fixture_root / "media_roots" / "camera", fixture_root / "media_roots" / "sound"]
    existing_roots = [path for path in roots if path.exists()]
    if existing_roots:
        return existing_roots
    media_root = fixture_root / "media"
    if media_root.exists():
        return [media_root]
    raise RuntimeError(f"media_roots_not_found:{fixture_root}")


def _load_camera_reports(fixture_root: Path) -> list[CameraReportEntry]:
    report_path = fixture_root / "reports" / "camera_report.csv"
    rows = _read_csv(report_path)
    reports: list[CameraReportEntry] = []
    for row in rows:
        scene = _int_value(row.get("scene"))
        shot = _int_value(row.get("shot"))
        take = _int_value(row.get("take"))
        reports.append(
            CameraReportEntry(
                card_or_mag=row.get("filmroll") or row.get("reel") or "unknown",
                clip_name=_camera_file_name(scene, shot, take),
                scene=scene,
                shot=shot,
                take=take,
                fps=_float_value(row.get("fps") or row.get("rate"), FPS_DEFAULT),
                lens=row.get("lens") or None,
                notes=row.get("notes") or None,
            )
        )
    return reports


def _load_sound_reports(fixture_root: Path) -> list[SoundReportEntry]:
    report_path = fixture_root / "reports" / "sound_report.csv"
    rows = _read_csv(report_path)
    reports: list[SoundReportEntry] = []
    metadata = _load_metadata_manifest(fixture_root)
    for row in rows:
        scene = _int_value(row.get("scene"))
        shot = _int_value(row.get("shot"))
        take = _int_value(row.get("take"))
        key = _take_key(scene, shot, take)
        reports.append(
            SoundReportEntry(
                sound_roll=row.get("roll") or row.get("reel") or "unknown",
                file_name=_sound_file_name(scene, shot, take),
                scene=scene,
                shot=shot,
                take=take,
                timecode_start=str(metadata.get(key, {}).get("tc") or "00:00:00:00"),
                tracks_count=2,
                notes=row.get("notes") or None,
            )
        )
    return reports


def _load_script_notes(
    fixture_root: Path,
    camera_reports: list[CameraReportEntry],
) -> list[ScriptSupervisorNote]:
    report_path = fixture_root / "reports" / "script_notes.csv"
    rows_by_shot = {
        (_int_value(row.get("scene")), _int_value(row.get("shot"))): row
        for row in _read_csv(report_path)
    }
    circled = _circled_takes(fixture_root)
    notes: list[ScriptSupervisorNote] = []
    for report in camera_reports:
        row = rows_by_shot.get((report.scene, report.shot), {})
        notes.append(
            ScriptSupervisorNote(
                scene_number=report.scene,
                shot_number=report.shot,
                take_number=report.take,
                is_circled=_take_key(report.scene, report.shot, report.take) in circled,
                continuity_notes=row.get("notes") or row.get("description") or None,
                editor_note=row.get("action") or None,
            )
        )
    return notes


def _load_director_notes(
    fixture_root: Path,
    camera_reports: list[CameraReportEntry],
) -> list[DirectorNote]:
    notes_path = fixture_root / "reports" / "director_notes.md"
    notes_text = notes_path.read_text(encoding="utf-8") if notes_path.exists() else ""
    preferred = _preferred_takes(camera_reports, _circled_takes(fixture_root))
    notes: list[DirectorNote] = []
    for report in camera_reports:
        notes.append(
            DirectorNote(
                scene_number=report.scene,
                shot_number=report.shot,
                take_number=report.take,
                is_preferred=_take_key(report.scene, report.shot, report.take) in preferred,
                intention_note=_director_note_for_shot(notes_text, report.scene, report.shot),
            )
        )
    return notes


def _enrich_assets(
    assets: list[EditorialMediaAsset],
    metadata: dict[tuple[int, int, int], dict[str, Any]],
) -> list[EditorialMediaAsset]:
    by_camera_file = {str(item.get("camera_file")): item for item in metadata.values()}
    by_sound_file = {str(item.get("sound_file")): item for item in metadata.values()}
    enriched: list[EditorialMediaAsset] = []
    for asset in assets:
        item = by_camera_file.get(asset.file_name) or by_sound_file.get(asset.file_name) or {}
        duration_frames = int(float(item.get("duration") or 4.0) * FPS_DEFAULT)
        asset.duration_frames = duration_frames
        asset.fps = FPS_DEFAULT
        asset.start_timecode = str(item.get("tc") or "00:00:00:00")
        if asset.asset_type == "audio":
            asset.channels = 2
            asset.sample_rate = 48000
        enriched.append(asset)
    return enriched


def _validate_fcpxml_payload(payload: bytes) -> None:
    if not payload:
        raise RuntimeError("fcpxml_empty")
    root = ET.fromstring(payload)
    resources = root.find("resources")
    assets = resources.findall("asset") if resources is not None else []
    if root.tag != "fcpxml":
        raise RuntimeError("fcpxml_root_missing")
    if not assets:
        raise RuntimeError("fcpxml_media_resources_missing")


def _load_metadata_manifest(fixture_root: Path) -> dict[tuple[int, int, int], dict[str, Any]]:
    manifest_path = fixture_root / "metadata_manifest.json"
    if not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        _take_key(_int_value(item.get("scene")), _int_value(item.get("shot")), _int_value(item.get("take"))): item
        for item in data
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _circled_takes(fixture_root: Path) -> set[tuple[int, int, int]]:
    metadata = _load_metadata_manifest(fixture_root)
    circled = {key for key, value in metadata.items() if value.get("circled") is True}
    if circled:
        return circled
    circled_from_camera = set()
    for row in _read_csv(fixture_root / "reports" / "camera_report.csv"):
        if str(row.get("circular") or "").upper() == "OK":
            circled_from_camera.add(
                _take_key(_int_value(row.get("scene")), _int_value(row.get("shot")), _int_value(row.get("take")))
            )
    return circled_from_camera


def _preferred_takes(
    camera_reports: list[CameraReportEntry],
    circled: set[tuple[int, int, int]],
) -> set[tuple[int, int, int]]:
    preferred: dict[tuple[int, int], tuple[int, int, int]] = {}
    for report in camera_reports:
        key = _take_key(report.scene, report.shot, report.take)
        shot_key = (report.scene, report.shot)
        if key in circled and shot_key not in preferred:
            preferred[shot_key] = key
    return set(preferred.values())


def _director_note_for_shot(notes_text: str, scene: int, shot: int) -> str | None:
    pattern = rf"SH{shot:02d}:\s*(.+)"
    match = re.search(pattern, notes_text)
    if match:
        return f"Scene {scene}: {match.group(1).strip()}"
    return None


def _clip_summary(timeline: Any) -> list[dict[str, Any]]:
    clips = []
    for sequence in timeline.sequences:
        for clip in sequence.clips:
            clips.append(
                {
                    "scene_number": sequence.scene_number,
                    "clip_name": clip.clip_name,
                    "take_id": clip.take_id,
                    "source_media_asset_id": clip.source_media_asset_id,
                    "audio_media_asset_id": clip.audio_media_asset_id,
                    "duration_frames": clip.duration_frames,
                    "timecode_offset_frames": clip.timecode_offset_frames,
                    "assigned_tracks": clip.assigned_tracks,
                }
            )
    return clips


def _count_assets(assets: list[EditorialMediaAsset], asset_type: str) -> int:
    return sum(1 for asset in assets if asset.asset_type == asset_type)


def _camera_file_name(scene: int, shot: int, take: int) -> str:
    return f"S{scene:02d}_SH{shot:02d}_TK{take:02d}_CAM.mov"


def _sound_file_name(scene: int, shot: int, take: int) -> str:
    return f"S{scene:02d}_SH{shot:02d}_TK{take:02d}_SOUND.wav"


def _take_key(scene: int, shot: int, take: int) -> tuple[int, int, int]:
    return scene, shot, take


def _int_value(value: Any, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def _float_value(value: Any, default: float) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def main() -> None:
    manifest = run_smoke()
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
