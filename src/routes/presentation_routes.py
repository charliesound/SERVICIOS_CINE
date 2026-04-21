from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.presentation_schema import (
    PresentationFilmstripResponse,
    PresentationPdfExportResponse,
)
from services.pdf_service import PdfRenderError, pdf_service
from services.presentation_service import (
    PresentationForbiddenError,
    PresentationNotFoundError,
    PresentationPreviewUnavailableError,
    presentation_service,
)


router = APIRouter(prefix="/api/projects", tags=["presentation"])


def _build_pdf_filename(project_name: str) -> str:
    normalized = "".join(ch if ch.isalnum() else "_" for ch in project_name.strip())
    sanitized = "_".join(part for part in normalized.split("_") if part)
    return f"{(sanitized or 'project')[:80]}_filmstrip.pdf"


def _raise_presentation_http_error(exc: ValueError) -> None:
    if isinstance(exc, PresentationForbiddenError):
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    if isinstance(exc, PresentationNotFoundError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, PresentationPreviewUnavailableError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{project_id}/presentation/filmstrip", response_model=PresentationFilmstripResponse)
async def get_project_filmstrip(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PresentationFilmstripResponse:
    try:
        return await presentation_service.build_filmstrip(
            db,
            project_id=project_id,
            tenant=tenant,
        )
    except ValueError as exc:
        _raise_presentation_http_error(exc)


@router.get("/{project_id}/presentation/filmstrip.html", response_class=HTMLResponse)
async def preview_project_filmstrip_html(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> HTMLResponse:
    try:
        payload = await presentation_service.build_filmstrip(
            db,
            project_id=project_id,
            tenant=tenant,
        )
    except ValueError as exc:
        _raise_presentation_http_error(exc)

    return HTMLResponse(content=pdf_service.render_filmstrip_html(payload))


@router.get("/{project_id}/presentation/export/pdf")
async def download_project_filmstrip_pdf(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> Response:
    try:
        payload = await presentation_service.build_filmstrip(
            db,
            project_id=project_id,
            tenant=tenant,
        )
        render_payload = await presentation_service.build_pdf_render_payload(
            db,
            payload=payload,
            tenant=tenant,
        )
        pdf_bytes = pdf_service.export_filmstrip_pdf(render_payload)
    except ValueError as exc:
        _raise_presentation_http_error(exc)
    except PdfRenderError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    filename = _build_pdf_filename(str(payload.project.name))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/presentation/assets/{asset_id}/preview")
async def preview_project_asset(
    project_id: str,
    asset_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    try:
        payload = await presentation_service.get_asset_preview_payload(
            db,
            project_id=project_id,
            asset_id=asset_id,
            tenant=tenant,
        )
    except ValueError as exc:
        _raise_presentation_http_error(exc)

    if payload["kind"] == "file":
        return FileResponse(
            path=payload["path"],
            media_type=payload["media_type"],
            filename=payload["filename"],
            content_disposition_type="inline",
        )
    if payload["kind"] == "json":
        return JSONResponse(content=payload["payload"])

    raise HTTPException(status_code=500, detail="Unexpected asset preview control flow")


@router.post("/{project_id}/presentation/export-pdf", response_model=PresentationPdfExportResponse)
async def export_project_filmstrip_pdf(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> PresentationPdfExportResponse:
    try:
        payload = await presentation_service.build_filmstrip(
            db,
            project_id=project_id,
            tenant=tenant,
        )
        render_payload = await presentation_service.build_pdf_render_payload(
            db,
            payload=payload,
            tenant=tenant,
        )
    except ValueError as exc:
        _raise_presentation_http_error(exc)

    try:
        pdf_bytes = pdf_service.export_filmstrip_pdf(render_payload)
    except PdfRenderError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return PresentationPdfExportResponse(
        status="ready",
        detail=(
            "PDF generated successfully. "
            f"Bytes={len(pdf_bytes)}. Deprecated wrapper: use GET /api/projects/{project_id}/presentation/export/pdf to download the file."
        ),
    )
