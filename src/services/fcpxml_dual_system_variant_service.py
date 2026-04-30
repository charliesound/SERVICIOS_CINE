from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


class FCPXMLDualSystemVariantService:
    """
    Variant FCPXML service for dual-system audio.
    Generates two variants:
    - assembly_conservative.fcpxml: current behavior (audio as resource note only)
    - assembly_linked_audio_experimental.fcpxml: attempts linked audio sync
    """

    def build_fcpxml_variants(
        self,
        *,
        project_name: str,
        assembly_cut: dict[str, Any],
        resolved_assets: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[bytes, bytes, str, str, dict[str, Any]]:
        assembly = assembly_cut["assembly_cut"]
        items = assembly.get("items", [])
        fps = self._resolve_fps(items)
        total_duration = sum(int(item.get("duration_frames") or 0) for item in items) or int(fps * 4)

        conservative_xml, conservative_name = self._build_conservative_fcpxml(
            project_name=project_name,
            assembly=assembly,
            items=items,
            fps=fps,
            total_duration=total_duration,
            resolved_assets=resolved_assets,
        )

        experimental_xml, experimental_name = self._build_linked_audio_fcpxml(
            project_name=project_name,
            assembly=assembly,
            items=items,
            fps=fps,
            total_duration=total_duration,
            resolved_assets=resolved_assets,
        )

        manifest = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "project_name": project_name,
            "assembly_cut_id": assembly.get("id"),
            "clip_count": len(items),
            "fps": fps,
            "variants": {
                "conservative": {
                    "filename": conservative_name,
                    "linked_audio": False,
                    "audio_state": "resource_note_only",
                },
                "experimental": {
                    "filename": experimental_name,
                    "linked_audio": True,
                    "audio_state": "synchronized_track_attempted",
                },
            },
            "resolved_media_count": sum(
                1 for item in resolved_assets.values() if item.get("status") == "resolved"
            )
            if resolved_assets
            else 0,
        }

        return conservative_xml, experimental_xml, conservative_name, experimental_name, manifest

    def _build_conservative_fcpxml(
        self,
        *,
        project_name: str,
        assembly: dict[str, Any],
        items: list[dict[str, Any]],
        fps: float,
        total_duration: int,
        resolved_assets: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[bytes, str]:
        fcpxml = ET.Element("fcpxml", version="1.10")
        resources = ET.SubElement(fcpxml, "resources")
        ET.SubElement(
            resources,
            "format",
            id="r1",
            name=f"FFVideoFormat{int(round(fps))}p",
            frameDuration=self._frame_duration(fps),
            width="1920",
            height="1080",
        )

        asset_ids: dict[str, str] = {}
        audio_asset_ids: dict[str, str] = {}
        warnings: list[str] = []
        resolved_assets = resolved_assets or {}
        next_resource_index = 2

        for item in items:
            asset_id = f"r{next_resource_index}"
            next_resource_index += 1
            asset_ids[str(item.get("id"))] = asset_id
            source_asset_id = str(item.get("source_media_asset_id") or "")
            resolution = resolved_assets.get(source_asset_id, {}) if source_asset_id else {}
            if resolution.get("status") != "resolved":
                warnings.append(
                    f"offline_media:{self._asset_name(item)}:{resolution.get('reason') or 'unresolved_source_media'}"
                )
            ET.SubElement(
                resources,
                "asset",
                id=asset_id,
                name=self._asset_name(item),
                src=self._asset_src(item, resolution=resolution),
                start="0s",
                duration=self._frames_to_duration(int(item.get("duration_frames") or int(fps * 4)), fps),
                hasVideo="1",
                hasAudio="1" if item.get("audio_media_asset_id") else "0",
                format="r1",
            )
            audio_asset_id = str(item.get("audio_media_asset_id") or "")
            if audio_asset_id and audio_asset_id != source_asset_id and audio_asset_id not in audio_asset_ids:
                audio_resolution = resolved_assets.get(audio_asset_id, {})
                audio_resource_id = f"r{next_resource_index}"
                next_resource_index += 1
                audio_asset_ids[audio_asset_id] = audio_resource_id
                ET.SubElement(
                    resources,
                    "asset",
                    id=audio_resource_id,
                    name=self._asset_name(item) + "_AUDIO",
                    src=self._asset_src(item, resolution=audio_resolution, role="audio"),
                    start="0s",
                    duration=self._frames_to_duration(int(item.get("duration_frames") or int(fps * 4)), fps),
                    hasVideo="0",
                    hasAudio="1",
                    format="r1",
                )
                warnings.append("dual_system_audio_export_partial")

        library = ET.SubElement(fcpxml, "library")
        event = ET.SubElement(library, "event", name=project_name)
        project = ET.SubElement(event, "project", name=assembly.get("name") or f"{project_name} Assembly")
        sequence = ET.SubElement(
            project,
            "sequence",
            format="r1",
            duration=self._frames_to_duration(total_duration, fps),
            tcStart="0s",
            tcFormat="NDF",
            audioLayout="stereo",
            audioRate="48k",
        )
        spine = ET.SubElement(sequence, "spine")

        for item in items:
            duration_frames = int(item.get("duration_frames") or int(fps * 4))
            clip = ET.SubElement(
                spine,
                "asset-clip",
                name=self._asset_name(item),
                ref=asset_ids[str(item.get("id"))],
                offset=self._frames_to_duration(int(item.get("timeline_in") or 0), fps, allow_zero=True),
                start="0s",
                duration=self._frames_to_duration(duration_frames, fps),
                tcFormat="NDF",
            )
            note = item.get("recommended_reason")
            audio_note = None
            audio_asset_id = str(item.get("audio_media_asset_id") or "")
            source_asset_id = str(item.get("source_media_asset_id") or "")
            if audio_asset_id and audio_asset_id != source_asset_id:
                audio_resolution = resolved_assets.get(audio_asset_id, {})
                audio_note = (
                    f"external audio: {audio_resolution.get('filename') or audio_asset_id}; "
                    "dual_system_audio_export_partial"
                )
            if note:
                ET.SubElement(clip, "note").text = str(note if not audio_note else f"{note}; {audio_note}")
            elif audio_note:
                ET.SubElement(clip, "note").text = audio_note

        xml_bytes = ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
        file_name = f"{project_name.replace(' ', '_')}_conservative.fcpxml"
        return xml_bytes, file_name

    def _build_linked_audio_fcpxml(
        self,
        *,
        project_name: str,
        assembly: dict[str, Any],
        items: list[dict[str, Any]],
        fps: float,
        total_duration: int,
        resolved_assets: dict[str, dict[str, Any]] | None = None,
    ) -> tuple[bytes, str]:
        fcpxml = ET.Element("fcpxml", version="1.10")
        resources = ET.SubElement(fcpxml, "resources")
        ET.SubElement(
            resources,
            "format",
            id="r1",
            name=f"FFVideoFormat{int(round(fps))}p",
            frameDuration=self._frame_duration(fps),
            width="1920",
            height="1080",
        )

        asset_ids: dict[str, str] = {}
        audio_asset_ids: dict[str, str] = {}
        audio_timecodes: dict[str, dict[str, Any]] = {}
        warnings: list[str] = []
        resolved_assets = resolved_assets or {}
        next_resource_index = 2

        for item in items:
            asset_id = f"r{next_resource_index}"
            next_resource_index += 1
            asset_ids[str(item.get("id"))] = asset_id
            source_asset_id = str(item.get("source_media_asset_id") or "")
            resolution = resolved_assets.get(source_asset_id, {}) if source_asset_id else {}
            if resolution.get("status") != "resolved":
                warnings.append(
                    f"offline_media:{self._asset_name(item)}:{resolution.get('reason') or 'unresolved_source_media'}"
                )
            ET.SubElement(
                resources,
                "asset",
                id=asset_id,
                name=self._asset_name(item),
                src=self._asset_src(item, resolution=resolution),
                start="0s",
                duration=self._frames_to_duration(int(item.get("duration_frames") or int(fps * 4)), fps),
                hasVideo="1",
                hasAudio="0",
                format="r1",
            )
            audio_asset_id = str(item.get("audio_media_asset_id") or "")
            if audio_asset_id and audio_asset_id != source_asset_id:
                audio_resolution = resolved_assets.get(audio_asset_id, {})
                audio_resource_id = f"r{next_resource_index}"
                next_resource_index += 1
                audio_asset_ids[audio_asset_id] = audio_resource_id

                audio_tc = item.get("audio_start_tc") or item.get("start_tc")
                audio_duration = item.get("audio_duration_frames") or item.get("duration_frames")
                audio_timecodes[audio_resource_id] = {
                    "start_tc": audio_tc,
                    "duration_frames": audio_duration,
                    "filename": audio_resolution.get("filename"),
                }

                ET.SubElement(
                    resources,
                    "asset",
                    id=audio_resource_id,
                    name=self._asset_name(item) + "_LINKED_AUDIO",
                    src=self._asset_src(item, resolution=audio_resolution, role="audio"),
                    start="0s",
                    duration=self._frames_to_duration(
                        int(audio_duration or item.get("duration_frames") or int(fps * 4)), fps
                    ),
                    hasVideo="0",
                    hasAudio="1",
                    format="r1",
                )

        library = ET.SubElement(fcpxml, "library")
        event = ET.SubElement(library, "event", name=project_name)
        project = ET.SubElement(event, "project", name=assembly.get("name") or f"{project_name} Assembly")
        sequence = ET.SubElement(
            project,
            "sequence",
            format="r1",
            duration=self._frames_to_duration(total_duration, fps),
            tcStart="0s",
            tcFormat="NDF",
            audioLayout="stereo",
            audioRate="48k",
        )

        spine = ET.SubElement(sequence, "spine")

        audio_resources = list(audio_asset_ids.values())
        if audio_resources:
            audio_track = ET.SubElement(
                sequence,
                "track",
                id="A1",
                name="Linked Audio",
                type="audio",
            )

        for item in items:
            duration_frames = int(item.get("duration_frames") or int(fps * 4))
            clip = ET.SubElement(
                spine,
                "asset-clip",
                name=self._asset_name(item),
                ref=asset_ids[str(item.get("id"))],
                offset=self._frames_to_duration(int(item.get("timeline_in") or 0), fps, allow_zero=True),
                start="0s",
                duration=self._frames_to_duration(duration_frames, fps),
                tcFormat="NDF",
            )
            note = item.get("recommended_reason")
            if note:
                ET.SubElement(clip, "note").text = str(note)

            audio_asset_id = str(item.get("audio_media_asset_id") or "")
            if audio_asset_id and audio_asset_id in audio_asset_ids:
                audio_resource_id = audio_asset_ids[audio_asset_id]
                audio_tc_info = audio_timecodes.get(audio_resource_id, {})

                audio_offset = 0
                video_tc = item.get("start_tc")
                audio_tc = audio_tc_info.get("start_tc")

                if video_tc and audio_tc and video_tc != audio_tc:
                    try:
                        video_frames = self._timecode_to_frames(video_tc, fps)
                        audio_frames = self._timecode_to_frames(audio_tc, fps)
                        audio_offset = audio_frames - video_frames
                        if abs(audio_offset) > duration_frames:
                            audio_offset = 0
                    except Exception:
                        audio_offset = 0

                audio_clip = ET.SubElement(
                    audio_track,
                    "asset-clip",
                    name=self._asset_name(item) + "_AUDIO",
                    ref=audio_resource_id,
                    offset=self._frames_to_duration(
                        int(item.get("timeline_in") or 0) + audio_offset, fps, allow_zero=True
                    ),
                    start="0s",
                    duration=self._frames_to_duration(duration_frames, fps),
                    tcFormat="NDF",
                )
                ET.SubElement(audio_clip, "note").text = f"linked audio: {audio_tc_info.get('filename') or 'external'}"

        xml_bytes = ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
        file_name = f"{project_name.replace(' ', '_')}_linked_audio_experimental.fcpxml"
        return xml_bytes, file_name

    def _resolve_fps(self, items: list[dict[str, Any]]) -> float:
        for item in items:
            fps = item.get("fps")
            if fps:
                try:
                    return float(fps)
                except Exception:
                    continue
        return 24.0

    def _frames_to_duration(self, frames: int, fps: float, *, allow_zero: bool = False) -> str:
        frames = max(0 if allow_zero else 1, int(frames))
        fps_int = max(1, int(round(fps or 24.0)))
        return f"{frames}/{fps_int}s"

    def _timecode_to_frames(self, timecode: str, fps: float) -> int:
        try:
            parts = timecode.split(":")
            if len(parts) == 4:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                frames = int(parts[3])
                return ((hours * 3600) + (minutes * 60) + seconds) * int(fps) + frames
        except Exception:
            pass
        return 0

    def _frame_duration(self, fps: float) -> str:
        fps_int = max(1, int(round(fps or 24.0)))
        return f"1/{fps_int}s"

    def _asset_name(self, item: dict[str, Any]) -> str:
        scene_number = item.get("scene_number") or "X"
        shot_number = item.get("shot_number") or "X"
        take_number = item.get("take_number") or "X"
        return f"S{scene_number}_SH{shot_number}_TK{take_number}"

    def _asset_src(self, item: dict[str, Any], *, resolution: dict[str, Any] | None = None, role: str = "video") -> str:
        if resolution and resolution.get("fcpxml_uri"):
            return str(resolution["fcpxml_uri"])
        suffix = ".wav" if role == "audio" else ".mov"
        file_name = self._asset_name(item) + suffix
        offline_path = Path("/tmp") / file_name
        return offline_path.resolve().as_uri()


fcpxml_dual_system_variant_service = FCPXMLDualSystemVariantService()