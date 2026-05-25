from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from dependencies.tenant_context import get_tenant_context, require_write_permission
from schemas.auth_schema import TenantContext
from schemas.editorial_assembly_schema import (
    AssemblyTimeline,
    BuildAssemblyRequest,
    ImportReportsRequest,
    ImportReportsResponse,
    MatchTakesRequest,
    MatchTakesResponse,
    NLEExportRequest,
    NLEExportResult,
    RelinkReport,
    ReportLookupResponse,
    ScanMediaRequest,
    ScanMediaResponse,
)
from services.editorial_assembly_core_service import editorial_assembly_core_service
from services.editorial_export_adapter_service import (
    EditorialExportAdapterError,
    editorial_export_adapter_service,
)


router = APIRouter(prefix="/api/projects", tags=["editorial-assembly"])


@router.post(
    "/{project_id}/editorial/scan-media",
    response_model=ScanMediaResponse,
    dependencies=[Depends(require_write_permission)],
)
async def scan_editorial_media(
    project_id: str,
    request: ScanMediaRequest,
) -> ScanMediaResponse:
    root_paths = request.all_roots()
    assets, warnings = editorial_assembly_core_service.scan_media_roots(
        project_id=project_id,
        root_paths=root_paths,
        recursive=request.recursive,
        max_files=request.max_files,
    )
    return ScanMediaResponse(
        project_id=project_id,
        scanned_roots=root_paths,
        assets=assets,
        warnings=warnings,
    )


@router.post(
    "/{project_id}/editorial/import-reports",
    response_model=ImportReportsResponse,
    dependencies=[Depends(require_write_permission)],
)
async def import_editorial_reports(
    project_id: str,
    request: ImportReportsRequest,
) -> ImportReportsResponse:
    return editorial_assembly_core_service.import_reports(
        project_id=project_id,
        camera_reports=request.camera_reports,
        sound_reports=request.sound_reports,
        script_notes=request.script_notes,
        director_notes=request.director_notes,
    )


@router.post(
    "/{project_id}/editorial/match-takes",
    response_model=MatchTakesResponse,
    dependencies=[Depends(require_write_permission)],
)
async def match_editorial_takes(
    project_id: str,
    request: MatchTakesRequest,
) -> MatchTakesResponse:
    slate_matches, take_decisions, sync_candidates, warnings = editorial_assembly_core_service.match_takes(
        project_id=project_id,
        media_assets=request.media_assets,
        camera_reports=request.camera_reports,
        sound_reports=request.sound_reports,
        script_notes=request.script_notes,
        director_notes=request.director_notes,
    )
    return MatchTakesResponse(
        project_id=project_id,
        slate_matches=slate_matches,
        take_decisions=take_decisions,
        sync_candidates=sync_candidates,
        warnings=warnings,
    )


@router.post(
    "/{project_id}/editorial/build-assembly",
    response_model=AssemblyTimeline,
    dependencies=[Depends(require_write_permission)],
)
async def build_editorial_assembly(
    project_id: str,
    request: BuildAssemblyRequest,
) -> AssemblyTimeline:
    return editorial_assembly_core_service.build_neutral_assembly(
        project_id=project_id,
        take_decisions=request.take_decisions,
        media_assets=request.media_assets,
        name=request.name,
        fps=request.fps,
        allow_missing_audio=request.allow_missing_audio,
    )


@router.post(
    "/{project_id}/editorial/export/resolve",
    response_model=NLEExportResult,
    dependencies=[Depends(require_write_permission)],
)
async def export_editorial_resolve(
    project_id: str,
    request: NLEExportRequest,
) -> NLEExportResult:
    return _export_for_nle(project_id=project_id, expected_nle="resolve", request=request)


@router.post(
    "/{project_id}/editorial/export/premiere",
    response_model=NLEExportResult,
    dependencies=[Depends(require_write_permission)],
)
async def export_editorial_premiere(
    project_id: str,
    request: NLEExportRequest,
) -> NLEExportResult:
    return _export_for_nle(project_id=project_id, expected_nle="premiere", request=request)


@router.post(
    "/{project_id}/editorial/export/avid",
    response_model=NLEExportResult,
    dependencies=[Depends(require_write_permission)],
)
async def export_editorial_avid(
    project_id: str,
    request: NLEExportRequest,
) -> NLEExportResult:
    return _export_for_nle(project_id=project_id, expected_nle="avid", request=request)


@router.get("/{project_id}/editorial/reports/{report_id}", response_model=ReportLookupResponse)
async def get_editorial_assembly_report(
    project_id: str,
    report_id: str,
    _tenant: TenantContext = Depends(get_tenant_context),
) -> ReportLookupResponse:
    return ReportLookupResponse(
        project_id=project_id,
        report_id=report_id,
        status="contract_only_not_persisted",
        relink_report=RelinkReport(),
        warnings=["editorial_assembly_reports_are_not_persisted_in_editorial_2a"],
    )


def _export_for_nle(*, project_id: str, expected_nle: str, request: NLEExportRequest) -> NLEExportResult:
    if request.nle_type != expected_nle:
        raise HTTPException(
            status_code=400,
            detail=f"Request nle_type must be '{expected_nle}' for this endpoint",
        )
    timeline = request.timeline or _empty_timeline(project_id=project_id, nle_type=expected_nle)
    try:
        return editorial_export_adapter_service.export(request, timeline)
    except EditorialExportAdapterError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _empty_timeline(*, project_id: str, nle_type: str) -> AssemblyTimeline:
    return AssemblyTimeline(
        id=f"assembly-{project_id}-{nle_type}-contract",
        project_id=project_id,
        name=f"CID {nle_type.title()} Contract Assembly",
        fps=24.0,
        total_duration_frames=0,
        sequences=[],
    )
