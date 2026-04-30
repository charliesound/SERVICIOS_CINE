from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.delivery_schema import DeliverableResponse
from schemas.presentation_schema import (
    PresentationFilmstripResponse,
    PresentationPdfExportResponse,
)
from services.delivery_service import delivery_service
from services.pdf_service import PdfRenderError, pdf_service
from services.presentation_service import (
    PresentationForbiddenError,
    PresentationNotFoundError,
    PresentationPreviewUnavailableError,
    presentation_service,
)


router = APIRouter(prefix="/api/projects", tags=["presentation"])


def _deliverable_response(deliverable) -> DeliverableResponse:
    payload = getattr(deliverable, "delivery_payload", None)
    created_at = getattr(deliverable, "created_at", None)
    updated_at = getattr(deliverable, "updated_at", None)
    return DeliverableResponse(
        id=str(deliverable.id),
        project_id=str(deliverable.project_id),
        source_review_id=(
            str(deliverable.source_review_id)
            if getattr(deliverable, "source_review_id", None) is not None
            else None
        ),
        name=str(deliverable.name),
        format_type=str(deliverable.format_type),
        delivery_payload=payload if isinstance(payload, dict) else {},
        status=str(deliverable.status),
        created_at=created_at,
        updated_at=updated_at or created_at,
    )


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


@router.post(
    "/{project_id}/presentation/export/pdf/persist",
    response_model=DeliverableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def persist_project_filmstrip_pdf(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> DeliverableResponse:
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

    source_endpoint = f"/api/projects/{project_id}/presentation/export/pdf"
    filename = _build_pdf_filename(str(payload.project.name))
    manifest_summary = presentation_service.build_delivery_manifest(
        payload,
        source_endpoint=source_endpoint,
        pdf_file_name=filename,
    )
    deliverable = await delivery_service.create_project_file_deliverable(
        db,
        project_id=str(payload.project.id),
        organization_id=str(payload.project.organization_id),
        name=f"{payload.project.name} Presentation PDF",
        format_type="PRESENTATION_PDF",
        file_bytes=pdf_bytes,
        file_name=filename,
        mime_type="application/pdf",
        category="presentation_pdf",
        payload_extra={
            "project_name": payload.project.name,
            "presentation_generated_at": datetime.now(timezone.utc).isoformat(),
            "source_endpoint": source_endpoint,
        },
        manifest_payload=manifest_summary,
    )
    return _deliverable_response(deliverable)


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


IMAGE_THUMB_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
THUMB_WIDTH = 320
THUMB_FORMATS = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP"}


@router.get("/{project_id}/presentation/assets/{asset_id}/thumbnail")
async def thumbnail_project_asset(
    project_id: str,
    asset_id: str,
    w: int = Query(default=320, ge=80, le=800),
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

    if payload["kind"] != "file":
        raise HTTPException(status_code=404, detail="Thumbnail not available for this asset type")

    media_type = payload["media_type"]
    if media_type not in IMAGE_THUMB_MIME_TYPES:
        raise HTTPException(status_code=404, detail="Asset is not an image type")

    file_path = Path(payload["path"])
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Asset file not found")

    try:
        with PILImage.open(file_path) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            ratio = w / img.width
            new_height = max(1, int(img.height * ratio))
            img_thumb = img.resize((w, new_height), PILImage.LANCZOS)

            out = BytesIO()
            fmt = THUMB_FORMATS.get(media_type, "JPEG")
            if fmt == "JPEG":
                img_thumb.save(out, format=fmt, quality=75, optimize=True)
            elif fmt == "PNG":
                img_thumb.save(out, format=fmt, optimize=True)
            else:
                img_thumb.save(out, format=fmt, quality=75)

            out.seek(0)
            return Response(
                content=out.getvalue(),
                media_type=media_type,
                headers={
                    "Cache-Control": "public, max-age=86400, stale-while-revalidate=3600",
                    "Vary": "Accept",
                },
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Thumbnail generation failed") from exc


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
