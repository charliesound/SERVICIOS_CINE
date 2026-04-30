from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.postproduction import Take
from models.report import CameraReport, DirectorNote, ScriptNote, SoundReport
from models.storage import MediaAsset, MediaAssetType
from services.audio_metadata_service import AudioMetadataResult, audio_metadata_service


@dataclass
class ReconcileBucket:
    project_id: str
    organization_id: str
    scene_number: Optional[int]
    shot_number: Optional[int]
    take_number: Optional[int]
    camera_asset: Optional[MediaAsset] = None
    sound_asset: Optional[MediaAsset] = None
    camera_report: Optional[CameraReport] = None
    sound_report: Optional[SoundReport] = None
    script_note: Optional[ScriptNote] = None
    director_note: Optional[DirectorNote] = None
    audio_metadata: Optional[AudioMetadataResult] = None
    sync_method: Optional[str] = None
    sync_confidence: Optional[float] = None
    dual_system_status: Optional[str] = None
    sync_warning: Optional[str] = None
    warnings: list[str] = field(default_factory=list)


class EditorialReconciliationService:
    async def reconcile_project(
        self,
        db: AsyncSession,
        *,
        project: Project,
    ) -> dict[str, Any]:
        assets = list(
            (
                await db.execute(
                    select(MediaAsset).where(MediaAsset.project_id == str(project.id)).order_by(MediaAsset.created_at.asc())
                )
            ).scalars().all()
        )
        camera_reports = list(
            (
                await db.execute(select(CameraReport).where(CameraReport.project_id == str(project.id)).order_by(CameraReport.created_at.asc()))
            ).scalars().all()
        )
        sound_reports = list(
            (
                await db.execute(select(SoundReport).where(SoundReport.project_id == str(project.id)).order_by(SoundReport.created_at.asc()))
            ).scalars().all()
        )
        script_notes = list(
            (
                await db.execute(select(ScriptNote).where(ScriptNote.project_id == str(project.id)).order_by(ScriptNote.created_at.asc()))
            ).scalars().all()
        )
        director_notes = list(
            (
                await db.execute(select(DirectorNote).where(DirectorNote.project_id == str(project.id)).order_by(DirectorNote.created_at.asc()))
            ).scalars().all()
        )

        buckets: dict[tuple[Optional[int], Optional[int], Optional[int]], ReconcileBucket] = {}
        total_reports_considered = len(camera_reports) + len(sound_reports) + len(script_notes) + len(director_notes)

        camera_assets = [asset for asset in assets if str(asset.asset_type) != MediaAssetType.AUDIO]
        audio_assets = [asset for asset in assets if str(asset.asset_type) == MediaAssetType.AUDIO]

        for asset in camera_assets:
            key, warnings, _attrs = self._asset_key(asset=asset, prefer_audio=False)
            bucket = self._bucket_for_key(buckets, key, project)
            bucket.warnings.extend(warnings)
            bucket.camera_asset = asset

        for report in camera_reports:
            key = self._report_key(report.scene_id, report.shot_id, report.take_reference)
            self._bucket_for_key(buckets, key, project).camera_report = report

        for report in script_notes:
            key = self._report_key(report.scene_id, report.shot_id, report.best_take)
            self._bucket_for_key(buckets, key, project).script_note = report

        for report in director_notes:
            key = self._report_key(report.scene_id, report.shot_id, report.preferred_take)
            self._bucket_for_key(buckets, key, project).director_note = report

        for asset in audio_assets:
            audio_metadata = audio_metadata_service.get_audio_metadata(asset)
            matched_key, method, confidence, warnings = self._match_audio_bucket(buckets, asset, audio_metadata, project)
            bucket = self._bucket_for_key(buckets, matched_key, project)
            bucket.sound_asset = asset
            bucket.audio_metadata = audio_metadata
            bucket.sync_method = method
            bucket.sync_confidence = confidence
            bucket.warnings.extend(warnings)

        for report in sound_reports:
            key, method = self._match_sound_report_bucket(buckets, report, project)
            bucket = self._bucket_for_key(buckets, key, project)
            bucket.sound_report = report
            if bucket.sync_method is None:
                bucket.sync_method = method
                bucket.sync_confidence = self._method_confidence(method)

        existing_result = await db.execute(select(Take).where(Take.project_id == str(project.id)))
        existing_takes = {
            (take.scene_number, take.shot_number, take.take_number): take
            for take in existing_result.scalars().all()
        }

        takes_created = 0
        takes_updated = 0
        conflicts: list[dict[str, Any]] = []
        for key, bucket in buckets.items():
            take = existing_takes.get(key)
            if take is None:
                take = Take(
                    project_id=str(project.id),
                    organization_id=str(project.organization_id),
                    scene_number=bucket.scene_number,
                    shot_number=bucket.shot_number,
                    take_number=bucket.take_number,
                )
                db.add(take)
                takes_created += 1
            else:
                takes_updated += 1
            self._apply_bucket_to_take(take, bucket)
            if take.reconciliation_status == "conflict":
                conflicts.append(
                    {
                        "scene_number": take.scene_number,
                        "shot_number": take.shot_number,
                        "take_number": take.take_number,
                        "warnings": json.loads(take.conflict_flags_json or "[]"),
                    }
                )
        await db.commit()

        final_total = await db.execute(select(Take).where(Take.project_id == str(project.id)))
        warnings = sorted({warning for bucket in buckets.values() for warning in bucket.warnings if warning})
        return {
            "project_id": str(project.id),
            "total_assets_considered": len(assets),
            "total_reports_considered": total_reports_considered,
            "takes_created": takes_created,
            "takes_updated": takes_updated,
            "total_takes": len(final_total.scalars().all()),
            "conflicts": conflicts,
            "warnings": warnings,
        }

    def _bucket_for_key(
        self,
        buckets: dict[tuple[Optional[int], Optional[int], Optional[int]], ReconcileBucket],
        key: tuple[Optional[int], Optional[int], Optional[int]],
        project: Project,
    ) -> ReconcileBucket:
        return buckets.setdefault(
            key,
            ReconcileBucket(
                project_id=str(project.id),
                organization_id=str(project.organization_id),
                scene_number=key[0],
                shot_number=key[1],
                take_number=key[2],
            ),
        )

    def _apply_bucket_to_take(self, take: Take, bucket: ReconcileBucket) -> None:
        warnings = list(bucket.warnings)
        take.scene_number = bucket.scene_number
        take.shot_number = bucket.shot_number
        take.take_number = bucket.take_number
        if bucket.camera_asset is not None:
            take.camera_media_asset_id = str(bucket.camera_asset.id)
            take.video_filename = str(bucket.camera_asset.file_name)
            take.start_timecode = take.start_timecode or self._metadata_value(bucket.camera_asset, "start_timecode")
            take.end_timecode = take.end_timecode or self._metadata_value(bucket.camera_asset, "end_timecode")
            take.duration_frames = take.duration_frames or self._int_value(self._metadata_value(bucket.camera_asset, "duration_frames"))
            take.fps = take.fps or self._float_value(self._metadata_value(bucket.camera_asset, "fps"))
            take.camera_roll = take.camera_roll or self._metadata_value(bucket.camera_asset, "camera_roll")
            take.slate = take.slate or self._metadata_value(bucket.camera_asset, "slate")
        if bucket.sound_asset is not None:
            take.sound_media_asset_id = str(bucket.sound_asset.id)
            take.audio_filename = str(bucket.sound_asset.file_name)
            take.sound_roll = take.sound_roll or self._metadata_value(bucket.sound_asset, "sound_roll")

        if bucket.audio_metadata is not None:
            audio = bucket.audio_metadata
            take.audio_metadata_status = audio.status
            take.audio_metadata_json = json.dumps(audio.to_dict())
            take.audio_timecode_start = audio.timecode
            take.audio_time_reference_samples = audio.time_reference_samples
            take.audio_sample_rate = audio.sample_rate
            take.audio_channels = audio.channels
            take.audio_duration_seconds = audio.duration_seconds
            take.audio_fps = audio.fps
            take.audio_scene = audio.scene
            take.audio_take = audio.take
            take.audio_circled = audio.circled
            take.sound_roll = take.sound_roll or audio.sound_roll
            if take.fps is None:
                take.fps = audio.fps
            if take.start_timecode is None:
                take.start_timecode = audio.timecode
            if take.duration_frames is None and audio.duration_seconds and (take.fps or audio.fps):
                take.duration_frames = max(1, int(round(audio.duration_seconds * float(take.fps or audio.fps or 24.0))))
            if audio.status in {"error", "unsupported"}:
                warnings.append(f"audio_metadata_{audio.status}")

        if bucket.camera_report is not None:
            take.camera_report_id = str(bucket.camera_report.id)
            take.camera_roll = take.camera_roll or bucket.camera_report.card_or_mag
            take.camera_status = self._camera_status(bucket.camera_report)
            take.notes = self._append_text(take.notes, bucket.camera_report.notes, bucket.camera_report.incidents)
        if bucket.sound_report is not None:
            take.sound_report_id = str(bucket.sound_report.id)
            take.sound_roll = take.sound_roll or bucket.sound_report.sound_roll
            take.sound_status = self._sound_status(bucket.sound_report)
            take.notes = self._append_text(take.notes, bucket.sound_report.notes, bucket.sound_report.incidents)
            if not take.start_timecode:
                take.start_timecode = self._extract_timecode(bucket.sound_report.timecode_notes)
        if bucket.script_note is not None:
            take.script_note_id = str(bucket.script_note.id)
            take.script_status = self._script_status(bucket.script_note)
            take.is_circled = take.is_circled or take.script_status in {"circled", "best", "good"}
            take.is_best = take.is_best or take.script_status == "best"
            take.notes = self._append_text(take.notes, bucket.script_note.continuity_notes, bucket.script_note.editor_note)
        if bucket.director_note is not None:
            take.director_note_id = str(bucket.director_note.id)
            take.director_status = self._director_status(bucket.director_note)
            take.is_best = take.is_best or take.director_status in {"preferred", "best"}
            take.notes = self._append_text(take.notes, bucket.director_note.intention_note, bucket.director_note.pacing_note, bucket.director_note.coverage_note)

        take.sync_method = bucket.sync_method or ("exact_scene_shot_take" if take.camera_media_asset_id and take.sound_media_asset_id else "unresolved")
        take.sync_confidence = bucket.sync_confidence if bucket.sync_confidence is not None else self._method_confidence(take.sync_method)
        take.sync_warning = bucket.sync_warning

        if take.scene_number is None:
            warnings.append("missing_scene_number")
        if take.shot_number is None:
            warnings.append("missing_shot_number")
        if take.take_number is None:
            warnings.append("missing_take_number")
        if take.camera_media_asset_id is None:
            warnings.append("missing_camera")
        if take.sound_media_asset_id is None:
            warnings.append("missing_audio")
        if take.sync_method == "timecode_near":
            warnings.append("timecode_near_match")
        if take.sync_method == "manual_fallback":
            warnings.append("manual_sync_fallback")
        if take.audio_metadata_status in {"partial", "unsupported"}:
            warnings.append("audio_metadata_partial")

        unique_warnings = sorted(set(warnings))
        take.conflict_flags_json = json.dumps(unique_warnings)
        take.dual_system_status = self._dual_system_status(take, unique_warnings)
        if take.dual_system_status == "conflict":
            take.reconciliation_status = "conflict"
        elif take.dual_system_status in {"missing_audio", "missing_camera", "partial", "metadata_warning"}:
            take.reconciliation_status = "partial"
        else:
            take.reconciliation_status = "matched"
        if take.duration_frames is None:
            take.duration_frames = max(1, int((take.fps or 24.0) * 4))

    def _match_audio_bucket(
        self,
        buckets: dict[tuple[Optional[int], Optional[int], Optional[int]], ReconcileBucket],
        asset: MediaAsset,
        audio_metadata: AudioMetadataResult,
        project: Project,
    ) -> tuple[tuple[Optional[int], Optional[int], Optional[int]], str, float, list[str]]:
        metadata = self._parse_metadata(asset)
        scene = self._int_value(metadata.get("scene_number"), audio_metadata.scene)
        shot = self._int_value(metadata.get("shot_number"), audio_metadata.shot)
        take = self._int_value(metadata.get("take_number"), audio_metadata.take)
        candidate_key = (scene, shot, take)
        warnings: list[str] = []

        if candidate_key in buckets and None not in candidate_key:
            return candidate_key, "exact_scene_shot_take", 0.98, warnings

        for key, bucket in buckets.items():
            if scene is not None and take is not None and bucket.scene_number == scene and bucket.take_number == take:
                return key, "ixml_scene_take", 0.92, warnings

        slate = self._text_value(metadata.get("slate"), audio_metadata.notes)
        if slate:
            for key, bucket in buckets.items():
                bucket_slate = None
                if bucket.camera_asset is not None:
                    bucket_slate = self._metadata_value(bucket.camera_asset, "slate")
                if bucket_slate and slate.lower() in bucket_slate.lower():
                    return key, "slate_match", 0.85, warnings

        if audio_metadata.sound_roll and take is not None:
            for key, bucket in buckets.items():
                bucket_roll = None
                if bucket.sound_report is not None:
                    bucket_roll = bucket.sound_report.sound_roll
                elif bucket.camera_report is not None:
                    bucket_roll = bucket.camera_report.card_or_mag
                if bucket_roll and str(bucket_roll).lower() == str(audio_metadata.sound_roll).lower() and bucket.take_number == take:
                    return key, "sound_roll_take", 0.82, warnings

        filename_key = self._filename_key(str(asset.file_name))
        if filename_key:
            for key in buckets:
                if filename_key == self._bucket_filename_key(key):
                    return key, "filename_match", 0.75, warnings

        if audio_metadata.timecode:
            for key, bucket in buckets.items():
                camera_tc = self._metadata_value(bucket.camera_asset, "start_timecode") if bucket.camera_asset is not None else None
                if camera_tc and self._timecode_near(camera_tc, audio_metadata.timecode):
                    warnings.append("approximate_timecode_match")
                    return key, "timecode_near", 0.65, warnings

        if buckets:
            first_key = next(iter(buckets.keys()))
            warnings.append("manual_dual_system_fallback")
            return first_key, "manual_fallback", 0.4, warnings

        warnings.append(f"asset_unresolved:{asset.file_name}")
        return candidate_key, "unresolved", 0.0, warnings

    def _match_sound_report_bucket(
        self,
        buckets: dict[tuple[Optional[int], Optional[int], Optional[int]], ReconcileBucket],
        report: SoundReport,
        project: Project,
    ) -> tuple[tuple[Optional[int], Optional[int], Optional[int]], str]:
        take_ref = self._extract_take_reference(
            getattr(report, "timecode_notes", None),
            getattr(report, "notes", None),
            getattr(report, "incidents", None),
        )
        exact_key = self._report_key(report.scene_id, report.shot_id, take_ref)
        if exact_key in buckets and None not in exact_key:
            return exact_key, "exact_scene_shot_take"
        if report.sound_roll and take_ref:
            for key, bucket in buckets.items():
                if bucket.take_number == self._int_value(take_ref) and bucket.sound_asset is not None:
                    return key, "sound_roll_take"
        return exact_key, "manual_fallback"

    def _asset_key(self, *, asset: MediaAsset, prefer_audio: bool) -> tuple[tuple[Optional[int], Optional[int], Optional[int]], list[str], dict[str, Any]]:
        metadata = self._parse_metadata(asset)
        scene_number = self._int_value(metadata.get("scene_number")) or self._extract_number(str(asset.file_name), r"scene[_\- ]?(\d+)")
        shot_number = self._int_value(metadata.get("shot_number")) or self._extract_number(str(asset.file_name), r"shot[_\- ]?(\d+)")
        take_number = self._int_value(metadata.get("take_number")) or self._extract_number(str(asset.file_name), r"take[_\- ]?(\d+)")
        warnings: list[str] = []
        if scene_number is None or shot_number is None or take_number is None:
            warnings.append(f"asset_unresolved:{asset.file_name}")
        attrs = {"asset_type": str(asset.asset_type), "metadata": metadata, "prefer_audio": prefer_audio}
        return (scene_number, shot_number, take_number), warnings, attrs

    def _report_key(self, scene_id: Optional[str], shot_id: Optional[str], take_reference: Optional[str]) -> tuple[Optional[int], Optional[int], Optional[int]]:
        return (
            self._int_value(scene_id),
            self._int_value(shot_id),
            self._int_value(take_reference),
        )

    def _parse_metadata(self, asset: MediaAsset) -> dict[str, Any]:
        if not asset.metadata_json:
            return {}
        try:
            return json.loads(asset.metadata_json)
        except Exception:
            return {}

    def _metadata_value(self, asset: MediaAsset | None, key: str) -> Optional[str]:
        if asset is None:
            return None
        value = self._parse_metadata(asset).get(key)
        if value is None:
            return None
        return str(value)

    def _extract_timecode(self, raw_value: Optional[str]) -> Optional[str]:
        if not raw_value:
            return None
        match = re.search(r"\b\d{2}:\d{2}:\d{2}:\d{2}\b", raw_value)
        return match.group(0) if match else None

    def _extract_take_reference(self, *values: Optional[str]) -> Optional[str]:
        for value in values:
            if not value:
                continue
            match = re.search(r"take\s*[:\- ]?\s*(\d+)", value, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _extract_number(self, raw_value: str, pattern: str) -> Optional[int]:
        match = re.search(pattern, raw_value, re.IGNORECASE)
        if not match:
            return None
        try:
            return int(match.group(1))
        except Exception:
            return None

    def _append_text(self, base: Optional[str], *values: Optional[str]) -> Optional[str]:
        parts = [base] if base else []
        for value in values:
            if value:
                parts.append(value)
        if not parts:
            return None
        unique_parts: list[str] = []
        for part in parts:
            cleaned = part.strip()
            if cleaned and cleaned not in unique_parts:
                unique_parts.append(cleaned)
        return " | ".join(unique_parts) if unique_parts else None

    def _script_status(self, report: ScriptNote) -> str:
        note_text = " ".join(filter(None, [report.continuity_notes, report.editor_note])).lower()
        best_take = self._int_value(report.best_take)
        current_take = self._int_value(report.best_take)
        if best_take is not None and current_take == best_take:
            return "best"
        if "circled" in note_text or "circle" in note_text:
            return "circled"
        if "good" in note_text:
            return "good"
        if "ng" in note_text:
            return "ng"
        return "noted"

    def _director_status(self, report: DirectorNote) -> str:
        text = " ".join(filter(None, [report.intention_note, report.pacing_note, report.coverage_note])).lower()
        if report.preferred_take:
            return "preferred"
        if "best" in text:
            return "best"
        if "ng" in text or "reject" in text:
            return "ng"
        return "noted"

    def _camera_status(self, report: CameraReport) -> str:
        text = " ".join(filter(None, [report.notes, report.incidents])).lower()
        if any(token in text for token in ("focus issue", "soft focus", "out of focus", "ng")):
            return "issue"
        return "ok"

    def _sound_status(self, report: SoundReport) -> str:
        text = " ".join(filter(None, [report.notes, report.incidents, report.timecode_notes])).lower()
        if any(token in text for token in ("noise", "distortion", "rf", "dropout", "ng")):
            return "issue"
        return "clean"

    def _int_value(self, *values: Any) -> Optional[int]:
        for value in values:
            if value is None:
                continue
            match = re.search(r"(\d+)", str(value))
            if not match:
                continue
            try:
                return int(match.group(1))
            except Exception:
                continue
        return None

    def _float_value(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _text_value(self, *values: Any) -> Optional[str]:
        for value in values:
            if value is None:
                continue
            text = str(value).strip()
            if text:
                return text
        return None

    def _filename_key(self, raw_value: str) -> tuple[Optional[int], Optional[int], Optional[int]] | None:
        scene = self._extract_number(raw_value, r"scene[_\- ]?(\d+)")
        shot = self._extract_number(raw_value, r"shot[_\- ]?(\d+)")
        take = self._extract_number(raw_value, r"take[_\- ]?(\d+)")
        if scene is None and shot is None and take is None:
            return None
        return (scene, shot, take)

    def _bucket_filename_key(self, key: tuple[Optional[int], Optional[int], Optional[int]]) -> tuple[Optional[int], Optional[int], Optional[int]]:
        return key

    def _timecode_near(self, left: str, right: str) -> bool:
        return left[:8] == right[:8]

    def _method_confidence(self, method: str | None) -> float:
        mapping = {
            "exact_scene_shot_take": 0.98,
            "ixml_scene_take": 0.92,
            "slate_match": 0.85,
            "sound_roll_take": 0.82,
            "filename_match": 0.75,
            "timecode_near": 0.65,
            "manual_fallback": 0.4,
            "unresolved": 0.0,
        }
        return mapping.get(str(method or "unresolved"), 0.0)

    def _dual_system_status(self, take: Take, warnings: list[str]) -> str:
        if take.camera_media_asset_id and take.sound_media_asset_id:
            if take.sync_method == "unresolved":
                return "conflict"
            if any(flag in warnings for flag in ("manual_sync_fallback", "approximate_timecode_match", "audio_metadata_partial")):
                return "metadata_warning"
            return "matched"
        if take.camera_media_asset_id and not take.sound_media_asset_id:
            return "missing_audio"
        if take.sound_media_asset_id and not take.camera_media_asset_id:
            return "missing_camera"
        return "conflict"


editorial_reconciliation_service = EditorialReconciliationService()
