from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from schemas.editorial_assembly_schema import (
    AssemblyClip,
    AssemblySequence,
    AssemblyTimeline,
    CameraReportEntry,
    DirectorNote,
    EditorialMediaAsset,
    ImportReportsResponse,
    MissingMediaReport,
    RelinkReport,
    ScriptSupervisorNote,
    SlateMatch,
    SoundReportEntry,
    SyncCandidate,
    TakeDecision,
)


VIDEO_EXTENSIONS = {".mov", ".mxf", ".mp4", ".r3d", ".ari", ".braw"}
AUDIO_EXTENSIONS = {".wav", ".bwf", ".aif", ".aiff"}


class EditorialAssemblyCoreService:
    def scan_media_roots(
        self,
        *,
        project_id: str,
        root_paths: list[str],
        recursive: bool = True,
        max_files: int = 1000,
    ) -> tuple[list[EditorialMediaAsset], list[str]]:
        assets: list[EditorialMediaAsset] = []
        warnings: list[str] = []

        for raw_root in root_paths:
            root = Path(raw_root).expanduser()
            if not root.exists():
                warnings.append(f"root_not_found:{raw_root}")
                continue
            if not root.is_dir():
                warnings.append(f"root_not_directory:{raw_root}")
                continue

            iterator = root.rglob("*") if recursive else root.iterdir()
            for path in iterator:
                if len(assets) >= max_files:
                    warnings.append("max_files_reached")
                    return assets, warnings
                if not path.is_file():
                    continue
                asset_type = self._asset_type(path.suffix)
                if asset_type == "other":
                    continue
                assets.append(
                    EditorialMediaAsset(
                        id=f"asset-{project_id}-{len(assets) + 1}",
                        file_name=path.name,
                        file_path=str(path),
                        asset_type=asset_type,
                    )
                )

        return assets, warnings

    def import_reports(
        self,
        *,
        project_id: str,
        camera_reports: list[CameraReportEntry] | None = None,
        sound_reports: list[SoundReportEntry] | None = None,
        script_notes: list[ScriptSupervisorNote] | None = None,
        director_notes: list[DirectorNote] | None = None,
    ) -> ImportReportsResponse:
        counts = {
            "camera_reports": len(camera_reports or []),
            "sound_reports": len(sound_reports or []),
            "script_notes": len(script_notes or []),
            "director_notes": len(director_notes or []),
        }
        return ImportReportsResponse(
            project_id=project_id,
            report_id=f"report-{uuid4().hex[:12]}",
            imported_counts=counts,
        )

    def match_takes(
        self,
        *,
        project_id: str,
        media_assets: list[EditorialMediaAsset],
        camera_reports: list[CameraReportEntry] | None = None,
        sound_reports: list[SoundReportEntry] | None = None,
        script_notes: list[ScriptSupervisorNote] | None = None,
        director_notes: list[DirectorNote] | None = None,
    ) -> tuple[list[SlateMatch], list[TakeDecision], list[SyncCandidate], list[str]]:
        del project_id
        warnings: list[str] = []
        camera_reports = camera_reports or []
        sound_reports = sound_reports or []
        script_notes = script_notes or []
        director_notes = director_notes or []
        assets_by_name = {asset.file_name.lower(): asset for asset in media_assets}
        audio_assets = [asset for asset in media_assets if asset.asset_type == "audio"]

        slate_matches: list[SlateMatch] = []
        take_decisions: list[TakeDecision] = []
        sync_candidates: list[SyncCandidate] = []

        for camera_report in camera_reports:
            camera_asset = assets_by_name.get(camera_report.clip_name.lower())
            sound_report = self._find_sound_report(camera_report, sound_reports)
            script_note = self._find_script_note(camera_report, script_notes)
            director_note = self._find_director_note(camera_report, director_notes)
            confidence = 0.95 if camera_asset else 0.65
            method = "exact_report_asset" if camera_asset else "report_only"

            slate_matches.append(
                SlateMatch(
                    scene_number=camera_report.scene,
                    shot_number=camera_report.shot,
                    take_number=camera_report.take,
                    confidence=confidence,
                    matching_method=method,
                    warnings=[] if camera_asset else ["camera_asset_missing"],
                )
            )

            audio_asset = self._find_audio_asset(sound_report, audio_assets) if sound_report else None
            score = self._score_take(script_note, director_note, camera_asset is not None, audio_asset is not None)
            take_decisions.append(
                TakeDecision(
                    take_id=f"take-{camera_report.scene}-{camera_report.shot}-{camera_report.take}",
                    scene_number=camera_report.scene,
                    shot_number=camera_report.shot,
                    take_number=camera_report.take,
                    score=score,
                    is_recommended=score >= 0.7,
                    recommended_reason=self._recommended_reason(score, script_note, director_note),
                    camera_asset_id=camera_asset.id if camera_asset else None,
                    sound_asset_id=audio_asset.id if audio_asset else None,
                )
            )
            if audio_asset:
                timecode_offset_frames = self._timecode_offset_frames(
                    camera_asset.start_timecode if camera_asset else "00:00:00:00",
                    sound_report.timecode_start,
                    camera_report.fps,
                )
                sync_candidates.append(
                    SyncCandidate(
                        audio_asset_id=audio_asset.id,
                        audio_filename=audio_asset.file_name,
                        timecode_offset_frames=timecode_offset_frames,
                        sync_confidence=0.9 if camera_asset else 0.65,
                        sync_method="scene_take_report_match",
                    )
                )

        if not camera_reports and media_assets:
            warnings.append("no_camera_reports_provided")

        return slate_matches, take_decisions, sync_candidates, warnings

    def build_neutral_assembly(
        self,
        *,
        project_id: str,
        take_decisions: list[TakeDecision],
        media_assets: list[EditorialMediaAsset],
        name: str = "CID Neutral Assembly",
        fps: float = 24.0,
        allow_missing_audio: bool = True,
    ) -> AssemblyTimeline:
        assets_by_id = {asset.id: asset for asset in media_assets}
        recommended = [decision for decision in take_decisions if decision.is_recommended]
        if not recommended:
            recommended = sorted(take_decisions, key=lambda decision: decision.score, reverse=True)[:1]

        sequences: dict[int, list[AssemblyClip]] = {}
        cursor = 0
        for decision in sorted(recommended, key=lambda item: (item.scene_number, item.shot_number, item.take_number)):
            if not decision.camera_asset_id:
                continue
            if not allow_missing_audio and not decision.sound_asset_id:
                continue
            camera_asset = assets_by_id.get(decision.camera_asset_id)
            if camera_asset is None:
                continue
            audio_asset = assets_by_id.get(decision.sound_asset_id) if decision.sound_asset_id else None
            duration = camera_asset.duration_frames or max(1, int((camera_asset.fps or fps) * 4))
            clip = AssemblyClip(
                id=f"clip-{decision.take_id}",
                take_id=decision.take_id,
                clip_name=f"S{decision.scene_number}_SH{decision.shot_number}_TK{decision.take_number}",
                source_media_asset_id=decision.camera_asset_id,
                audio_media_asset_id=decision.sound_asset_id,
                timeline_in=cursor,
                timeline_out=cursor + duration,
                duration_frames=duration,
                fps=camera_asset.fps or fps,
                start_tc=camera_asset.start_timecode,
                timecode_offset_frames=self._timecode_offset_frames(
                    camera_asset.start_timecode,
                    audio_asset.start_timecode if audio_asset else None,
                    camera_asset.fps or fps,
                ),
                assigned_tracks=self._assigned_tracks(audio_asset),
            )
            sequences.setdefault(decision.scene_number, []).append(clip)
            cursor += duration

        return AssemblyTimeline(
            id=f"assembly-{uuid4().hex[:12]}",
            project_id=project_id,
            name=name,
            fps=fps,
            total_duration_frames=cursor,
            sequences=[
                AssemblySequence(
                    id=f"seq-{scene_number}",
                    name=f"Scene {scene_number}",
                    scene_number=scene_number,
                    clips=clips,
                )
                for scene_number, clips in sorted(sequences.items())
            ],
        )

    def generate_relink_report(
        self,
        *,
        timeline: AssemblyTimeline,
        media_assets: list[EditorialMediaAsset],
        destination_root_path: str | None = None,
    ) -> tuple[RelinkReport, list[MissingMediaReport]]:
        assets_by_id = {asset.id: asset for asset in media_assets}
        path_mappings: dict[str, str] = {}
        missing: list[MissingMediaReport] = []
        resolved_count = 0

        for clip in self._iter_clips(timeline):
            for role, asset_id in (("video", clip.source_media_asset_id), ("audio", clip.audio_media_asset_id)):
                if not asset_id:
                    if role == "audio":
                        missing.append(self._missing_report(clip, role, "external_audio.wav"))
                    continue
                asset = assets_by_id.get(asset_id)
                if asset is None:
                    missing.append(self._missing_report(clip, role, asset_id))
                    continue
                resolved_count += 1
                if destination_root_path:
                    path_mappings[asset.file_path] = str(Path(destination_root_path) / asset.file_name)

        return (
            RelinkReport(
                resolved_media_count=resolved_count,
                offline_media_count=0,
                missing_media_count=len(missing),
                path_mappings=path_mappings,
            ),
            missing,
        )

    def _asset_type(self, suffix: str) -> str:
        normalized = suffix.lower()
        if normalized in VIDEO_EXTENSIONS:
            return "video"
        if normalized in AUDIO_EXTENSIONS:
            return "audio"
        return "other"

    def _find_sound_report(
        self,
        camera_report: CameraReportEntry,
        sound_reports: list[SoundReportEntry],
    ) -> SoundReportEntry | None:
        for report in sound_reports:
            if (
                report.scene == camera_report.scene
                and report.shot == camera_report.shot
                and report.take == camera_report.take
            ):
                return report
        for report in sound_reports:
            if report.shot is None and report.scene == camera_report.scene and report.take == camera_report.take:
                return report
        return None

    def _find_script_note(
        self,
        camera_report: CameraReportEntry,
        script_notes: list[ScriptSupervisorNote],
    ) -> ScriptSupervisorNote | None:
        for note in script_notes:
            if (
                note.scene_number == camera_report.scene
                and note.shot_number == camera_report.shot
                and note.take_number == camera_report.take
            ):
                return note
        return None

    def _find_director_note(
        self,
        camera_report: CameraReportEntry,
        director_notes: list[DirectorNote],
    ) -> DirectorNote | None:
        for note in director_notes:
            if (
                note.scene_number == camera_report.scene
                and note.shot_number == camera_report.shot
                and note.take_number == camera_report.take
            ):
                return note
        return None

    def _find_audio_asset(
        self,
        sound_report: SoundReportEntry | None,
        audio_assets: list[EditorialMediaAsset],
    ) -> EditorialMediaAsset | None:
        if sound_report is None:
            return None
        for asset in audio_assets:
            if asset.file_name.lower() == sound_report.file_name.lower():
                return asset
        return None

    def _score_take(
        self,
        script_note: ScriptSupervisorNote | None,
        director_note: DirectorNote | None,
        has_camera: bool,
        has_audio: bool,
    ) -> float:
        score = 0.35
        if has_camera:
            score += 0.2
        if has_audio:
            score += 0.15
        if script_note and script_note.is_circled:
            score += 0.15
        if director_note and director_note.is_preferred:
            score += 0.15
        return min(score, 1.0)

    def _timecode_offset_frames(self, video_tc: str | None, audio_tc: str | None, fps: float) -> int:
        if not video_tc or not audio_tc:
            return 0
        return self._timecode_to_frames(audio_tc, fps) - self._timecode_to_frames(video_tc, fps)

    def _timecode_to_frames(self, timecode: str, fps: float) -> int:
        parts = timecode.split(":")
        if len(parts) != 4:
            return 0
        try:
            hours, minutes, seconds, frames = [int(part) for part in parts]
        except ValueError:
            return 0
        fps_int = max(1, int(round(fps or 24.0)))
        return ((hours * 3600) + (minutes * 60) + seconds) * fps_int + frames

    def _assigned_tracks(self, audio_asset: EditorialMediaAsset | None) -> list[str]:
        if audio_asset is None:
            return ["V1"]
        channels = max(1, int(audio_asset.channels or 1))
        audio_tracks = [f"A{index}" for index in range(1, min(channels, 8) + 1)]
        return ["V1", *audio_tracks]

    def _recommended_reason(
        self,
        score: float,
        script_note: ScriptSupervisorNote | None,
        director_note: DirectorNote | None,
    ) -> str:
        reasons = []
        if script_note and script_note.is_circled:
            reasons.append("circled_take")
        if director_note and director_note.is_preferred:
            reasons.append("director_preferred")
        if score >= 0.7:
            reasons.append("score_threshold")
        return ",".join(reasons) or "metadata_available"

    def _iter_clips(self, timeline: AssemblyTimeline) -> Iterable[AssemblyClip]:
        for sequence in timeline.sequences:
            yield from sequence.clips

    def _missing_report(self, clip: AssemblyClip, role: str, expected_filename: str) -> MissingMediaReport:
        scene, shot, take = self._parse_clip_name(clip.clip_name)
        return MissingMediaReport(
            clip_name=clip.clip_name,
            role=role,  # type: ignore[arg-type]
            expected_filename=expected_filename,
            scene=scene,
            shot=shot,
            take=take,
        )

    def _parse_clip_name(self, clip_name: str) -> tuple[int, int, int]:
        match = re.search(r"S(\d+)_SH(\d+)_TK(\d+)", clip_name, re.IGNORECASE)
        if not match:
            return 0, 0, 0
        return int(match.group(1)), int(match.group(2)), int(match.group(3))


editorial_assembly_core_service = EditorialAssemblyCoreService()
