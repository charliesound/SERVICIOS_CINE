from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.integration import IntegrationConnectionStatus, IntegrationProvider
from routes.auth_routes import get_tenant_context
from schemas.auth_schema import TenantContext
from schemas.integration_schema import (
    GoogleDriveConnectionStatusResponse,
    GoogleDriveFolderItemResponse,
    GoogleDriveFolderLinkListResponse,
    GoogleDriveLinkFolderRequest,
    GoogleDriveFolderLinkResponse,
    GoogleDriveFolderListResponse,
    GoogleDriveSyncResponse,
    GoogleDriveSyncStateItemResponse,
    GoogleDriveSyncStatusResponse,
)
from services.google_drive_service import google_drive_service


router = APIRouter(tags=["google-drive-integrations"])


def _link_to_response(link) -> GoogleDriveFolderLinkResponse:
    return GoogleDriveFolderLinkResponse(
        id=str(link.id),
        project_id=str(link.project_id),
        organization_id=str(link.organization_id),
        connection_id=str(link.connection_id),
        provider=str(link.provider),
        external_folder_id=str(link.external_folder_id),
        external_folder_name=str(link.external_folder_name),
        sync_mode=str(link.sync_mode),
        last_sync_at=link.last_sync_at,
        created_at=link.created_at,
        updated_at=link.updated_at,
    )


async def _get_project_or_403(project_id: str, db: AsyncSession, tenant: TenantContext):
    project = await google_drive_service.get_project_for_tenant(
        db,
        project_id=project_id,
        organization_id=tenant.organization_id,
    )
    if project is None:
        raise HTTPException(status_code=403, detail="Project not accessible for tenant")
    return project


@router.get(
    "/api/integrations/google-drive/connect",
    name="google_drive_connect",
)
async def connect_google_drive(
    request: Request,
    tenant: TenantContext = Depends(get_tenant_context),
):
    state = google_drive_service.state_service.issue(
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
    )
    redirect_uri = google_drive_service.resolve_redirect_uri(
        str(request.url_for("google_drive_callback"))
    )
    authorize_url = google_drive_service._client().build_authorize_url(
        redirect_uri=redirect_uri,
        state=state,
    )
    return RedirectResponse(url=authorize_url, status_code=307)


@router.get(
    "/api/integrations/google-drive/callback",
    name="google_drive_callback",
)
async def google_drive_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    payload = google_drive_service.state_service.verify(state)
    redirect_uri = google_drive_service.resolve_redirect_uri(
        str(request.url_for("google_drive_callback"))
    )
    connection = await google_drive_service.connect_with_code(
        db,
        organization_id=str(payload["organization_id"]),
        code=code,
        redirect_uri=redirect_uri,
    )
    return JSONResponse(
        content={
            "provider": IntegrationProvider.GOOGLE_DRIVE,
            "status": connection.status,
            "external_account_email": connection.external_account_email,
        }
    )


@router.get(
    "/api/integrations/google-drive/status",
    response_model=GoogleDriveConnectionStatusResponse,
)
async def google_drive_status(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveConnectionStatusResponse:
    connection, token = await google_drive_service.get_connection_with_token(
        db,
        organization_id=tenant.organization_id,
    )
    status = connection.status if connection else IntegrationConnectionStatus.DISCONNECTED
    return GoogleDriveConnectionStatusResponse(
        provider=IntegrationProvider.GOOGLE_DRIVE,
        status=status,
        connected=bool(connection and status == IntegrationConnectionStatus.CONNECTED and token is not None),
        external_account_email=connection.external_account_email if connection else None,
        scope=token.scope if token else None,
        token_expiry_at=token.token_expiry_at if token else None,
    )


@router.post(
    "/api/integrations/google-drive/disconnect",
    response_model=GoogleDriveConnectionStatusResponse,
)
async def disconnect_google_drive(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveConnectionStatusResponse:
    result = await google_drive_service.disconnect(db, organization_id=tenant.organization_id)
    return GoogleDriveConnectionStatusResponse(
        provider=result["provider"],
        status=result["status"],
        connected=False,
    )


@router.get(
    "/api/projects/{project_id}/integrations/google-drive/folders",
    response_model=GoogleDriveFolderListResponse,
)
async def list_google_drive_folders(
    project_id: str,
    parent_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveFolderListResponse:
    await _get_project_or_403(project_id, db, tenant)
    folders = await google_drive_service.list_folders(
        db,
        organization_id=tenant.organization_id,
        parent_id=parent_id,
    )
    return GoogleDriveFolderListResponse(
        project_id=project_id,
        count=len(folders),
        folders=[GoogleDriveFolderItemResponse(**item) for item in folders],
    )


@router.post(
    "/api/projects/{project_id}/integrations/google-drive/link-folder",
    response_model=GoogleDriveFolderLinkResponse,
    status_code=201,
)
async def link_google_drive_folder(
    project_id: str,
    payload: GoogleDriveLinkFolderRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveFolderLinkResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    link = await google_drive_service.create_folder_link(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        external_folder_id=payload.external_folder_id,
        external_folder_name=payload.external_folder_name,
    )
    return _link_to_response(link)


@router.get(
    "/api/projects/{project_id}/integrations/google-drive/link-folder",
    response_model=GoogleDriveFolderLinkListResponse,
)
async def list_google_drive_folder_links(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveFolderLinkListResponse:
    project = await _get_project_or_403(project_id, db, tenant)
    links = await google_drive_service.list_folder_links(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
    )
    return GoogleDriveFolderLinkListResponse(
        project_id=project_id,
        count=len(links),
        links=[_link_to_response(link) for link in links],
    )


@router.delete("/api/projects/{project_id}/integrations/google-drive/link-folder/{link_id}")
async def delete_google_drive_folder_link(
    project_id: str,
    link_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    project = await _get_project_or_403(project_id, db, tenant)
    deleted = await google_drive_service.delete_folder_link(
        db,
        project_id=str(project.id),
        organization_id=str(project.organization_id),
        link_id=link_id,
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Linked folder not found")
    return {"project_id": project_id, "link_id": link_id, "status": "deleted"}


@router.post(
    "/api/projects/{project_id}/integrations/google-drive/sync",
    response_model=GoogleDriveSyncResponse,
)
async def sync_google_drive_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveSyncResponse:
    await _get_project_or_403(project_id, db, tenant)
    result = await google_drive_service.sync_project(
        db,
        project_id=project_id,
        organization_id=tenant.organization_id,
        user_id=tenant.user_id,
    )
    return GoogleDriveSyncResponse(**result)


@router.get(
    "/api/projects/{project_id}/integrations/google-drive/sync-status",
    response_model=GoogleDriveSyncStatusResponse,
)
async def google_drive_sync_status(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
) -> GoogleDriveSyncStatusResponse:
    await _get_project_or_403(project_id, db, tenant)
    status = await google_drive_service.get_sync_status(
        db,
        project_id=project_id,
        organization_id=tenant.organization_id,
    )
    return GoogleDriveSyncStatusResponse(
        project_id=status["project_id"],
        provider=status["provider"],
        count=status["count"],
        links=[GoogleDriveFolderLinkResponse(**item) for item in status["links"]],
        states=[GoogleDriveSyncStateItemResponse(**item) for item in status["states"]],
        last_sync_at=status["last_sync_at"],
    )
