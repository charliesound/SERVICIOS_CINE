from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import ClassVar
from xml.etree import ElementTree as ET

from schemas.editorial_assembly_schema import AssemblyTimeline, NLEExportRequest, NLEExportResult


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
        fcpxml = self._build_fcpxml(timeline)
        warnings.append("resolve_adapter_contract_uses_neutral_fcpxml_compatibility_layer")
        manifest = self._manifest(request, timeline, status="contract_ready")
        manifest["compatible_services"] = [
            "fcpxml_export_service",
            "davinci_platform_package_service",
        ]
        return NLEExportResult(
            nle_type=self.nle_type,
            export_format="fcpxml",
            file_name=f"{timeline.name.replace(' ', '_')}_resolve.fcpxml",
            file_bytes_b64=self._encode(fcpxml),
            warnings=warnings,
            manifest=manifest,
        )

    def _build_fcpxml(self, timeline: AssemblyTimeline) -> bytes:
        fcpxml = ET.Element("fcpxml", version="1.10")
        resources = ET.SubElement(fcpxml, "resources")
        ET.SubElement(
            resources,
            "format",
            id="r1",
            name=f"FFVideoFormat{int(round(timeline.fps))}p",
            frameDuration=f"1/{int(round(timeline.fps or 24.0))}s",
        )
        library = ET.SubElement(fcpxml, "library")
        event = ET.SubElement(library, "event", name=timeline.name)
        project = ET.SubElement(event, "project", name=timeline.name)
        sequence = ET.SubElement(
            project,
            "sequence",
            format="r1",
            duration=f"{max(timeline.total_duration_frames, 1)}/{int(round(timeline.fps or 24.0))}s",
            tcStart="0s",
            tcFormat="NDF",
        )
        spine = ET.SubElement(sequence, "spine")
        for sequence_item in timeline.sequences:
            for clip in sequence_item.clips:
                ET.SubElement(
                    spine,
                    "asset-clip",
                    name=clip.clip_name,
                    ref="r1",
                    offset=f"{clip.timeline_in}/{int(round(clip.fps or timeline.fps or 24.0))}s",
                    duration=f"{max(clip.duration_frames, 1)}/{int(round(clip.fps or timeline.fps or 24.0))}s",
                    tcFormat="NDF",
                )
        return ET.tostring(fcpxml, encoding="utf-8", xml_declaration=True)


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
