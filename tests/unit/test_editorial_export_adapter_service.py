from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("AUTH_SECRET_KEY", "a" * 32)
os.environ.setdefault("APP_SECRET_KEY", "a" * 32)
os.environ.setdefault("AUTH_DISABLED", "true")


def _timeline():
    from schemas.editorial_assembly_schema import AssemblyClip, AssemblySequence, AssemblyTimeline

    clip = AssemblyClip(
        id="clip-1",
        take_id="take-1-1-1",
        clip_name="S1_SH1_TK1",
        source_media_asset_id="video-1",
        audio_media_asset_id="audio-1",
        duration_frames=48,
        timeline_out=48,
    )
    return AssemblyTimeline(
        id="assembly-1",
        project_id="project-1",
        name="Assembly",
        total_duration_frames=48,
        sequences=[AssemblySequence(id="seq-1", name="Scene 1", scene_number=1, clips=[clip])],
    )


def test_adapters_exist_and_resolve_is_primary():
    from services.editorial_export_adapter_service import editorial_export_adapter_service

    supported = editorial_export_adapter_service.supported_adapters()

    assert list(supported.keys())[0] == "resolve"
    assert supported["resolve"] == ["fcpxml"]
    assert supported["premiere"] == ["fcpxml", "xml"]
    assert supported["avid"] == ["ale", "edl"]


def test_resolve_adapter_exports_fcpxml():
    from schemas.editorial_assembly_schema import EditorialMediaAsset, NLEExportRequest
    from services.editorial_export_adapter_service import editorial_export_adapter_service
    from services.fcpxml_validation_service import fcpxml_validation_service

    result = editorial_export_adapter_service.export(
        NLEExportRequest(
            nle_type="resolve",
            target_platform="linux",
            destination_root_path="/mnt/editorial/export",
            media_assets=[
                EditorialMediaAsset(
                    id="video-1",
                    file_name="A001_C001.mov",
                    file_path="/media/A001_C001.mov",
                    asset_type="video",
                ),
                EditorialMediaAsset(
                    id="audio-1",
                    file_name="S001_T001.wav",
                    file_path="/media/S001_T001.wav",
                    asset_type="audio",
                ),
            ],
        ),
        _timeline(),
    )

    payload = base64.b64decode(result.file_bytes_b64)
    assert result.export_format == "fcpxml"
    assert b"<fcpxml" in payload
    assert fcpxml_validation_service.validate(payload)["valid"] is True
    assert result.manifest["status"] == "resolve_fcpxml_ready"
    assert result.manifest["validation"]["valid"] is True
    assert result.manifest["relink_report"]["resolved_media_count"] == 2
    assert result.artifact_path == "/mnt/editorial/export/Assembly_assembly.fcpxml"


def test_premiere_and_avid_are_controlled_stubs():
    from schemas.editorial_assembly_schema import NLEExportRequest
    from services.editorial_export_adapter_service import editorial_export_adapter_service

    premiere = editorial_export_adapter_service.export(NLEExportRequest(nle_type="premiere"), _timeline())
    avid = editorial_export_adapter_service.export(NLEExportRequest(nle_type="avid"), _timeline())

    assert "premiere_export_stub_controlled" in premiere.warnings
    assert premiere.manifest["status"] == "stub_controlled"
    assert avid.export_format == "ale"
    assert "aaf_not_implemented_in_editorial_2a" in avid.warnings
