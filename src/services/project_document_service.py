from __future__ import annotations

import hashlib
import json
import os
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple
from xml.etree import ElementTree as ET

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.document import (
    DocumentChunk,
    ProjectDocument,
    ProjectDocumentType,
    ProjectDocumentUploadStatus,
    ProjectDocumentVisibilityScope,
)
from models.matcher import MatcherJob, MatcherJobStatus
from services.project_document_rag_service import project_document_rag_service
from services.queue_service import queue_service


class ProjectDocumentService:
    ALLOWED_MIME_TYPES = {
        ".pdf": {"application/pdf", "application/octet-stream"},
        ".docx": {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/zip",
            "application/octet-stream",
        },
        ".txt": {"text/plain", "application/octet-stream", "text/markdown"},
    }
    ALLOWED_DOCUMENT_TYPES = {
        ProjectDocumentType.SCRIPT,
        ProjectDocumentType.BUDGET,
        ProjectDocumentType.CONTRACT,
        ProjectDocumentType.TREATMENT,
        ProjectDocumentType.FINANCE_PLAN,
        ProjectDocumentType.OTHER,
    }
    ALLOWED_VISIBILITY_SCOPES = {
        ProjectDocumentVisibilityScope.PROJECT,
        ProjectDocumentVisibilityScope.ORGANIZATION_PRIVATE,
    }

    def __init__(self) -> None:
        self.storage_root = Path(
            os.getenv(
                "PROJECT_DOCUMENT_STORAGE_ROOT",
                "/opt/SERVICIOS_CINE/storage/project_documents",
            )
        ).resolve()
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.max_file_size_bytes = int(
            os.getenv("PROJECT_DOCUMENT_MAX_FILE_SIZE_BYTES", str(10 * 1024 * 1024))
        )

    async def get_project_for_tenant(
        self, db: AsyncSession, project_id: str, organization_id: str
    ) -> Project | None:
        result = await db.execute(
            select(Project).where(
                Project.id == project_id,
                Project.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    def _safe_file_name(self, file_name: str) -> str:
        sanitized = os.path.basename(file_name).strip().replace(" ", "_")
        cleaned = "".join(
            character if character.isalnum() or character in {"-", "_", "."} else "_"
            for character in sanitized
        )
        return cleaned or f"document_{uuid.uuid4().hex}.bin"

    def _validate_extension_and_mime(self, file_name: str, mime_type: str | None) -> str:
        extension = Path(file_name).suffix.lower()
        if extension not in self.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported document extension")
        normalized_mime_type = (mime_type or "application/octet-stream").strip().lower()
        if normalized_mime_type not in self.ALLOWED_MIME_TYPES[extension]:
            raise HTTPException(status_code=400, detail="Unsupported MIME type")
        return extension

    def _validate_document_type(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in self.ALLOWED_DOCUMENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid document_type")
        return normalized

    def _validate_visibility_scope(self, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in self.ALLOWED_VISIBILITY_SCOPES:
            raise HTTPException(status_code=400, detail="Invalid visibility_scope")
        return normalized

    async def _read_upload_bytes(self, upload: UploadFile) -> bytes:
        payload = await upload.read()
        if not payload:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(payload) > self.max_file_size_bytes:
            raise HTTPException(status_code=413, detail="Uploaded file exceeds configured max size")
        return payload

    def _build_storage_path(
        self, organization_id: str, project_id: str, safe_file_name: str
    ) -> Path:
        target_dir = self.storage_root / organization_id / project_id / "documents"
        target_dir.mkdir(parents=True, exist_ok=True)
        stored_name = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:12]}_{safe_file_name}"
        return target_dir / stored_name

    def _extract_text(self, file_path: Path, extension: str) -> str:
        if extension == ".txt":
            for encoding in ("utf-8", "utf-8-sig", "latin-1"):
                try:
                    return file_path.read_text(encoding=encoding)
                except UnicodeDecodeError:
                    continue
            return file_path.read_text(errors="ignore")
        if extension == ".pdf":
            reader = PdfReader(str(file_path))
            parts: list[str] = []
            for page in reader.pages:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text.strip())
            return "\n\n".join(parts)
        if extension == ".docx":
            parts: list[str] = []
            namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            with zipfile.ZipFile(file_path) as archive:
                for member in archive.namelist():
                    if not member.startswith("word/") or not member.endswith(".xml"):
                        continue
                    root = ET.fromstring(archive.read(member))
                    for paragraph in root.findall(".//w:p", namespace):
                        text_parts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
                        joined = "".join(text_parts).strip()
                        if joined:
                            parts.append(joined)
            return "\n".join(parts)
        raise RuntimeError("Unsupported extraction path")

    async def import_document_bytes(
        self,
        db: AsyncSession,
        *,
        project: Project,
        uploaded_by_user_id: str,
        document_type: str,
        visibility_scope: str,
        file_name: str,
        mime_type: str,
        file_bytes: bytes,
        checksum_override: str | None = None,
        existing_document_id: str | None = None,
    ) -> ProjectDocument:
        normalized_document_type = self._validate_document_type(document_type)
        normalized_visibility_scope = self._validate_visibility_scope(visibility_scope)
        safe_file_name = self._safe_file_name(file_name or "document.bin")
        extension = self._validate_extension_and_mime(safe_file_name, mime_type)
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        if len(file_bytes) > self.max_file_size_bytes:
            raise HTTPException(status_code=413, detail="Uploaded file exceeds configured max size")

        checksum = checksum_override or hashlib.sha256(file_bytes).hexdigest()
        storage_path = self._build_storage_path(
            str(project.organization_id), str(project.id), safe_file_name
        )
        storage_path.write_bytes(file_bytes)

        document = None
        previous_file_path = None
        if existing_document_id:
            document = await self.get_document(
                db,
                project_id=str(project.id),
                organization_id=str(project.organization_id),
                document_id=existing_document_id,
            )
            if document is not None:
                previous_file_path = Path(document.storage_path)

        if document is None:
            document = ProjectDocument(
                project_id=str(project.id),
                organization_id=str(project.organization_id),
                uploaded_by_user_id=uploaded_by_user_id,
                document_type=normalized_document_type,
                upload_status=ProjectDocumentUploadStatus.PROCESSING,
                file_name=safe_file_name,
                mime_type=(mime_type or "application/octet-stream").strip().lower(),
                file_size=float(len(file_bytes)),
                storage_path=str(storage_path),
                checksum=checksum,
                extracted_text=None,
                visibility_scope=normalized_visibility_scope,
                error_message=None,
            )
            db.add(document)
            await db.flush()
        else:
            document.uploaded_by_user_id = uploaded_by_user_id
            document.document_type = normalized_document_type
            document.upload_status = ProjectDocumentUploadStatus.PROCESSING
            document.file_name = safe_file_name
            document.mime_type = (mime_type or "application/octet-stream").strip().lower()
            document.file_size = float(len(file_bytes))
            document.storage_path = str(storage_path)
            document.checksum = checksum
            document.extracted_text = None
            document.visibility_scope = normalized_visibility_scope
            document.error_message = None

        try:
            extracted_text = self._extract_text(storage_path, extension)
            document.extracted_text = extracted_text
            await project_document_rag_service.index_document(
                db,
                document=document,
                force=True,
            )
            document.upload_status = ProjectDocumentUploadStatus.COMPLETED
            document.error_message = None
            
            # After successful document processing, enqueue matcher job if this is a PROJECT-scoped document
            if document.visibility_scope == ProjectDocumentVisibilityScope.PROJECT:
                await self._enqueue_matcher_job_for_document_update(
                    db, 
                    project_id=str(project.id),
                    organization_id=str(project.organization_id),
                    document_id=str(document.id),
                    document_checksum=document.checksum
                )
        except Exception as exc:
            document.upload_status = ProjectDocumentUploadStatus.ERROR
            document.error_message = str(exc)

        await db.commit()
        await db.refresh(document)

        if previous_file_path and previous_file_path.exists() and previous_file_path != storage_path:
            previous_file_path.unlink()

        return document

    async def create_document(
        self,
        db: AsyncSession,
        *,
        project: Project,
        uploaded_by_user_id: str,
        document_type: str,
        visibility_scope: str,
        upload: UploadFile,
    ) -> ProjectDocument:
        file_bytes = await self._read_upload_bytes(upload)
        return await self.import_document_bytes(
            db,
            project=project,
            uploaded_by_user_id=uploaded_by_user_id,
            document_type=document_type,
            visibility_scope=visibility_scope,
            file_name=upload.filename or "document.bin",
            mime_type=upload.content_type or "application/octet-stream",
            file_bytes=file_bytes,
        )

    async def list_documents(
        self, db: AsyncSession, *, project_id: str, organization_id: str
    ) -> list[ProjectDocument]:
        result = await db.execute(
            select(ProjectDocument)
            .where(
                ProjectDocument.project_id == project_id,
                ProjectDocument.organization_id == organization_id,
            )
            .order_by(ProjectDocument.created_at.desc(), ProjectDocument.id.desc())
        )
        return list(result.scalars().all())

    async def get_document(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        document_id: str,
    ) -> ProjectDocument | None:
        result = await db.execute(
            select(ProjectDocument).where(
                ProjectDocument.id == document_id,
                ProjectDocument.project_id == project_id,
                ProjectDocument.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_document(
        self,
        db: AsyncSession,
        *,
        document: ProjectDocument,
    ) -> None:
        file_path = Path(document.storage_path)
        await db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == document.id))
        await db.flush()
        await db.delete(document)
        await db.commit()
        if file_path.exists():
            file_path.unlink()
        parent_dir = file_path.parent
        while parent_dir != self.storage_root and parent_dir.exists():
            if any(parent_dir.iterdir()):
                break
            parent_dir.rmdir()
            parent_dir = parent_dir.parent

    def ensure_downloadable_file(self, document: ProjectDocument) -> Path:
        file_path = Path(document.storage_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Stored document file not found")
        return file_path


    async def _enqueue_matcher_job_for_document_update(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        document_id: str,
        document_checksum: str
    ) -> None:
        """Enqueue a matcher job when a project document is updated/completed.
        
        This method implements idempotency by checking if a completed job already exists
        with the same input hash for the project.
        """
        from sqlalchemy import select
        
        # Compute input hash based on:
        # 1. All PROJECT-scoped documents for this project with their checksums
        # 2. All relevant funding calls for the organization (using ingested_at as version)
        # 3. Matcher evaluation version (hardcoded for now, could be configurable)
        
        # Get all completed PROJECT-scoped documents for this project
        from models.document import ProjectDocument, ProjectDocumentUploadStatus, ProjectDocumentVisibilityScope
        
        docs_result = await db.execute(
            select(ProjectDocument.id, ProjectDocument.checksum)
            .where(
                ProjectDocument.project_id == project_id,
                ProjectDocument.organization_id == organization_id,
                ProjectDocument.visibility_scope == ProjectDocumentVisibilityScope.PROJECT,
                ProjectDocument.upload_status == ProjectDocumentUploadStatus.COMPLETED
            )
            .order_by(ProjectDocument.id)  # Order for consistent hash
        )
        document_entries = [(str(row.id), str(row.checksum)) for row in docs_result.fetchall()]
        
        # Get all funding calls for the organization (relevant for matching)
        from models.production import FundingCall
        
        calls_result = await db.execute(
            select(FundingCall.id, FundingCall.ingested_at)
            .where(FundingCall.organization_id == organization_id)
            .order_by(FundingCall.id)  # Order for consistent hash
        )
        call_entries = [(str(row.id), row.ingested_at.isoformat() if row.ingested_at else "") 
                       for row in calls_result.fetchall()]
        
        # Matcher evaluation version (could be made configurable)
        evaluation_version = "v1.0"
        
        # Create input hash
        hash_input = {
            "documents": document_entries,
            "funding_calls": call_entries,
            "evaluation_version": evaluation_version
        }
        
        hash_string = json.dumps(hash_input, sort_keys=True)
        input_hash = hashlib.sha256(hash_string.encode()).hexdigest()
        
        # Check if we already have a completed job with this input hash
        existing_job_result = await db.execute(
            select(MatcherJob)
            .where(
                MatcherJob.project_id == project_id,
                MatcherJob.organization_id == organization_id,
                MatcherJob.input_hash == input_hash,
                MatcherJob.status.in_([MatcherJobStatus.COMPLETED, MatcherJobStatus.SKIPPED])
            )
        )
        existing_job = existing_job_result.scalar_one_or_none()
        
        if existing_job:
            # Job already processed, skip
            return
            
        # Check if there's already a pending/queued job with same hash (avoid duplicates in queue)
        pending_job_result = await db.execute(
            select(MatcherJob)
            .where(
                MatcherJob.project_id == project_id,
                MatcherJob.organization_id == organization_id,
                MatcherJob.input_hash == input_hash,
                MatcherJob.status.in_([MatcherJobStatus.PENDING, MatcherJobStatus.QUEUED, MatcherJobStatus.PROCESSING])
            )
        )
        pending_job = pending_job_result.scalar_one_or_none()
        
        if pending_job:
            # Job already in queue, skip
            return
            
        # Create new matcher job
        new_job = MatcherJob(
            project_id=project_id,
            organization_id=organization_id,
            trigger_type="document_updated",
            trigger_ref_id=document_id,
            input_hash=input_hash,
            status=MatcherJobStatus.QUEUED
        )
        
        db.add(new_job)
        await db.flush()  # Get the ID
        
        # Enqueue job for processing
        await queue_service.enqueue(
            queue_name="matcher",
            job_data={
                "job_id": str(new_job.id),
                "project_id": project_id,
                "organization_id": organization_id
            }
        )

project_document_service = ProjectDocumentService()
