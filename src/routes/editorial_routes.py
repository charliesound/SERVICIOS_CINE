from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.core import Project
from models.delivery import Deliverable
from models.postproduction import Take
from models.storage import MediaAsset, StorageSource
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.editorial_schema import (
    AssemblyCutCreateResponse,
    AssemblyCutItemResponse,
    DavinciPlatformExportRequest,
    DavinciPlatformExportResponse,
    EditorialAudioMetadataListResponse,
    EditorialAudioMetadataResponse,
    EditorialAudioMetadataScanResponse,
    AssemblyCutResponse,
    EditorialFCPXMLStatusResponse,
    EditorialFCPXMLValidationResponse,
    EditorialMediaRelinkReportResponse,
    EditorialRecommendedTakeListResponse,
    EditorialRecommendedTakeResponse,
    EditorialReconcileResponse,
    EditorialScoreResponse,
    EditorialTakeListResponse,
    EditorialTakeResponse,
)
from services.assembly_service import assembly_service
from services.audio_metadata_service import audio_metadata_service
from services.davinci_platform_package_service import davinci_platform_package_service
from services.delivery_service import delivery_service
from services.editorial_reconciliation_service import editorial_reconciliation_service
from services.fcpxml_export_service import fcpxml_export_service
from services.fcpxml_validation_service import fcpxml_validation_service
from services.media_path_resolver_service import media_path_resolver_service
from services.take_scoring_service import take_scoring_service


router = APIRouter(prefix="/api/projects", tags=["editorial"])


async def _get_project_for_tenant(db: AsyncSession, project_id: str, tenant: TenantContext) -> Project:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


def _take_response(take: Take) -> EditorialTakeResponse:
    conflict_flags = []
    audio_metadata = None
    if take.conflict_flags_json:
        try:
            loaded = json.loads(take.conflict_flags_json)
            if isinstance(loaded, list):
                conflict_flags = [str(item) for item in loaded]
        except Exception:
            conflict_flags = []
    if take.audio_metadata_json:
        try:
            loaded_audio = json.loads(take.audio_metadata_json)
            if isinstance(loaded_audio, dict):
                audio_metadata = loaded_audio
        except Exception:
            audio_metadata = None
    return EditorialTakeResponse(
        id=str(take.id),
        project_id=str(take.project_id),
        organization_id=str(take.organization_id),
        scene_number=take.scene_number,
        shot_number=take.shot_number,
        take_number=take.take_number,
        camera_roll=take.camera_roll,
        sound_roll=take.sound_roll,
        camera_media_asset_id=take.camera_media_asset_id,
        sound_media_asset_id=take.sound_media_asset_id,
        camera_report_id=take.camera_report_id,
        sound_report_id=take.sound_report_id,
        script_note_id=take.script_note_id,
        director_note_id=take.director_note_id,
        video_filename=take.video_filename,
        audio_filename=take.audio_filename,
        start_timecode=take.start_timecode,
        end_timecode=take.end_timecode,
        audio_timecode_start=take.audio_timecode_start,
        audio_time_reference_samples=take.audio_time_reference_samples,
        audio_sample_rate=take.audio_sample_rate,
        audio_channels=take.audio_channels,
        audio_duration_seconds=take.audio_duration_seconds,
        audio_fps=take.audio_fps,
        audio_scene=take.audio_scene,
        audio_take=take.audio_take,
        audio_circled=take.audio_circled,
        audio_metadata_status=take.audio_metadata_status,
        audio_metadata=audio_metadata,
        dual_system_status=take.dual_system_status,
        sync_confidence=take.sync_confidence,
        sync_method=take.sync_method,
        sync_warning=take.sync_warning,
        duration_frames=take.duration_frames,
        fps=take.fps,
        slate=take.slate,
        script_status=take.script_status,
        director_status=take.director_status,
        camera_status=take.camera_status,
        sound_status=take.sound_status,
        reconciliation_status=take.reconciliation_status,
        is_circled=bool(take.is_circled),
        is_best=bool(take.is_best),
        is_recommended=bool(take.is_recommended),
        score=float(take.score or 0.0),
        recommended_reason=take.recommended_reason,
        conflict_flags=conflict_flags,
        notes=take.notes,
        created_at=take.created_at,
        updated_at=take.updated_at,
    )


def _assembly_response(payload: dict) -> AssemblyCutResponse:
    assembly = payload.get("assembly_cut")
    if assembly is None:
        raise HTTPException(status_code=404, detail="Assembly cut not found")
    return AssemblyCutResponse(
        id=assembly["id"],
        project_id=assembly["project_id"],
        organization_id=assembly.get("organization_id"),
        name=assembly["name"],
        description=assembly.get("description"),
        status=assembly.get("status"),
        source_scope=assembly.get("source_scope"),
        source_version=assembly.get("source_version"),
        metadata_json=assembly.get("metadata_json") or {},
        created_by=assembly.get("created_by"),
        created_at=assembly.get("created_at"),
        updated_at=assembly.get("updated_at"),
        items=[AssemblyCutItemResponse(**item) for item in assembly.get("items", [])],
    )


async def _load_media_assets(
    db: AsyncSession,
    *,
    assembly: dict,
) -> tuple[dict[str, MediaAsset], dict[str, StorageSource]]:
    asset_ids = {
        str(asset_id)
        for item in assembly.get("items", [])
        for asset_id in [item.get("source_media_asset_id"), item.get("audio_media_asset_id")]
        if asset_id
    }
    if not asset_ids:
        return {}, {}

    asset_result = await db.execute(select(MediaAsset).where(MediaAsset.id.in_(asset_ids)))
    assets = list(asset_result.scalars().all())
    assets_by_id = {str(asset.id): asset for asset in assets}

    source_ids = {str(asset.storage_source_id) for asset in assets if getattr(asset, "storage_source_id", None)}
    storage_sources_by_id: dict[str, StorageSource] = {}
    if source_ids:
        source_result = await db.execute(select(StorageSource).where(StorageSource.id.in_(source_ids)))
        storage_sources_by_id = {str(source.id): source for source in source_result.scalars().all()}
    return assets_by_id, storage_sources_by_id


def _resolved_assets_map(
    assets_by_id: dict[str, MediaAsset],
    storage_sources_by_id: dict[str, StorageSource],
) -> dict[str, dict]:
    resolved: dict[str, dict] = {}
    for asset_id, asset in assets_by_id.items():
        storage_source = storage_sources_by_id.get(str(asset.storage_source_id)) if getattr(asset, "storage_source_id", None) else None
        resolved[asset_id] = media_path_resolver_service.resolve_asset(asset, storage_source=storage_source)
    return resolved


def _route_status_counts(resolved_assets: dict[str, dict]) -> dict[str, int]:
    return {
        "resolved": sum(1 for item in resolved_assets.values() if item.get("status") == "resolved"),
        "offline": sum(1 for item in resolved_assets.values() if item.get("status") == "offline"),
        "missing": sum(1 for item in resolved_assets.values() if item.get("status") == "missing"),
    }


def _build_media_relink_report(
    *,
    project_id: str,
    assembly: dict,
    assets_by_id: dict[str, MediaAsset],
    storage_sources_by_id: dict[str, StorageSource],
    resolved_assets: dict[str, dict],
    takes_by_id: dict[str, Take],
) -> dict:
    entries: list[dict] = []
    warnings: list[str] = []
    for item in assembly.get("items", []):
        clip_name = fcpxml_export_service._asset_name(item)
        take = takes_by_id.get(str(item.get("take_id"))) if item.get("take_id") else None
        take_flags = []
        if take and take.conflict_flags_json:
            try:
                loaded_flags = json.loads(take.conflict_flags_json)
                if isinstance(loaded_flags, list):
                    take_flags = [str(flag) for flag in loaded_flags]
            except Exception:
                take_flags = []
        clip_video = resolved_assets.get(str(item.get("source_media_asset_id") or ""), {})
        clip_audio = resolved_assets.get(str(item.get("audio_media_asset_id") or ""), {})
        for role, asset_key in (("video", "source_media_asset_id"), ("audio", "audio_media_asset_id")):
            asset_id = item.get(asset_key)
            if not asset_id:
                warnings.append(f"missing_{role}_asset:{clip_name}")
                continue
            asset = assets_by_id.get(str(asset_id))
            resolution = resolved_assets.get(str(asset_id))
            if asset is None or resolution is None:
                warnings.append(f"missing_asset_record:{role}:{asset_id}")
                continue
            entry = {
                "clip_id": str(item.get("id")),
                "clip_name": clip_name,
                "role": role,
                "asset_id": str(asset_id),
                "filename": str(resolution.get("filename") or getattr(asset, "file_name", "media_asset")),
                "resolved_path": str(resolution.get("resolved_path") or ""),
                "fcpxml_uri": str(resolution.get("fcpxml_uri") or ""),
                "status": str(resolution.get("status") or "missing"),
                "reason": str(resolution.get("reason") or "unknown"),
                "duration_frames": item.get("duration_frames"),
                "start_timecode": item.get("start_tc"),
                "scene": item.get("scene_number"),
                "shot": item.get("shot_number"),
                "take": item.get("take_number"),
                "video_asset_id": item.get("source_media_asset_id"),
                "audio_asset_id": item.get("audio_media_asset_id"),
                "video_path": str(clip_video.get("resolved_path") or ""),
                "audio_path": str(clip_audio.get("resolved_path") or ""),
                "video_status": str(clip_video.get("status") or "missing"),
                "audio_status": str(clip_audio.get("status") or "missing"),
                "sync_method": getattr(take, "sync_method", None),
                "sync_confidence": getattr(take, "sync_confidence", None),
                "dual_system_status": getattr(take, "dual_system_status", None),
                "take_warnings": take_flags,
            }
            if role == "audio":
                storage_source = storage_sources_by_id.get(str(asset.storage_source_id)) if getattr(asset, "storage_source_id", None) else None
                entry["audio_metadata"] = audio_metadata_service.get_audio_metadata(asset, storage_source=storage_source).to_dict()
            entries.append(entry)

    status_counts = _route_status_counts(resolved_assets)
    return {
        "generated_at": datetime.now(timezone.utc),
        "project_id": project_id,
        "assembly_cut_id": str(assembly.get("id")),
        "clip_count": len(assembly.get("items", [])),
        "resolved_media_count": status_counts["resolved"],
        "offline_media_count": status_counts["offline"],
        "missing_media_count": status_counts["missing"],
        "warnings": warnings,
        "entries": entries,
    }


async def _build_editorial_export_bundle(
    db: AsyncSession,
    *,
    project: Project,
    payload: dict,
) -> dict:
    assembly = payload.get("assembly_cut")
    if assembly is None:
        raise HTTPException(status_code=404, detail="No assembly cut available for export")
    assets_by_id, storage_sources_by_id = await _load_media_assets(db, assembly=assembly)
    take_ids = [str(item.get("take_id")) for item in assembly.get("items", []) if item.get("take_id")]
    takes_by_id: dict[str, Take] = {}
    if take_ids:
        takes_result = await db.execute(select(Take).where(Take.id.in_(take_ids)))
        takes_by_id = {str(take.id): take for take in takes_result.scalars().all()}
    resolved_assets = _resolved_assets_map(assets_by_id, storage_sources_by_id)
    fcpxml_bytes, file_name, manifest = fcpxml_export_service.build_fcpxml(
        project_name=str(project.name),
        assembly_cut=payload,
        resolved_assets=resolved_assets,
    )
    validation = fcpxml_validation_service.validate(fcpxml_bytes)
    media_relink_report = _build_media_relink_report(
        project_id=str(project.id),
        assembly=assembly,
        assets_by_id=assets_by_id,
        storage_sources_by_id=storage_sources_by_id,
        resolved_assets=resolved_assets,
        takes_by_id=takes_by_id,
    )
    warnings = list(manifest.get("warnings") or []) + list(media_relink_report.get("warnings") or []) + list(validation.get("warnings") or [])
    return {
        "assembly": assembly,
        "file_bytes": fcpxml_bytes,
        "file_name": file_name,
        "manifest": manifest,
        "validation": validation,
        "media_relink_report": media_relink_report,
        "route_status": _route_status_counts(resolved_assets),
        "warnings": warnings,
    }


def _build_editorial_notes(project: Project, export_bundle: dict) -> str:
    validation = export_bundle["validation"]
    relink = export_bundle["media_relink_report"]
    lines = [
        "CID editorial export package",
        f"project={project.name}",
        f"assembly_cut_id={export_bundle['assembly']['id']}",
        f"generated_at={export_bundle['manifest']['generated_at']}",
        f"fcpxml_valid={validation['valid']}",
        f"clips={export_bundle['manifest']['clip_count']}",
        f"resolved_media={relink['resolved_media_count']}",
        f"offline_media={relink['offline_media_count']}",
        "",
        "warnings:",
    ]
    warnings = export_bundle.get("warnings") or ["none"]
    lines.extend(f"- {warning}" for warning in warnings)
    dual_system_entries = [
        entry for entry in relink.get("entries", []) if entry.get("dual_system_status") and entry.get("role") == "audio"
    ]
    if dual_system_entries:
        lines.extend([
            "",
            "dual_system_audio:",
        ])
        for entry in dual_system_entries:
            lines.append(
                f"- {entry.get('clip_name')}: {entry.get('dual_system_status')} via {entry.get('sync_method') or 'unknown'}"
            )
    return "\n".join(lines) + "\n"


def _build_editorial_package_bytes(
    *,
    project: Project,
    export_bundle: dict,
    recommended_takes: list[dict],
) -> bytes:
    archive_buffer = BytesIO()
    assembly = export_bundle["assembly"]
    assembly_summary = {
        "project_id": str(project.id),
        "project_name": str(project.name),
        "assembly_cut_id": assembly["id"],
        "clip_count": export_bundle["manifest"]["clip_count"],
        "fps": export_bundle["manifest"]["fps"],
        "route_status": export_bundle["route_status"],
        "warnings": export_bundle["warnings"],
        "validation": export_bundle["validation"],
    }
    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("assembly.fcpxml", export_bundle["file_bytes"])
        archive.writestr("assembly_summary.json", json.dumps(assembly_summary, ensure_ascii=False, indent=2, default=str))
        archive.writestr(
            "media_relink_report.json",
            json.dumps(export_bundle["media_relink_report"], ensure_ascii=False, indent=2, default=str),
        )
        archive.writestr("recommended_takes.json", json.dumps(recommended_takes, ensure_ascii=False, indent=2, default=str))
        archive.writestr("editorial_notes.txt", _build_editorial_notes(project, export_bundle))
    return archive_buffer.getvalue()


@router.get("/{project_id}/editorial/takes", response_model=EditorialTakeListResponse)
async def list_editorial_takes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialTakeListResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    result = await db.execute(
        select(Take)
        .where(Take.project_id == project_id)
        .order_by(Take.scene_number.asc(), Take.shot_number.asc(), Take.take_number.asc())
    )
    takes = list(result.scalars().all())
    return EditorialTakeListResponse(takes=[_take_response(take) for take in takes])


@router.post("/{project_id}/editorial/reconcile", response_model=EditorialReconcileResponse)
async def reconcile_editorial_material(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialReconcileResponse:
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await editorial_reconciliation_service.reconcile_project(db, project=project)
    return EditorialReconcileResponse(**payload)


@router.post("/{project_id}/editorial/score", response_model=EditorialScoreResponse)
async def score_editorial_takes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialScoreResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    payload = await take_scoring_service.score_project_takes(db, project_id=project_id)
    return EditorialScoreResponse(**payload)


@router.get("/{project_id}/editorial/audio-metadata", response_model=EditorialAudioMetadataListResponse)
async def get_editorial_audio_metadata(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialAudioMetadataListResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    results = await audio_metadata_service.scan_project_audio_metadata(db, project_id=project_id)
    return EditorialAudioMetadataListResponse(
        project_id=project_id,
        audio_assets=[EditorialAudioMetadataResponse(**result.to_dict()) for result in results],
    )


@router.post("/{project_id}/editorial/audio-metadata/scan", response_model=EditorialAudioMetadataScanResponse)
async def scan_editorial_audio_metadata(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialAudioMetadataScanResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    results = await audio_metadata_service.scan_project_audio_metadata(db, project_id=project_id)
    counts = {
        "parsed_count": sum(1 for result in results if result.status == "parsed"),
        "partial_count": sum(1 for result in results if result.status == "partial"),
        "unsupported_count": sum(1 for result in results if result.status == "unsupported"),
        "error_count": sum(1 for result in results if result.status == "error"),
    }
    return EditorialAudioMetadataScanResponse(
        project_id=project_id,
        scanned_count=len(results),
        audio_assets=[EditorialAudioMetadataResponse(**result.to_dict()) for result in results],
        **counts,
    )


@router.get("/{project_id}/editorial/recommended-takes", response_model=EditorialRecommendedTakeListResponse)
async def list_recommended_takes(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialRecommendedTakeListResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    result = await db.execute(
        select(Take)
        .where(Take.project_id == project_id, Take.is_recommended.is_(True))
        .order_by(Take.scene_number.asc(), Take.shot_number.asc(), Take.take_number.asc())
    )
    takes = list(result.scalars().all())
    return EditorialRecommendedTakeListResponse(
        recommended_takes=[
            EditorialRecommendedTakeResponse(
                scene_number=take.scene_number,
                shot_number=take.shot_number,
                take=_take_response(take),
            )
            for take in takes
        ]
    )


@router.post("/{project_id}/editorial/assembly", response_model=AssemblyCutCreateResponse)
async def create_editorial_assembly(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AssemblyCutCreateResponse:
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.generate_assembly(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        created_by=tenant.user_id,
    )
    return AssemblyCutCreateResponse(
        assembly_cut=_assembly_response(payload),
        items_created=payload.get("items_created", 0),
    )


@router.get("/{project_id}/editorial/assembly", response_model=AssemblyCutResponse)
async def get_editorial_assembly(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AssemblyCutResponse:
    await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)
    return _assembly_response(payload)


@router.get("/{project_id}/editorial/export/fcpxml")
async def export_editorial_fcpxml(
    project_id: str,
    download: bool = Query(default=True),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)
    export_bundle = await _build_editorial_export_bundle(db, project=project, payload=payload)
    assembly = export_bundle["assembly"]
    if not download:
        deliverable_result = await db.execute(
            select(Deliverable)
            .where(Deliverable.project_id == project_id, Deliverable.format_type == "FCPXML")
            .order_by(Deliverable.created_at.desc(), Deliverable.id.desc())
            .limit(1)
        )
        deliverable = deliverable_result.scalars().first()
        delivery_payload = deliverable.delivery_payload if deliverable is not None else {}
        return EditorialFCPXMLStatusResponse(
            deliverable_id=str(deliverable.id) if deliverable is not None else None,
            file_name=str(delivery_payload.get("file_name") or export_bundle["file_name"]),
            file_path=str(delivery_payload.get("file_path") or ""),
            assembly_cut_id=str(assembly["id"]),
            clip_count=int(export_bundle["manifest"]["clip_count"]),
            route_status=export_bundle["route_status"],
            warnings=export_bundle["warnings"],
            validation=EditorialFCPXMLValidationResponse(**export_bundle["validation"]),
            media_relink_report=EditorialMediaRelinkReportResponse(**export_bundle["media_relink_report"]),
        )
    deliverable = await delivery_service.create_project_file_deliverable(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        name=f"{project.name} Assembly FCPXML",
        format_type="FCPXML",
        file_bytes=export_bundle["file_bytes"],
        file_name=export_bundle["file_name"],
        mime_type="application/xml",
        category="editorial",
        manifest_payload=export_bundle["manifest"],
        payload_extra={
            "assembly_cut_id": assembly["id"],
            "validation": export_bundle["validation"],
            "route_status": export_bundle["route_status"],
            "warnings": export_bundle["warnings"],
        },
    )
    file_path = deliverable.delivery_payload.get("file_path")
    if not file_path:
        raise HTTPException(status_code=500, detail="FCPXML export path missing")
    return FileResponse(
        path=file_path,
        filename=deliverable.delivery_payload.get("file_name") or export_bundle["file_name"],
        media_type=deliverable.delivery_payload.get("mime_type") or "application/xml",
    )


@router.get("/{project_id}/editorial/export/fcpxml/validate", response_model=EditorialFCPXMLValidationResponse)
async def validate_editorial_fcpxml(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialFCPXMLValidationResponse:
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)
    export_bundle = await _build_editorial_export_bundle(db, project=project, payload=payload)
    return EditorialFCPXMLValidationResponse(**export_bundle["validation"])


@router.get("/{project_id}/editorial/media-relink-report", response_model=EditorialMediaRelinkReportResponse)
async def get_editorial_media_relink_report(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EditorialMediaRelinkReportResponse:
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)
    export_bundle = await _build_editorial_export_bundle(db, project=project, payload=payload)
    return EditorialMediaRelinkReportResponse(**export_bundle["media_relink_report"])


@router.post("/{project_id}/editorial/export/package")
async def export_editorial_package(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)
    export_bundle = await _build_editorial_export_bundle(db, project=project, payload=payload)
    takes_result = await db.execute(
        select(Take)
        .where(Take.project_id == project_id, Take.is_recommended.is_(True))
        .order_by(Take.scene_number.asc(), Take.shot_number.asc(), Take.take_number.asc())
    )
    recommended_takes = [_take_response(take).model_dump(mode="json") for take in takes_result.scalars().all()]
    package_file_name = f"{str(project.name).replace(' ', '_')}_editorial_package.zip"
    package_bytes = _build_editorial_package_bytes(
        project=project,
        export_bundle=export_bundle,
        recommended_takes=recommended_takes,
    )
    deliverable = await delivery_service.create_project_file_deliverable(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        name=f"{project.name} Editorial Package",
        format_type="ZIP",
        file_bytes=package_bytes,
        file_name=package_file_name,
        mime_type="application/zip",
        category="editorial",
        manifest_payload={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "assembly_cut_id": export_bundle["assembly"]["id"],
            "package_entries": [
                "assembly.fcpxml",
                "assembly_summary.json",
                "media_relink_report.json",
                "recommended_takes.json",
                "editorial_notes.txt",
            ],
            "include_media": False,
        },
        payload_extra={"assembly_cut_id": export_bundle["assembly"]["id"]},
    )
    file_path = deliverable.delivery_payload.get("file_path")
    if not file_path:
        raise HTTPException(status_code=500, detail="Editorial package export path missing")
    return FileResponse(
        path=file_path,
        filename=deliverable.delivery_payload.get("file_name") or package_file_name,
        media_type=deliverable.delivery_payload.get("mime_type") or "application/zip",
    )


@router.post("/{project_id}/editorial/export/davinci-package")
async def export_davinci_platform_package(
    project_id: str,
    request: DavinciPlatformExportRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_for_tenant(db, project_id, tenant)
    payload = await assembly_service.get_latest_assembly(db, project_id=project_id)

    assembly = payload.get("assembly_cut")
    if not assembly:
        raise HTTPException(status_code=400, detail="No assembly cut found for project")

    items = assembly.get("items", [])
    if not items:
        raise HTTPException(status_code=400, detail="No items in assembly cut")

    platform = request.platform
    root_path = request.root_path or davinci_platform_package_service.PLATFORM_CONFIGS.get(platform, {}).get("default_root")

    platforms = [platform] if platform != "all" else ["windows", "mac", "linux", "offline"]
    root_paths = {platform: root_path} if platform != "all" else {
        "windows": "C:/CID_DaVinci_Export",
        "mac": "/Users/cliente/CID_DaVinci_Export",
        "linux": "/home/cliente/CID_DaVinci_Export",
        "offline": "/tmp",
    }

    resolved_assets = {}

    result = davinci_platform_package_service.build_multiplatform_package(
        project_name=str(project.name),
        assembly_cut=payload,
        resolved_assets=resolved_assets,
        platforms=platforms,
        root_paths=root_paths,
        audio_mode=request.audio_mode,
    )

    packages = result["packages"]

    package_data = packages.get(platform, packages.get(platforms[0]))
    if not package_data:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")

    fcpxml_bytes, fcpxml_filename = package_data["fcpxml"]
    relink_reports = davinci_platform_package_service.generate_multiplatform_relink_report(
        project_name=str(project.name),
        assembly_cut=payload,
        resolved_assets=resolved_assets,
        platforms=platforms,
        root_paths=root_paths,
    )

    package_file_name = f"{str(project.name).replace(' ', '_')}_davinci_{platform}.fcpxml"
    deliverable = await delivery_service.create_project_file_deliverable(
        db,
        project_id=project_id,
        organization_id=str(project.organization_id),
        name=f"{project.name} DaVinci {platform.title()} Export",
        format_type="FCPXML",
        file_bytes=fcpxml_bytes,
        file_name=package_file_name,
        mime_type="application/xml",
        category="editorial",
        manifest_payload={
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "assembly_cut_id": assembly.get("id"),
            "platform": platform,
            "root_path": root_path,
            "audio_mode": request.audio_mode,
            "include_media": request.include_media,
        },
        payload_extra={
            "assembly_cut_id": assembly.get("id"),
            "platform": platform,
            "root_path": root_path,
        },
    )

    file_path = deliverable.delivery_payload.get("file_path")
    if not file_path:
        raise HTTPException(status_code=500, detail="DaVinci package export path missing")

    return DavinciPlatformExportResponse(
        deliverable_id=str(deliverable.id),
        file_name=package_file_name,
        file_path=file_path,
        assembly_cut_id=assembly.get("id"),
        platform=platform,
        root_path=root_path,
    )
