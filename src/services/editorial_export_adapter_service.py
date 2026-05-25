from __future__ import annotations

import base64
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import ClassVar

from schemas.editorial_assembly_schema import AssemblyClip, AssemblyTimeline, NLEExportRequest, NLEExportResult
from services.davinci_platform_package_service import DavinciPlatformConfig
from services.editorial_assembly_core_service import editorial_assembly_core_service
from services.fcpxml_export_service import fcpxml_export_service
from services.fcpxml_validation_service import fcpxml_validation_service


class EditorialExportAdapterError(ValueError):
    """Raised when an editorial export request is not supported."""


class EditorialExportAdapter(ABC):
    nle_type: ClassVar[str]
    supported_formats: ClassVar[list[str]]

    def validate_request(self, request: NLEExportRequest) -> list[str]:
        warnings: list[str] = []
        if request.nle_type != self.nle_type:
            raise EditorialExportAdapterError(
                f"Adapter '{self.nle_type}' cannot export request for '{request.nle_type}'"
            )
        if request.audio_mode == "linked_multitrack":
            warnings.append("linked_multitrack_audio_not_finalized")
        return warnings

    @abstractmethod
    def export(self, request: NLEExportRequest, timeline: AssemblyTimeline) -> NLEExportResult:
        raise NotImplementedError

    def _encode(self, payload: bytes) -> str:
        return base64.b64encode(payload).decode("ascii")

    def _manifest(self, request: NLEExportRequest, timeline: AssemblyTimeline, *, status: str) -> dict:
        return {
            "status": status,
            "nle_type": self.nle_type,
            "supported_formats": self.supported_formats,
            "timeline_id": timeline.id,
            "project_id": timeline.project_id,
            "sequence_count": len(timeline.sequences),
            "clip_count": sum(len(sequence.clips) for sequence in timeline.sequences),
            "target_platform": request.target_platform,
            "destination_root_path": request.destination_root_path,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


class ResolveExportAdapter(EditorialExportAdapter):
    nle_type = "resolve"
    supported_formats = ["fcpxml"]

    def export(self, request: NLEExportRequest, timeline: AssemblyTimeline) -> NLEExportResult:
        warnings = self.validate_request(request)
        assembly_cut = self._to_assembly_cut(timeline)
        resolved_assets = self._resolved_assets(request)
        fcpxml, file_name, fcpxml_manifest = fcpxml_export_service.build_fcpxml(
            project_name=timeline.name,
            assembly_cut=assembly_cut,
            resolved_assets=resolved_assets,
        )
        validation = fcpxml_validation_service.validate(fcpxml)
        if not validation["valid"]:
            raise EditorialExportAdapterError(
                "Resolve FCPXML validation failed: " + ",".join(validation["errors"])
            )
        warnings.extend(fcpxml_manifest.get("warnings", []))
        warnings.extend(validation.get("warnings", []))
        relink_report = None
        missing_media = []
        if request.include_relink_report:
            relink_report, missing_media = editorial_assembly_core_service.generate_relink_report(
                timeline=timeline,
                media_assets=request.media_assets,
                destination_root_path=request.destination_root_path,
            )
        artifact_path = self._artifact_path(request, file_name)
        manifest = self._manifest(request, timeline, status="resolve_fcpxml_ready")
        manifest.update(fcpxml_manifest)
        manifest["validation"] = validation
        manifest["relink_report"] = relink_report.model_dump() if relink_report else None
        manifest["missing_media"] = [item.model_dump() for item in missing_media]
        manifest["compatible_services"] = [
            "fcpxml_export_service",
            "fcpxml_validation_service",
            "davinci_platform_package_service",
        ]
        if artifact_path:
            manifest["artifact_path_kind"] = "suggested_destination"
        return NLEExportResult(
            nle_type=self.nle_type,
            export_format="fcpxml",
            file_name=file_name,
            file_bytes_b64=self._encode(fcpxml),
            artifact_path=artifact_path,
            artifact_url=self._path_to_uri(artifact_path) if artifact_path else None,
            warnings=warnings,
            manifest=manifest,
        )

    def _to_assembly_cut(self, timeline: AssemblyTimeline) -> dict:
        items = []
        for sequence in timeline.sequences:
            for clip in sequence.clips:
                scene_number, shot_number, take_number = self._clip_numbers(clip)
                items.append(
                    {
                        "id": clip.id,
                        "take_id": clip.take_id,
                        "scene_number": scene_number or sequence.scene_number,
                        "shot_number": shot_number,
                        "take_number": take_number,
                        "source_media_asset_id": clip.source_media_asset_id,
                        "audio_media_asset_id": clip.audio_media_asset_id,
                        "timeline_in": clip.timeline_in,
                        "timeline_out": clip.timeline_out,
                        "duration_frames": clip.duration_frames,
                        "fps": clip.fps or timeline.fps,
                        "start_tc": clip.start_tc,
                        "timecode_offset_frames": clip.timecode_offset_frames,
                        "assigned_tracks": clip.assigned_tracks,
                        "recommended_reason": "neutral_editorial_assembly",
                    }
                )
        return {
            "assembly_cut": {
                "id": timeline.id,
                "project_id": timeline.project_id,
                "name": timeline.name,
                "items": items,
            }
        }

    def _resolved_assets(self, request: NLEExportRequest) -> dict[str, dict]:
        resolved: dict[str, dict] = {}
        for asset in request.media_assets:
            resolved[asset.id] = {
                "status": "resolved" if asset.file_path else "missing",
                "filename": asset.file_name,
                "asset_type": asset.asset_type,
                "resolved_path": self._resolved_path(asset.file_name, asset.file_path, request),
                "fcpxml_uri": self._asset_uri(asset.file_name, asset.file_path, request),
            }
        return resolved

    def _resolved_path(self, file_name: str, file_path: str, request: NLEExportRequest) -> str:
        if request.destination_root_path:
            return self._join_destination_path(request, file_name)
        return file_path

    def _asset_uri(self, file_name: str, file_path: str, request: NLEExportRequest) -> str:
        if request.destination_root_path and request.target_platform != "offline":
            config = DavinciPlatformConfig(
                platform=request.target_platform,
                root_path=request.destination_root_path,
            )
            return config.get_media_uri(file_name)
        return self._path_to_uri(file_path) or f"file:///tmp/{file_name}"

    def _artifact_path(self, request: NLEExportRequest, file_name: str) -> str | None:
        if not request.destination_root_path:
            return None
        return self._join_destination_path(request, file_name)

    def _join_destination_path(self, request: NLEExportRequest, file_name: str) -> str:
        if request.target_platform == "windows":
            return str(PureWindowsPath(request.destination_root_path or "") / file_name)
        return str(Path(request.destination_root_path or "") / file_name)

    def _path_to_uri(self, path: str | None) -> str | None:
        if not path:
            return None
        if path.startswith("file://"):
            return path
        normalized = path.replace("\\", "/")
        if re.match(r"^[A-Za-z]:/", normalized):
            return "file:///" + PureWindowsPath(normalized).as_posix()
        if normalized.startswith("/"):
            return Path(normalized).as_uri()
        return None

    def _clip_numbers(self, clip: AssemblyClip) -> tuple[int, int, int]:
        match = re.search(r"S(\d+)_SH(\d+)_TK(\d+)", clip.clip_name, re.IGNORECASE)
        if not match:
            return 0, 0, 0
        return int(match.group(1)), int(match.group(2)), int(match.group(3))


class PremiereExportAdapter(EditorialExportAdapter):
    nle_type = "premiere"
    supported_formats = ["fcpxml", "xml"]

    def export(self, request: NLEExportRequest, timeline: AssemblyTimeline) -> NLEExportResult:
        warnings = self.validate_request(request)
        warnings.append("premiere_export_stub_controlled")
        payload = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<premiere-export status=\"stub\" "
            f"timeline=\"{timeline.id}\" />\n"
        ).encode("utf-8")
        return NLEExportResult(
            nle_type=self.nle_type,
            export_format="fcpxml",
            file_name=f"{timeline.name.replace(' ', '_')}_premiere_stub.xml",
            file_bytes_b64=self._encode(payload),
            warnings=warnings,
            manifest=self._manifest(request, timeline, status="stub_controlled"),
        )


class AvidExportAdapter(EditorialExportAdapter):
    nle_type = "avid"
    supported_formats = ["ale", "edl"]

    def export(self, request: NLEExportRequest, timeline: AssemblyTimeline) -> NLEExportResult:
        warnings = self.validate_request(request)
        warnings.extend(["avid_export_stub_controlled", "aaf_not_implemented_in_editorial_2a"])
        payload = self._build_ale_stub(timeline)
        return NLEExportResult(
            nle_type=self.nle_type,
            export_format="ale",
            file_name=f"{timeline.name.replace(' ', '_')}_avid_stub.ale",
            file_bytes_b64=self._encode(payload),
            warnings=warnings,
            manifest=self._manifest(request, timeline, status="stub_controlled"),
        )

    def _build_ale_stub(self, timeline: AssemblyTimeline) -> bytes:
        lines = [
            "Heading",
            "FIELD_DELIM\tTABS",
            "VIDEO_FORMAT\t1080p",
            "",
            "Column",
            "Name\tScene\tTake\tNotes",
            "",
            "Data",
        ]
        for sequence in timeline.sequences:
            for clip in sequence.clips:
                lines.append(f"{clip.clip_name}\t{sequence.scene_number}\t{clip.take_id}\tCID Editorial 2A stub")
        return ("\n".join(lines) + "\n").encode("utf-8")


class EditorialExportAdapterService:
    def __init__(self) -> None:
        self._adapters: dict[str, EditorialExportAdapter] = {
            "resolve": ResolveExportAdapter(),
            "premiere": PremiereExportAdapter(),
            "avid": AvidExportAdapter(),
        }

    def get_adapter(self, nle_type: str) -> EditorialExportAdapter:
        adapter = self._adapters.get(nle_type)
        if adapter is None:
            raise EditorialExportAdapterError(f"Unsupported NLE adapter '{nle_type}'")
        return adapter

    def export(self, request: NLEExportRequest, timeline: AssemblyTimeline) -> NLEExportResult:
        return self.get_adapter(request.nle_type).export(request, timeline)

    def supported_adapters(self) -> dict[str, list[str]]:
        return {
            nle_type: adapter.supported_formats
            for nle_type, adapter in self._adapters.items()
        }


editorial_export_adapter_service = EditorialExportAdapterService()
