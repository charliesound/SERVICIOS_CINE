from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Optional
from xml.etree import ElementTree as ET


@dataclass
class DavinciPlatformConfig:
    platform: str
    root_path: str
    media_folder: str = "media"
    preserve_original_paths: bool = False

    def get_media_uri(self, filename: str) -> str:
        if self.platform == "windows":
            if re.match(r"^[A-Za-z]:", self.root_path):
                win_path = PureWindowsPath(self.root_path) / self.media_folder / filename
                return f"file:///{win_path.as_posix().replace('/', '|').replace('|', '/', 1)}"
            else:
                return f"file:///{self.root_path}/{self.media_folder}/{filename}"
        elif self.platform == "mac":
            if self.root_path.startswith("/Volumes/"):
                return f"file://{self.root_path}/{self.media_folder}/{filename}"
            else:
                return f"file://{self.root_path}/{self.media_folder}/{filename}"
        elif self.platform == "linux":
            if self.root_path.startswith("/mnt/"):
                return f"file://{self.root_path}/{self.media_folder}/{filename}"
            else:
                return f"file://{self.root_path}/{self.media_folder}/{filename}"
        return f"file:///tmp/{filename}"

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "root_path": self.root_path,
            "media_folder": self.media_folder,
        }


@dataclass
class DavinciPackageManifest:
    generated_at: str
    project_name: str
    platform: str
    root_path: str
    clip_count: int
    fps: float
    audio_mode: str
    files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DavinciPlatformPackageService:
    PLATFORM_CONFIGS = {
        "windows": {
            "default_root": "C:/CID_DaVinci_Export",
            "uri_prefix": "file:///C:/",
            "path_pattern": r"^[A-Za-z]:/",
        },
        "mac": {
            "default_root": "/Users/cliente/CID_DaVinci_Export",
            "uri_prefix": "file:///Users/",
            "path_pattern": r"^/Users/|^/Volumes/",
        },
        "linux": {
            "default_root": "/home/cliente/CID_DaVinci_Export",
            "uri_prefix": "file:///home/",
            "path_pattern": r"^/home/|^/mnt/",
        },
    }

    def __init__(self):
        self.fcpxml_service = None

    def build_multiplatform_package(
        self,
        *,
        project_name: str,
        assembly_cut: dict[str, Any],
        resolved_assets: dict[str, dict[str, Any]] | None = None,
        platforms: list[str] | None = None,
        root_paths: dict[str, str] | None = None,
        audio_mode: str = "conservative",
    ) -> dict[str, Any]:
        platforms = platforms or ["windows", "mac", "linux", "offline"]
        root_paths = root_paths or {}
        resolved_assets = resolved_assets or {}
        assembly = assembly_cut.get("assembly_cut", {})
        items = assembly.get("items", [])
        fps = self._resolve_fps(items)

        packages: dict[str, Any] = {}

        for platform in platforms:
            root_path = root_paths.get(platform, self.PLATFORM_CONFIGS.get(platform, {}).get("default_root", "/tmp"))

            if platform == "offline":
                packages[platform] = self._build_offline_package(
                    project_name=project_name,
                    assembly=assembly,
                    items=items,
                    fps=fps,
                    resolved_assets=resolved_assets,
                    audio_mode=audio_mode,
                )
            else:
                config = DavinciPlatformConfig(platform=platform, root_path=root_path)
                packages[platform] = self._build_platform_fcpxml(
                    project_name=project_name,
                    assembly=assembly,
                    items=items,
                    fps=fps,
                    config=config,
                    resolved_assets=resolved_assets,
                    audio_mode=audio_mode,
                )

        manifest = DavinciPackageManifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            project_name=project_name,
            platform=", ".join(platforms),
            root_path=", ".join(root_paths.values()),
            clip_count=len(items),
            fps=fps,
            audio_mode=audio_mode,
            files=[f"{p}.fcpxml" for p in platforms],
        )

        return {
            "packages": packages,
            "manifest": manifest.__dict__,
            "platforms": platforms,
        }

    def _build_platform_fcpxml(
        self,
        *,
        project_name: str,
        assembly: dict[str, Any],
        items: list[dict[str, Any]],
        fps: float,
        config: DavinciPlatformConfig,
        resolved_assets: dict[str, dict[str, Any]],
        audio_mode: str,
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
        next_resource_index = 2

        total_duration = sum(int(item.get("duration_frames") or 0) for item in items) or int(fps * 4)

        for item in items:
            asset_id = f"r{next_resource_index}"
            next_resource_index += 1
            asset_ids[str(item.get("id"))] = asset_id
            filename = self._asset_filename(item)
            src = config.get_media_uri(filename)
            duration = int(item.get("duration_frames") or int(fps * 4))

            ET.SubElement(
                resources,
                "asset",
                id=asset_id,
                name=self._asset_name(item),
                src=src,
                start="0s",
                duration=self._frames_to_duration(duration, fps),
                hasVideo="1",
                hasAudio="1" if audio_mode == "conservative" else "0",
                format="r1",
            )

            if audio_mode == "conservative":
                audio_asset_id_str = str(item.get("audio_media_asset_id") or "")
                if audio_asset_id_str and audio_asset_id_str != str(item.get("source_media_asset_id") or ""):
                    audio_filename = filename.replace(".mov", ".wav")
                    audio_resource_id = f"r{next_resource_index}"
                    next_resource_index += 1
                    audio_asset_ids[audio_asset_id_str] = audio_resource_id

                    audio_src = config.get_media_uri(audio_filename)

                    ET.SubElement(
                        resources,
                        "asset",
                        id=audio_resource_id,
                        name=self._asset_name(item) + "_AUDIO",
                        src=audio_src,
                        start="0s",
                        duration=self._frames_to_duration(duration, fps),
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
            if audio_mode == "conservative":
                audio_note = "external audio: (see media_relink_report.json); dual_system_audio_export_partial"
                ET.SubElement(clip, "note").text = str(note) + "; " + audio_note if note else audio_note

        xml_bytes = ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
        filename = f"assembly_{config.platform}.fcpxml"
        return xml_bytes, filename

    def _build_offline_package(
        self,
        *,
        project_name: str,
        assembly: dict[str, Any],
        items: list[dict[str, Any]],
        fps: float,
        resolved_assets: dict[str, dict[str, Any]],
        audio_mode: str,
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
        next_resource_index = 2
        total_duration = sum(int(item.get("duration_frames") or 0) for item in items) or int(fps * 4)

        for item in items:
            asset_id = f"r{next_resource_index}"
            next_resource_index += 1
            asset_ids[str(item.get("id"))] = asset_id
            filename = self._asset_filename(item)
            duration = int(item.get("duration_frames") or int(fps * 4))

            ET.SubElement(
                resources,
                "asset",
                id=asset_id,
                name=self._asset_name(item),
                src=f"file:///tmp/{filename}",
                start="0s",
                duration=self._frames_to_duration(duration, fps),
                hasVideo="1",
                hasAudio="1" if audio_mode == "conservative" else "0",
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
                ET.SubElement(clip, "note").text = str(note) + " (relink media manually)"

        xml_bytes = ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)
        filename = "assembly_offline_relink.fcpxml"
        return xml_bytes, filename

    def _asset_name(self, item: dict[str, Any]) -> str:
        scene_number = item.get("scene_number") or "X"
        shot_number = item.get("shot_number") or "X"
        take_number = item.get("take_number") or "X"
        return f"S{scene_number}_SH{shot_number}_TK{take_number}"

    def _asset_filename(self, item: dict[str, Any]) -> str:
        return self._asset_name(item) + ".mov"

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

    def _frame_duration(self, fps: float) -> str:
        fps_int = max(1, int(round(fps or 24.0)))
        return f"1/{fps_int}s"

    def generate_multiplatform_relink_report(
        self,
        *,
        project_name: str,
        assembly_cut: dict[str, Any],
        resolved_assets: dict[str, dict[str, Any]] | None = None,
        platforms: list[str] | None = None,
        root_paths: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        platforms = platforms or ["windows", "mac", "linux", "offline"]
        root_paths = root_paths or {}
        resolved_assets = resolved_assets or {}
        assembly = assembly_cut.get("assembly_cut", {})
        items = assembly.get("items", [])

        relink_reports: dict[str, dict[str, Any]] = {}

        for platform in platforms:
            root_path = root_paths.get(platform, self.PLATFORM_CONFIGS.get(platform, {}).get("default_root", "/tmp"))
            config = DavinciPlatformConfig(platform=platform, root_path=root_path)

            resources = {}
            for item in items:
                asset_key = str(item.get("source_media_asset_id") or item.get("id"))
                filename = self._asset_filename(item)
                resolved = resolved_assets.get(asset_key, {})

                resources[asset_key] = {
                    "status": "resolved",
                    "filename": filename,
                    "asset_type": "video",
                    "resolved_path": f"{root_path}/media/{filename}",
                    "fcpxml_uri": config.get_media_uri(filename),
                    "scene_number": item.get("scene_number"),
                    "shot_number": item.get("shot_number"),
                    "take_number": item.get("take_number"),
                }

                audio_asset_id = str(item.get("audio_media_asset_id") or "")
                if audio_asset_id and audio_asset_id != str(item.get("source_media_asset_id")):
                    audio_filename = filename.replace(".mov", ".wav")
                    audio_resolved = resolved_assets.get(audio_asset_id, {})
                    resources[audio_asset_id] = {
                        "status": "resolved",
                        "filename": audio_filename,
                        "asset_type": "audio",
                        "resolved_path": f"{root_path}/media/{audio_filename}",
                        "fcpxml_uri": config.get_media_uri(audio_filename),
                        "scene_number": item.get("scene_number"),
                        "shot_number": item.get("shot_number"),
                        "take_number": item.get("take_number"),
                    }

            relink_reports[platform] = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "project_id": assembly.get("project_id", "unknown"),
                "assembly_cut_id": assembly.get("id", "unknown"),
                "platform": platform,
                "root_path": root_path,
                "resources": resources,
                "dual_system_summary": {
                    "total_items": len(items),
                    "matched": len([i for i in items if i.get("audio_media_asset_id")]),
                    "dual_system_audio_export": "partial",
                    "notes": "Audio exported as resource with note. Use relink report for manual relink.",
                },
            }

        return relink_reports


davinci_platform_package_service = DavinciPlatformPackageService()