from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from models.core import Project
from models.document import ProjectDocumentType, ProjectDocumentVisibilityScope
from models.integration import (
    ExternalDocumentSyncState,
    ExternalDocumentSyncStatus,
    ExternalFolderSyncMode,
    IntegrationConnection,
    IntegrationConnectionStatus,
    IntegrationProvider,
    IntegrationToken,
    ProjectExternalFolderLink,
)
from services.encryption_service import encryption_service
from services.logging_service import logger
from services.project_document_service import project_document_service


@dataclass
class OAuthTokenPayload:
    access_token: str
    refresh_token: str | None
    expires_at: datetime | None
    scope: str | None


class GoogleDriveOAuthStateService:
    def __init__(self) -> None:
        self._secret = (
            os.getenv("GOOGLE_DRIVE_OAUTH_STATE_SECRET")
            or os.getenv("AUTH_SECRET_KEY")
            or str(config.get("auth", {}).get("secret_key", ""))
            or os.getenv("APP_SECRET_KEY")
            or str(config.get("app", {}).get("secret_key", ""))
        )
        self._algorithm = str(config.get("auth", {}).get("algorithm", "HS256"))
        if not self._secret:
            raise RuntimeError("Missing Google Drive OAuth state secret")

    def issue(self, *, organization_id: str, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "organization_id": organization_id,
            "user_id": user_id,
            "nonce": secrets.token_urlsafe(24),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, state: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(state, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise HTTPException(status_code=400, detail="Invalid OAuth state") from exc
        if not payload.get("nonce") or not payload.get("organization_id") or not payload.get("user_id"):
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        return payload


class GoogleDriveApiClient:
    AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    DRIVE_BASE_URL = "https://www.googleapis.com/drive/v3"
    DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.readonly"

    def __init__(self) -> None:
        self.client_id = (os.getenv("GOOGLE_DRIVE_CLIENT_ID") or "").strip()
        self.client_secret = (os.getenv("GOOGLE_DRIVE_CLIENT_SECRET") or "").strip()

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def build_authorize_url(self, *, redirect_uri: str, state: str) -> str:
        if not self.is_configured():
            raise HTTPException(status_code=503, detail="Google Drive OAuth is not configured")
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.DRIVE_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
        return str(httpx.URL(self.AUTH_BASE_URL, params=params))

    async def exchange_code(self, *, code: str, redirect_uri: str) -> OAuthTokenPayload:
        if not self.is_configured():
            raise HTTPException(status_code=503, detail="Google Drive OAuth is not configured")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="Google OAuth token exchange failed")
        payload = response.json()
        expires_in = payload.get("expires_in")
        expires_at = None
        if expires_in is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))
        return OAuthTokenPayload(
            access_token=str(payload.get("access_token") or ""),
            refresh_token=payload.get("refresh_token"),
            expires_at=expires_at,
            scope=payload.get("scope"),
        )

    async def refresh_access_token(self, *, refresh_token: str) -> OAuthTokenPayload:
        if not self.is_configured():
            raise HTTPException(status_code=503, detail="Google Drive OAuth is not configured")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="Google OAuth token refresh failed")
        payload = response.json()
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(payload.get("expires_in") or 3600))
        return OAuthTokenPayload(
            access_token=str(payload.get("access_token") or ""),
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=payload.get("scope"),
        )

    async def get_account_email(self, *, access_token: str) -> str | None:
        response = await self._get(
            "/about",
            access_token=access_token,
            params={"fields": "user(emailAddress)"},
        )
        return response.get("user", {}).get("emailAddress")

    async def list_folders(self, *, access_token: str, parent_id: str | None) -> list[dict[str, Any]]:
        clauses = ["mimeType = 'application/vnd.google-apps.folder'", "trashed = false"]
        if parent_id:
            clauses.append(f"'{parent_id}' in parents")
        else:
            clauses.append("'root' in parents")
        response = await self._get(
            "/files",
            access_token=access_token,
            params={
                "q": " and ".join(clauses),
                "fields": "files(id,name,parents)",
                "pageSize": "100",
                "orderBy": "name_natural",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            },
        )
        return list(response.get("files", []))

    async def list_files(self, *, access_token: str, folder_id: str) -> list[dict[str, Any]]:
        q = f"'{folder_id}' in parents and trashed = false"
        response = await self._get(
            "/files",
            access_token=access_token,
            params={
                "q": q,
                "fields": "files(id,name,mimeType,modifiedTime,md5Checksum,size,parents)",
                "pageSize": "200",
                "orderBy": "modifiedTime desc,name_natural",
                "supportsAllDrives": "true",
                "includeItemsFromAllDrives": "true",
            },
        )
        return list(response.get("files", []))

    async def download_file(self, *, access_token: str, file_id: str) -> bytes:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.DRIVE_BASE_URL}/files/{file_id}",
                params={"alt": "media", "supportsAllDrives": "true"},
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="Google Drive download failed")
        return response.content

    async def _get(self, path: str, *, access_token: str, params: dict[str, str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.DRIVE_BASE_URL}{path}",
                params=params,
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=400, detail="Google Drive request failed")
        return response.json()


class GoogleDriveService:
    SUPPORTED_MIME_TYPES = {
        "application/pdf": ".pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "text/plain": ".txt",
    }
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}

    def __init__(self) -> None:
        self.state_service = GoogleDriveOAuthStateService()
        self.client_factory = GoogleDriveApiClient

    def _client(self) -> GoogleDriveApiClient:
        return self.client_factory()

    def resolve_redirect_uri(self, callback_url: str) -> str:
        configured = (os.getenv("GOOGLE_DRIVE_REDIRECT_URI") or "").strip()
        return configured or callback_url

    def _as_utc(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    async def get_connection(
        self, db: AsyncSession, *, organization_id: str
    ) -> IntegrationConnection | None:
        result = await db.execute(
            select(IntegrationConnection)
            .where(
                IntegrationConnection.organization_id == organization_id,
                IntegrationConnection.provider == IntegrationProvider.GOOGLE_DRIVE,
            )
            .order_by(IntegrationConnection.updated_at.desc(), IntegrationConnection.id.desc())
        )
        return result.scalars().first()

    async def get_connection_with_token(
        self, db: AsyncSession, *, organization_id: str
    ) -> tuple[IntegrationConnection | None, IntegrationToken | None]:
        connection = await self.get_connection(db, organization_id=organization_id)
        if connection is None:
            return None, None
        token_result = await db.execute(
            select(IntegrationToken).where(
                IntegrationToken.connection_id == connection.id,
                IntegrationToken.organization_id == organization_id,
            )
        )
        return connection, token_result.scalar_one_or_none()

    async def ensure_access_token(
        self, db: AsyncSession, *, organization_id: str
    ) -> tuple[IntegrationConnection, IntegrationToken, str]:
        connection, token = await self.get_connection_with_token(db, organization_id=organization_id)
        if connection is None or token is None or connection.status != IntegrationConnectionStatus.CONNECTED:
            raise HTTPException(status_code=404, detail="Google Drive connection not found")

        access_token = encryption_service.decrypt(token.access_token_encrypted)
        refresh_token = encryption_service.decrypt(token.refresh_token_encrypted)
        now = datetime.now(timezone.utc)
        token_expiry_at = self._as_utc(token.token_expiry_at)
        if token_expiry_at and token_expiry_at <= now + timedelta(seconds=60):
            if not refresh_token:
                raise HTTPException(status_code=400, detail="Google Drive refresh token unavailable")
            refreshed = await self._client().refresh_access_token(refresh_token=refresh_token)
            access_token = refreshed.access_token
            token.access_token_encrypted = encryption_service.encrypt(refreshed.access_token)
            token.token_expiry_at = refreshed.expires_at
            if refreshed.scope:
                token.scope = refreshed.scope
            connection.status = IntegrationConnectionStatus.CONNECTED
            await db.commit()
            await db.refresh(connection)
            await db.refresh(token)
        return connection, token, access_token or ""

    async def connect_with_code(
        self,
        db: AsyncSession,
        *,
        organization_id: str,
        code: str,
        redirect_uri: str,
    ) -> IntegrationConnection:
        oauth_payload = await self._client().exchange_code(code=code, redirect_uri=redirect_uri)
        if not oauth_payload.access_token:
            raise HTTPException(status_code=400, detail="Google OAuth access token missing")

        account_email = await self._client().get_account_email(access_token=oauth_payload.access_token)
        connection, token = await self.get_connection_with_token(db, organization_id=organization_id)
        if connection is None:
            connection = IntegrationConnection(
                organization_id=organization_id,
                provider=IntegrationProvider.GOOGLE_DRIVE,
                external_account_email=account_email,
                status=IntegrationConnectionStatus.CONNECTED,
            )
            db.add(connection)
            await db.flush()
        else:
            connection.external_account_email = account_email
            connection.status = IntegrationConnectionStatus.CONNECTED

        if token is None:
            token = IntegrationToken(
                connection_id=connection.id,
                organization_id=organization_id,
                access_token_encrypted=encryption_service.encrypt(oauth_payload.access_token) or "",
                refresh_token_encrypted=encryption_service.encrypt(oauth_payload.refresh_token),
                token_expiry_at=oauth_payload.expires_at,
                scope=oauth_payload.scope,
            )
            db.add(token)
        else:
            token.access_token_encrypted = encryption_service.encrypt(oauth_payload.access_token) or ""
            if oauth_payload.refresh_token:
                token.refresh_token_encrypted = encryption_service.encrypt(oauth_payload.refresh_token)
            token.token_expiry_at = oauth_payload.expires_at
            token.scope = oauth_payload.scope

        await db.commit()
        await db.refresh(connection)
        return connection

    async def disconnect(self, db: AsyncSession, *, organization_id: str) -> dict[str, Any]:
        connection, token = await self.get_connection_with_token(db, organization_id=organization_id)
        if connection is None:
            return {"provider": IntegrationProvider.GOOGLE_DRIVE, "status": IntegrationConnectionStatus.DISCONNECTED}
        connection.status = IntegrationConnectionStatus.DISCONNECTED
        if token is not None:
            await db.delete(token)
        await db.commit()
        return {"provider": connection.provider, "status": connection.status}

    async def list_folders(
        self, db: AsyncSession, *, organization_id: str, parent_id: str | None
    ) -> list[dict[str, Any]]:
        _connection, _token, access_token = await self.ensure_access_token(db, organization_id=organization_id)
        folders = await self._client().list_folders(access_token=access_token, parent_id=parent_id)
        path_prefix = "Drive"
        if parent_id:
            path_prefix = f"Drive/{parent_id}"
        return [
            {
                "folder_id": str(item.get("id") or ""),
                "name": str(item.get("name") or ""),
                "parent_id": (item.get("parents") or [None])[0],
                "path_hint": f"{path_prefix}/{str(item.get('name') or '').strip('/')}",
            }
            for item in folders
        ]

    async def list_folder_links(
        self, db: AsyncSession, *, project_id: str, organization_id: str
    ) -> list[ProjectExternalFolderLink]:
        result = await db.execute(
            select(ProjectExternalFolderLink)
            .where(
                ProjectExternalFolderLink.project_id == project_id,
                ProjectExternalFolderLink.organization_id == organization_id,
                ProjectExternalFolderLink.provider == IntegrationProvider.GOOGLE_DRIVE,
            )
            .order_by(ProjectExternalFolderLink.created_at.desc(), ProjectExternalFolderLink.id.desc())
        )
        return list(result.scalars().all())

    async def create_folder_link(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        external_folder_id: str,
        external_folder_name: str,
    ) -> ProjectExternalFolderLink:
        connection = await self.get_connection(db, organization_id=organization_id)
        if connection is None or connection.status != IntegrationConnectionStatus.CONNECTED:
            raise HTTPException(status_code=404, detail="Google Drive connection not found")

        result = await db.execute(
            select(ProjectExternalFolderLink).where(
                ProjectExternalFolderLink.project_id == project_id,
                ProjectExternalFolderLink.organization_id == organization_id,
                ProjectExternalFolderLink.provider == IntegrationProvider.GOOGLE_DRIVE,
                ProjectExternalFolderLink.external_folder_id == external_folder_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            existing.external_folder_name = external_folder_name
            await db.commit()
            await db.refresh(existing)
            return existing

        link = ProjectExternalFolderLink(
            project_id=project_id,
            organization_id=organization_id,
            connection_id=connection.id,
            provider=IntegrationProvider.GOOGLE_DRIVE,
            external_folder_id=external_folder_id,
            external_folder_name=external_folder_name,
            sync_mode=ExternalFolderSyncMode.IMPORT_ONLY,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return link

    async def delete_folder_link(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        link_id: str,
    ) -> bool:
        result = await db.execute(
            select(ProjectExternalFolderLink).where(
                ProjectExternalFolderLink.id == link_id,
                ProjectExternalFolderLink.project_id == project_id,
                ProjectExternalFolderLink.organization_id == organization_id,
                ProjectExternalFolderLink.provider == IntegrationProvider.GOOGLE_DRIVE,
            )
        )
        link = result.scalar_one_or_none()
        if link is None:
            return False
        await db.delete(link)
        await db.commit()
        return True

    async def get_project_for_tenant(
        self, db: AsyncSession, *, project_id: str, organization_id: str
    ) -> Project | None:
        return await project_document_service.get_project_for_tenant(
            db,
            project_id=project_id,
            organization_id=organization_id,
        )

    def _is_supported_file(self, item: dict[str, Any]) -> bool:
        mime_type = str(item.get("mimeType") or "").strip().lower()
        name = str(item.get("name") or "")
        extension = os.path.splitext(name)[1].lower()
        return mime_type in self.SUPPORTED_MIME_TYPES or extension in self.SUPPORTED_EXTENSIONS

    def _resolved_mime_type(self, item: dict[str, Any]) -> str:
        mime_type = str(item.get("mimeType") or "application/octet-stream").strip().lower()
        if mime_type in self.SUPPORTED_MIME_TYPES:
            return mime_type
        extension = os.path.splitext(str(item.get("name") or ""))[1].lower()
        if extension == ".pdf":
            return "application/pdf"
        if extension == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if extension == ".txt":
            return "text/plain"
        return mime_type

    def _parse_modified_time(self, value: str | None) -> datetime | None:
        if not value:
            return None
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)

    async def sync_project(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        project = await self.get_project_for_tenant(
            db,
            project_id=project_id,
            organization_id=organization_id,
        )
        if project is None:
            raise HTTPException(status_code=403, detail="Project not accessible for tenant")

        links = await self.list_folder_links(db, project_id=project_id, organization_id=organization_id)
        if not links:
            raise HTTPException(status_code=400, detail="No Google Drive folder linked to project")

        _connection, _token, access_token = await self.ensure_access_token(db, organization_id=organization_id)

        imported = 0
        updated = 0
        skipped = 0
        errors = 0
        seen_file_ids: set[str] = set()
        now = datetime.now(timezone.utc)
        state_map_result = await db.execute(
            select(ExternalDocumentSyncState).where(
                ExternalDocumentSyncState.project_id == project_id,
                ExternalDocumentSyncState.organization_id == organization_id,
                ExternalDocumentSyncState.provider == IntegrationProvider.GOOGLE_DRIVE,
            )
        )
        state_map = {item.external_file_id: item for item in state_map_result.scalars().all()}

        for link in links:
            files = await self._client().list_files(access_token=access_token, folder_id=link.external_folder_id)
            for file_item in files:
                if not self._is_supported_file(file_item):
                    continue
                external_file_id = str(file_item.get("id") or "")
                if not external_file_id:
                    continue
                seen_file_ids.add(external_file_id)
                modified_time = self._parse_modified_time(file_item.get("modifiedTime"))
                checksum = str(file_item.get("md5Checksum") or "") or None
                sync_state = state_map.get(external_file_id)
                should_sync = sync_state is None
                if sync_state is not None:
                    if self._as_utc(sync_state.external_modified_time) != self._as_utc(modified_time):
                        should_sync = True
                    if checksum and sync_state.external_checksum != checksum:
                        should_sync = True

                if sync_state is None:
                    sync_state = ExternalDocumentSyncState(
                        project_id=project_id,
                        organization_id=organization_id,
                        provider=IntegrationProvider.GOOGLE_DRIVE,
                        external_file_id=external_file_id,
                        sync_status=ExternalDocumentSyncStatus.PENDING,
                    )
                    db.add(sync_state)
                    await db.flush()
                    state_map[external_file_id] = sync_state

                sync_state.external_modified_time = modified_time
                sync_state.external_checksum = checksum
                sync_state.last_seen_at = now

                if not should_sync:
                    sync_state.sync_status = ExternalDocumentSyncStatus.SKIPPED
                    skipped += 1
                    continue

                try:
                    file_bytes = await self._client().download_file(
                        access_token=access_token,
                        file_id=external_file_id,
                    )
                    derived_checksum = hashlib.sha256(file_bytes).hexdigest()
                    document = await project_document_service.import_document_bytes(
                        db,
                        project=project,
                        uploaded_by_user_id=user_id,
                        document_type=ProjectDocumentType.OTHER,
                        visibility_scope=ProjectDocumentVisibilityScope.PROJECT,
                        file_name=str(file_item.get("name") or f"drive_{external_file_id}.bin"),
                        mime_type=self._resolved_mime_type(file_item),
                        file_bytes=file_bytes,
                        checksum_override=derived_checksum,
                        existing_document_id=sync_state.linked_project_document_id,
                    )
                    previously_linked = sync_state.linked_project_document_id is not None
                    sync_state.linked_project_document_id = document.id
                    sync_state.external_checksum = checksum or derived_checksum
                    sync_state.sync_status = ExternalDocumentSyncStatus.SYNCED
                    if previously_linked:
                        updated += 1
                    else:
                        imported += 1
                except Exception as exc:
                    sync_state.sync_status = ExternalDocumentSyncStatus.ERROR
                    errors += 1
                    logger.warning(
                        "Google Drive sync failed organization_id=%s project_id=%s file_id=%s error=%s",
                        organization_id,
                        project_id,
                        external_file_id,
                        str(exc),
                    )

            link.last_sync_at = now

        await db.commit()
        stale_count = 0
        for state in state_map.values():
            if (
                state.external_file_id not in seen_file_ids
                and self._as_utc(state.last_seen_at)
                and self._as_utc(state.last_seen_at) < now
            ):
                stale_count += 1

        return {
            "project_id": project_id,
            "provider": IntegrationProvider.GOOGLE_DRIVE,
            "status": "completed" if errors == 0 else "completed_with_errors",
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "errors": errors,
            "stale": stale_count,
            "linked_folders": len(links),
            "synced_at": now,
        }

    async def get_sync_status(
        self, db: AsyncSession, *, project_id: str, organization_id: str
    ) -> dict[str, Any]:
        links = await self.list_folder_links(db, project_id=project_id, organization_id=organization_id)
        state_result = await db.execute(
            select(ExternalDocumentSyncState).where(
                ExternalDocumentSyncState.project_id == project_id,
                ExternalDocumentSyncState.organization_id == organization_id,
                ExternalDocumentSyncState.provider == IntegrationProvider.GOOGLE_DRIVE,
            )
        )
        states = list(state_result.scalars().all())
        latest_sync_at = None
        if links:
            latest_sync_at = max((link.last_sync_at for link in links if link.last_sync_at), default=None)

        items = []
        for state in states:
            stale = bool(
                self._as_utc(latest_sync_at)
                and self._as_utc(state.last_seen_at)
                and self._as_utc(state.last_seen_at) < self._as_utc(latest_sync_at)
            )
            items.append(
                {
                    "external_file_id": state.external_file_id,
                    "linked_project_document_id": state.linked_project_document_id,
                    "sync_status": state.sync_status,
                    "external_modified_time": state.external_modified_time,
                    "external_checksum": state.external_checksum,
                    "last_seen_at": state.last_seen_at,
                    "stale": stale,
                }
            )
        return {
            "project_id": project_id,
            "provider": IntegrationProvider.GOOGLE_DRIVE,
            "links": [
                {
                    "id": link.id,
                    "project_id": link.project_id,
                    "organization_id": link.organization_id,
                    "connection_id": link.connection_id,
                    "provider": link.provider,
                    "external_folder_id": link.external_folder_id,
                    "external_folder_name": link.external_folder_name,
                    "sync_mode": link.sync_mode,
                    "last_sync_at": link.last_sync_at,
                    "created_at": link.created_at,
                    "updated_at": link.updated_at,
                }
                for link in links
            ],
            "states": items,
            "count": len(items),
            "last_sync_at": latest_sync_at,
        }


google_drive_service = GoogleDriveService()
