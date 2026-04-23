import csv
import json
import mimetypes
import os
import zipfile
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Optional
from xml.etree import ElementTree as ET

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.core import Project
from models.document import (
    ClassificationStatus,
    DocumentAsset,
    DocumentAssetStatus,
    DocumentClassification,
    DocumentExtraction,
    DocumentLink,
    DocumentSourceKind,
    DocumentStructuredData,
    DocumentType,
    ExtractionStatus,
    StructuredReviewStatus,
)
from models.storage import IngestEvent, IngestEventType, MediaAsset, StorageSource
from services.report_service import report_service
from services.storage_service import storage_service


class DocumentService:
    SOUND_REPORT_KEYWORDS = ["roll", "mixer", "boom", "sample rate"]
    CAMERA_REPORT_KEYWORDS = ["camera", "mag", "card", "lens", "fps"]
    SCRIPT_NOTE_KEYWORDS = ["continuity", "best take", "editor note"]
    DIRECTOR_NOTE_KEYWORDS = ["intention", "pacing", "coverage"]
    OPERATOR_NOTE_KEYWORDS = ["operator", "camera op", "movement", "rig"]

    IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "heic"}
    LEGACY_UNSUPPORTED_EXTENSIONS = {"doc", "xls"}

    DERIVABLE_TYPES = {
        DocumentType.CAMERA_REPORT: "camera",
        DocumentType.SOUND_REPORT: "sound",
        DocumentType.SCRIPT_NOTE: "script",
        DocumentType.DIRECTOR_NOTE: "director",
    }
    NON_DERIVABLE_TYPES = {
        DocumentType.UNKNOWN: "unknown_document",
        DocumentType.OPERATOR_NOTE: "operator_note",
    }

    def _related(self, document: DocumentAsset, relation_name: str):
        return document.__dict__.get(relation_name)

    async def create_document(
        self,
        db: AsyncSession,
        *,
        user_org_id: str,
        payload: dict[str, Any],
        uploaded_by: Optional[str] = None,
    ) -> DocumentAsset:
        media_asset = None
        storage_source = None

        media_asset_id = payload.get("media_asset_id")
        if media_asset_id:
            media_asset = await self._get_media_asset_for_org(
                db, media_asset_id, user_org_id
            )
            if media_asset is None:
                raise HTTPException(status_code=404, detail="Media asset not found")

            organization_id = str(media_asset.organization_id)
            project_id = str(media_asset.project_id)
            storage_source_id = str(media_asset.storage_source_id)
            original_path = str(media_asset.canonical_path)
            file_name = str(media_asset.file_name)
            file_extension = str(media_asset.file_extension).lower()
            mime_type = getattr(media_asset, "mime_type", None)
            source_kind = DocumentSourceKind.MEDIA_ASSET
        else:
            organization_id = payload.get("organization_id")
            project_id = payload.get("project_id")
            storage_source_id = payload.get("storage_source_id")
            original_path = payload.get("original_path")
            file_name = payload.get("file_name") or (
                os.path.basename(str(original_path)) if original_path else None
            )
            source_kind = payload.get("source_kind") or DocumentSourceKind.PATH
            mime_type = payload.get("mime_type")
            file_extension = Path(file_name or "").suffix.lower().lstrip(".")

            if not organization_id or organization_id != user_org_id:
                raise HTTPException(
                    status_code=403,
                    detail="Cannot create document for a different organization",
                )
            if not project_id:
                raise HTTPException(
                    status_code=400,
                    detail="project_id is required when media_asset_id is not provided",
                )

        await self._ensure_project_access(db, project_id, user_org_id)

        if storage_source_id:
            storage_source = await self._get_storage_source_for_org(
                db, storage_source_id, user_org_id
            )
            if storage_source is None:
                raise HTTPException(status_code=404, detail="Storage source not found")
            if str(storage_source.project_id) != project_id:
                raise HTTPException(
                    status_code=400,
                    detail="storage_source_id does not belong to the provided project",
                )
            if original_path and not self.is_path_within(
                original_path, str(storage_source.mount_path)
            ):
                raise HTTPException(
                    status_code=400,
                    detail="original_path must be within the storage source mount path",
                )

        if not file_name:
            raise HTTPException(
                status_code=400, detail="file_name could not be determined"
            )

        if not file_extension:
            file_extension = Path(file_name).suffix.lower().lstrip(".")

        inferred_mime_type = mime_type or mimetypes.guess_type(file_name)[0]
        initial_status = self.initial_status_for_extension(file_extension)

        document_asset = DocumentAsset(
            organization_id=organization_id,
            project_id=project_id,
            storage_source_id=storage_source_id,
            media_asset_id=media_asset_id,
            file_name=file_name,
            file_extension=file_extension,
            mime_type=inferred_mime_type,
            source_kind=source_kind,
            original_path=original_path,
            uploaded_by=uploaded_by,
            status=initial_status,
        )
        db.add(document_asset)
        await db.commit()
        await db.refresh(document_asset)

        if any(
            payload.get(key)
            for key in (
                "shooting_day_id",
                "sequence_id",
                "scene_id",
                "shot_id",
                "media_asset_id",
            )
        ):
            link = DocumentLink(
                document_asset_id=str(document_asset.id),
                organization_id=organization_id,
                project_id=project_id,
                shooting_day_id=payload.get("shooting_day_id"),
                sequence_id=payload.get("sequence_id"),
                scene_id=payload.get("scene_id"),
                shot_id=payload.get("shot_id"),
                media_asset_id=media_asset_id,
            )
            db.add(link)
            await db.commit()

        await self._log_document_event(
            db,
            document_asset=document_asset,
            event_type=IngestEventType.DOCUMENT_REGISTERED,
            payload={
                "document_asset_id": str(document_asset.id),
                "source_kind": source_kind,
                "file_name": file_name,
            },
            created_by=uploaded_by,
        )
        return await self.get_document(db, str(document_asset.id), user_org_id)

    async def update_document(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        *,
        status: Optional[str] = None,
        original_path: Optional[str] = None,
        structured_payload_json: Optional[dict[str, Any]] = None,
        review_status: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> DocumentAsset:
        if status is not None:
            document.status = status.strip().lower()
        if original_path is not None:
            document.original_path = original_path.strip() or None
        if structured_payload_json is not None:
            structured_data = self._related(document, "structured_data")
            if structured_data is None:
                schema_type = (
                    getattr(self._related(document, "classification"), "doc_type", None)
                    or DocumentType.UNKNOWN
                )
                structured_data = DocumentStructuredData(
                    document_asset_id=str(document.id),
                    schema_type=str(schema_type),
                    structured_payload_json="{}",
                )
                db.add(structured_data)
                await db.flush()
            structured_data.structured_payload_json = json.dumps(
                structured_payload_json, ensure_ascii=False
            )
            if review_status is not None:
                structured_data.review_status = review_status.strip().lower()
        await db.commit()
        await db.refresh(document)
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_UPDATED,
            payload={
                "status": getattr(document, "status", None),
                "original_path": getattr(document, "original_path", None),
                "structured_payload_updated": structured_payload_json is not None,
                "review_status": review_status,
            },
            created_by=updated_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def list_documents(
        self,
        db: AsyncSession,
        organization_id: str,
        *,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        doc_type: Optional[str] = None,
    ) -> list[DocumentAsset]:
        query = (
            select(DocumentAsset)
            .options(
                selectinload(DocumentAsset.extraction),
                selectinload(DocumentAsset.classification),
                selectinload(DocumentAsset.structured_data),
                selectinload(DocumentAsset.links),
            )
            .where(DocumentAsset.organization_id == organization_id)
        )
        if project_id:
            query = query.where(DocumentAsset.project_id == project_id)
        if status:
            query = query.where(DocumentAsset.status == status.strip().lower())
        if doc_type:
            query = query.join(DocumentAsset.classification).where(
                DocumentClassification.doc_type == doc_type.strip().lower()
            )
        query = query.order_by(DocumentAsset.created_at.desc(), DocumentAsset.id.desc())
        result = await db.execute(query)
        return result.scalars().unique().all()

    async def get_document(
        self, db: AsyncSession, document_id: str, organization_id: str
    ) -> Optional[DocumentAsset]:
        result = await db.execute(
            select(DocumentAsset)
            .options(
                selectinload(DocumentAsset.extraction),
                selectinload(DocumentAsset.classification),
                selectinload(DocumentAsset.structured_data),
                selectinload(DocumentAsset.links),
            )
            .where(
                DocumentAsset.id == document_id,
                DocumentAsset.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def extract_document(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        created_by: Optional[str] = None,
    ) -> DocumentAsset:
        extraction = self._related(document, "extraction")
        if extraction is None:
            extraction = DocumentExtraction(document_asset_id=str(document.id))
            db.add(extraction)
            await db.flush()

        extracted = self._extract_content(document)
        extraction.extraction_status = extracted["status"]
        extraction.extraction_engine = extracted.get("engine")
        extraction.raw_text = extracted.get("raw_text")
        extraction.extracted_table_json = (
            json.dumps(extracted.get("table"), ensure_ascii=False)
            if extracted.get("table") is not None
            else None
        )
        extraction.error_message = extracted.get("error_message")

        document.status = self._map_extraction_status_to_document_status(
            extracted["status"]
        )
        await db.commit()
        await db.refresh(document)

        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_EXTRACTED,
            payload={
                "extraction_status": extracted["status"],
                "extraction_engine": extracted.get("engine"),
            },
            created_by=created_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def extract_text_directly(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        raw_text: str,
        created_by: Optional[str] = None,
    ) -> DocumentAsset:
        extraction = self._related(document, "extraction")
        if extraction is None:
            extraction = DocumentExtraction(document_asset_id=str(document.id))
            db.add(extraction)
            await db.flush()

        extraction.extraction_status = ExtractionStatus.COMPLETED
        extraction.extraction_engine = "text_direct"
        extraction.raw_text = raw_text
        extraction.extracted_table_json = None
        extraction.error_message = None

        document.status = DocumentAssetStatus.EXTRACTED
        await db.commit()
        await db.refresh(document)

        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_EXTRACTED,
            payload={
                "extraction_status": ExtractionStatus.COMPLETED,
                "extraction_engine": "text_direct",
            },
            created_by=created_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def classify_document(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        created_by: Optional[str] = None,
    ) -> DocumentAsset:
        if self._related(document, "extraction") is None:
            document = await self.extract_document(db, document, created_by=created_by)

        extraction = self._related(document, "extraction")
        text = self._build_classification_text(extraction)
        doc_type, confidence = self._classify_text(text)

        classification = self._related(document, "classification")
        if classification is None:
            classification = DocumentClassification(document_asset_id=str(document.id))
            db.add(classification)
            await db.flush()

        classification.doc_type = doc_type
        classification.classification_status = ClassificationStatus.COMPLETED
        classification.confidence_score = confidence
        document.status = DocumentAssetStatus.CLASSIFIED

        await db.commit()
        await db.refresh(document)
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_CLASSIFIED,
            payload={"doc_type": doc_type, "confidence_score": confidence},
            created_by=created_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def structure_document(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        created_by: Optional[str] = None,
    ) -> DocumentAsset:
        if self._related(document, "classification") is None:
            document = await self.classify_document(db, document, created_by=created_by)

        extraction = self._related(document, "extraction")
        classification = self._related(document, "classification")
        payload = self._build_structured_payload(document, extraction, classification)

        structured_data = self._related(document, "structured_data")
        if structured_data is None:
            structured_data = DocumentStructuredData(
                document_asset_id=str(document.id),
                schema_type=payload["schema_type"],
                structured_payload_json="{}",
            )
            db.add(structured_data)
            await db.flush()

        structured_data.schema_type = payload["schema_type"]
        structured_data.structured_payload_json = json.dumps(
            payload, ensure_ascii=False
        )
        structured_data.review_status = StructuredReviewStatus.DRAFT
        structured_data.approved_by = None
        structured_data.approved_at = None
        document.status = DocumentAssetStatus.STRUCTURED

        await db.commit()
        await db.refresh(document)
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_STRUCTURED,
            payload={"schema_type": payload["schema_type"]},
            created_by=created_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def approve_document(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        approved_by: Optional[str] = None,
    ) -> DocumentAsset:
        if self._related(document, "structured_data") is None:
            raise HTTPException(
                status_code=400, detail="Document must be structured before approval"
            )

        structured_data = self._related(document, "structured_data")
        structured_data.review_status = StructuredReviewStatus.APPROVED
        structured_data.approved_by = approved_by
        structured_data.approved_at = datetime.now(timezone.utc)
        document.status = DocumentAssetStatus.APPROVED

        await db.commit()
        await db.refresh(document)
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_APPROVED,
            payload={"review_status": StructuredReviewStatus.APPROVED},
            created_by=approved_by,
        )
        return await self.get_document(
            db, str(document.id), str(document.organization_id)
        )

    async def create_script_document(
        self,
        db: AsyncSession,
        *,
        user_org_id: str,
        project_id: str,
        file_name: str,
        raw_text: str,
        uploaded_by: Optional[str] = None,
    ) -> DocumentAsset:
        document_asset = DocumentAsset(
            organization_id=user_org_id,
            project_id=project_id,
            storage_source_id=None,
            media_asset_id=None,
            file_name=file_name,
            file_extension="txt",
            mime_type="text/plain",
            source_kind=DocumentSourceKind.SCRIPT_TEXT,
            original_path=None,
            uploaded_by=uploaded_by,
            status=DocumentAssetStatus.REGISTERED,
        )
        db.add(document_asset)
        await db.commit()
        await db.refresh(document_asset)

        document_asset = await self.extract_text_directly(
            db, document_asset, raw_text=raw_text, created_by=uploaded_by
        )

        await self._log_document_event(
            db,
            document_asset=document_asset,
            event_type=IngestEventType.DOCUMENT_REGISTERED,
            payload={
                "document_asset_id": str(document_asset.id),
                "source_kind": DocumentSourceKind.SCRIPT_TEXT,
                "file_name": file_name,
            },
            created_by=uploaded_by,
        )
        return await self.get_document(db, str(document_asset.id), user_org_id)

    async def list_document_events(
        self, db: AsyncSession, document: DocumentAsset
    ) -> list[IngestEvent]:
        result = await db.execute(
            select(IngestEvent)
            .where(
                IngestEvent.organization_id == str(document.organization_id),
                IngestEvent.document_asset_id == str(document.id),
            )
            .order_by(IngestEvent.created_at.asc(), IngestEvent.id.asc())
        )
        return result.scalars().all()

    async def _ensure_project_access(
        self, db: AsyncSession, project_id: str, organization_id: str
    ) -> None:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if str(project.organization_id) != organization_id:
            raise HTTPException(status_code=403, detail="Access denied to this project")

    async def _get_media_asset_for_org(
        self, db: AsyncSession, media_asset_id: str, organization_id: str
    ) -> Optional[MediaAsset]:
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == media_asset_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _get_storage_source_for_org(
        self, db: AsyncSession, storage_source_id: str, organization_id: str
    ) -> Optional[StorageSource]:
        result = await db.execute(
            select(StorageSource).where(
                StorageSource.id == storage_source_id,
                StorageSource.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def _log_document_event(
        self,
        db: AsyncSession,
        *,
        document_asset: DocumentAsset,
        event_type: str,
        payload: dict[str, Any],
        created_by: Optional[str],
    ) -> None:
        await storage_service.log_ingest_event(
            db,
            organization_id=str(document_asset.organization_id),
            project_id=str(document_asset.project_id),
            storage_source_id=str(document_asset.storage_source_id)
            if getattr(document_asset, "storage_source_id", None)
            else None,
            document_asset_id=str(document_asset.id),
            event_type=event_type,
            event_payload=payload,
            created_by=created_by,
        )

    def initial_status_for_extension(self, extension: str) -> str:
        ext = extension.lower().lstrip(".")
        if ext in self.IMAGE_EXTENSIONS:
            return DocumentAssetStatus.PENDING_OCR
        if ext in self.LEGACY_UNSUPPORTED_EXTENSIONS:
            return DocumentAssetStatus.UNSUPPORTED
        return DocumentAssetStatus.REGISTERED

    def is_path_within(self, child_path: str, parent_path: str) -> bool:
        try:
            child = os.path.realpath(os.path.normpath(child_path.strip()))
            parent = os.path.realpath(os.path.normpath(parent_path.strip()))
            return os.path.commonpath([child, parent]) == parent
        except ValueError:
            return False

    def _extract_content(self, document: DocumentAsset) -> dict[str, Any]:
        extension = str(document.file_extension or "").lower().lstrip(".")
        path = getattr(document, "original_path", None)

        if not path:
            return {
                "status": ExtractionStatus.FAILED,
                "engine": "none",
                "raw_text": None,
                "table": None,
                "error_message": "Document has no original_path",
            }

        if extension in self.IMAGE_EXTENSIONS:
            return {
                "status": ExtractionStatus.PENDING_OCR,
                "engine": "pending_ocr",
                "raw_text": None,
                "table": None,
                "error_message": "OCR is not enabled for image-based documents",
            }

        if extension in self.LEGACY_UNSUPPORTED_EXTENSIONS:
            return {
                "status": ExtractionStatus.UNSUPPORTED,
                "engine": "unsupported_legacy",
                "raw_text": None,
                "table": None,
                "error_message": f"Legacy .{extension} parsing is not supported",
            }

        if extension == "txt":
            return self._extract_txt(path)
        if extension == "csv":
            return self._extract_csv(path)
        if extension == "docx":
            return self._extract_docx(path)
        if extension == "xlsx":
            return self._extract_xlsx(path)
        if extension == "pdf":
            return self._extract_pdf(path)

        return {
            "status": ExtractionStatus.UNSUPPORTED,
            "engine": "unsupported",
            "raw_text": None,
            "table": None,
            "error_message": f"No extraction strategy for .{extension}",
        }

    def _extract_txt(self, path: str) -> dict[str, Any]:
        raw_text = None
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                with open(path, "r", encoding=encoding) as handle:
                    raw_text = handle.read()
                break
            except UnicodeDecodeError:
                continue
        if raw_text is None:
            return {
                "status": ExtractionStatus.FAILED,
                "engine": "text",
                "raw_text": None,
                "table": None,
                "error_message": "Unable to decode TXT file",
            }
        return {
            "status": ExtractionStatus.COMPLETED,
            "engine": "text",
            "raw_text": raw_text,
            "table": None,
            "error_message": None,
        }

    def _extract_csv(self, path: str) -> dict[str, Any]:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
        headers = rows[0] if rows else []
        body = rows[1:] if len(rows) > 1 else []
        table = {
            "headers": headers,
            "rows": body,
            "row_count": len(body),
            "column_count": len(headers),
        }
        raw_text = "\n".join([", ".join(row) for row in rows])
        return {
            "status": ExtractionStatus.COMPLETED,
            "engine": "csv",
            "raw_text": raw_text,
            "table": table,
            "error_message": None,
        }

    def _extract_docx(self, path: str) -> dict[str, Any]:
        namespace = {
            "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        }
        try:
            with zipfile.ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml")
            root = ET.fromstring(document_xml)
        except Exception as exc:
            return {
                "status": ExtractionStatus.FAILED,
                "engine": "docx_zip",
                "raw_text": None,
                "table": None,
                "error_message": str(exc),
            }
        text_nodes = [node.text or "" for node in root.findall(".//w:t", namespace)]
        raw_text = " ".join(text_nodes).strip()
        return {
            "status": ExtractionStatus.COMPLETED
            if raw_text
            else ExtractionStatus.FAILED,
            "engine": "docx_zip",
            "raw_text": raw_text or None,
            "table": None,
            "error_message": None if raw_text else "No text found in DOCX",
        }

    def _extract_xlsx(self, path: str) -> dict[str, Any]:
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        try:
            with zipfile.ZipFile(path) as archive:
                shared_strings = self._load_shared_strings(archive, namespace)
                sheet_names = sorted(
                    name
                    for name in archive.namelist()
                    if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
                )
                sheets = []
                text_parts: list[str] = []
                for index, sheet_name in enumerate(sheet_names, start=1):
                    root = ET.fromstring(archive.read(sheet_name))
                    rows = []
                    for row in root.findall(".//x:sheetData/x:row", namespace):
                        values = []
                        for cell in row.findall("x:c", namespace):
                            cell_type = cell.get("t")
                            value_node = cell.find("x:v", namespace)
                            value_text = (
                                value_node.text if value_node is not None else ""
                            )
                            if cell_type == "s" and value_text:
                                try:
                                    values.append(shared_strings[int(value_text)])
                                except Exception:
                                    values.append(value_text)
                            else:
                                values.append(value_text or "")
                        rows.append(values)
                        text_parts.extend(values)
                    sheets.append(
                        {
                            "name": f"sheet{index}",
                            "headers": rows[0] if rows else [],
                            "rows": rows[1:] if len(rows) > 1 else [],
                            "row_count": max(len(rows) - 1, 0),
                        }
                    )
        except Exception as exc:
            return {
                "status": ExtractionStatus.FAILED,
                "engine": "xlsx_zip",
                "raw_text": None,
                "table": None,
                "error_message": str(exc),
            }
        table = {"sheet_count": len(sheets), "sheets": sheets}
        return {
            "status": ExtractionStatus.COMPLETED,
            "engine": "xlsx_zip",
            "raw_text": "\n".join(filter(None, text_parts)) or None,
            "table": table,
            "error_message": None,
        }

    def _load_shared_strings(
        self, archive: zipfile.ZipFile, namespace: dict[str, str]
    ) -> list[str]:
        if "xl/sharedStrings.xml" not in archive.namelist():
            return []
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        values = []
        for item in root.findall("x:si", namespace):
            texts = [node.text or "" for node in item.findall(".//x:t", namespace)]
            values.append("".join(texts))
        return values

    def _extract_pdf(self, path: str) -> dict[str, Any]:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            return {
                "status": ExtractionStatus.UNSUPPORTED,
                "engine": "pypdf_missing",
                "raw_text": None,
                "table": None,
                "error_message": "PDF extraction requires pypdf, which is not installed",
            }

        try:
            reader = PdfReader(path)
            raw_text = "\n".join(
                (page.extract_text() or "") for page in reader.pages
            ).strip()
            if not raw_text:
                return {
                    "status": ExtractionStatus.PENDING_OCR,
                    "engine": "pypdf",
                    "raw_text": None,
                    "table": None,
                    "error_message": "No extractable PDF text found; OCR is required",
                }
            return {
                "status": ExtractionStatus.COMPLETED,
                "engine": "pypdf",
                "raw_text": raw_text,
                "table": None,
                "error_message": None,
            }
        except Exception as exc:
            return {
                "status": ExtractionStatus.FAILED,
                "engine": "pypdf",
                "raw_text": None,
                "table": None,
                "error_message": str(exc),
            }

    def _map_extraction_status_to_document_status(self, extraction_status: str) -> str:
        if extraction_status == ExtractionStatus.COMPLETED:
            return DocumentAssetStatus.EXTRACTED
        if extraction_status == ExtractionStatus.PENDING_OCR:
            return DocumentAssetStatus.PENDING_OCR
        if extraction_status == ExtractionStatus.UNSUPPORTED:
            return DocumentAssetStatus.UNSUPPORTED
        return DocumentAssetStatus.ERROR

    def _build_classification_text(
        self, extraction: Optional[DocumentExtraction]
    ) -> str:
        if extraction is None:
            return ""
        parts = []
        if extraction.raw_text:
            parts.append(extraction.raw_text)
        if extraction.extracted_table_json:
            parts.append(extraction.extracted_table_json)
        return "\n".join(parts).lower()

    def _classify_text(self, text: str) -> tuple[str, Optional[float]]:
        checks = [
            (DocumentType.SOUND_REPORT, self.SOUND_REPORT_KEYWORDS),
            (DocumentType.CAMERA_REPORT, self.CAMERA_REPORT_KEYWORDS),
            (DocumentType.SCRIPT_NOTE, self.SCRIPT_NOTE_KEYWORDS),
            (DocumentType.DIRECTOR_NOTE, self.DIRECTOR_NOTE_KEYWORDS),
            (DocumentType.OPERATOR_NOTE, self.OPERATOR_NOTE_KEYWORDS),
        ]
        best_type = DocumentType.UNKNOWN
        best_score = 0.0
        for doc_type, keywords in checks:
            matches = sum(1 for keyword in keywords if keyword in text)
            score = matches / len(keywords)
            if score > best_score:
                best_type = doc_type
                best_score = score
        if best_type == DocumentType.UNKNOWN:
            return best_type, 0.0
        return best_type, round(best_score, 2)

    def _build_structured_payload(
        self,
        document: DocumentAsset,
        extraction: Optional[DocumentExtraction],
        classification: Optional[DocumentClassification],
    ) -> dict[str, Any]:
        table_payload = None
        if extraction and extraction.extracted_table_json:
            try:
                table_payload = json.loads(extraction.extracted_table_json)
            except Exception:
                table_payload = None

        text_preview = None
        if extraction and extraction.raw_text:
            text_preview = extraction.raw_text[:500]

        return {
            "schema_type": classification.doc_type
            if classification
            else DocumentType.UNKNOWN,
            "document_id": str(document.id),
            "file_name": str(document.file_name),
            "source_kind": str(document.source_kind),
            "doc_type": classification.doc_type
            if classification
            else DocumentType.UNKNOWN,
            "summary": {
                "status": extraction.extraction_status if extraction else None,
                "text_length": len(extraction.raw_text)
                if extraction and extraction.raw_text
                else 0,
                "table_rows": self._count_table_rows(table_payload),
                "mime_type": getattr(document, "mime_type", None),
            },
            "text_preview": text_preview,
            "table_preview": table_payload,
            "metadata": {
                "file_extension": str(document.file_extension),
                "original_path": getattr(document, "original_path", None),
                "storage_source_id": getattr(document, "storage_source_id", None),
                "media_asset_id": getattr(document, "media_asset_id", None),
            },
        }

    def _count_table_rows(self, table_payload: Any) -> int:
        if not table_payload:
            return 0
        if isinstance(table_payload, dict) and "row_count" in table_payload:
            return int(table_payload.get("row_count") or 0)
        if isinstance(table_payload, dict) and "sheets" in table_payload:
            return sum(
                int(sheet.get("row_count") or 0)
                for sheet in table_payload.get("sheets", [])
            )
        return 0

    def is_derivable(self, document: DocumentAsset) -> tuple[bool, str]:
        classification = self._related(document, "classification")
        if classification is None:
            return False, "Document has not been classified"
        doc_type = str(classification.doc_type)
        if doc_type in self.NON_DERIVABLE_TYPES:
            return False, f"Document type '{doc_type}' is not derivable to a report"
        if doc_type not in self.DERIVABLE_TYPES:
            return False, f"Document type '{doc_type}' is not a known derivable type"
        structured_data = self._related(document, "structured_data")
        if structured_data is None:
            return False, "Document has no structured data"
        if (
            getattr(structured_data, "review_status", None)
            != StructuredReviewStatus.APPROVED
        ):
            return False, "Document structured data is not approved"
        return True, ""

    def get_report_type(self, document: DocumentAsset) -> Optional[str]:
        classification = self._related(document, "classification")
        if classification is None:
            return None
        return self.DERIVABLE_TYPES.get(str(classification.doc_type))

    async def derive_preview(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:
        allowed, reason = self.is_derivable(document)
        report_type = self.get_report_type(document)
        if not allowed:
            await self._log_document_event(
                db,
                document_asset=document,
                event_type=IngestEventType.DOCUMENT_DERIVE_PREVIEW,
                payload={
                    "allowed": False,
                    "reason": reason,
                    "target_report_type": report_type,
                },
                created_by=created_by,
            )
            return {
                "target_report_type": report_type or "",
                "initial_report_payload": {},
                "source_document_id": str(document.id),
                "allowed": False,
                "reason": reason,
            }
        prefill = report_service._build_prefill(report_type, document)
        links = self._related(document, "links") or []
        link = links[0] if links else None
        structured_data = self._related(document, "structured_data")
        if structured_data:
            try:
                payload = json.loads(structured_data.structured_payload_json)
                prefill["project_id"] = str(document.project_id)
                prefill["organization_id"] = str(document.organization_id)
                prefill["document_asset_id"] = str(document.id)
                prefill["media_asset_id"] = getattr(document, "media_asset_id", None)
                if link:
                    prefill["scene_id"] = getattr(link, "scene_id", None)
                    prefill["shot_id"] = getattr(link, "shot_id", None)
                    prefill["shooting_day_id"] = getattr(link, "shooting_day_id", None)
                    prefill["sequence_id"] = getattr(link, "sequence_id", None)
            except Exception:
                pass
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_DERIVE_PREVIEW,
            payload={"allowed": True, "target_report_type": report_type},
            created_by=created_by,
        )
        return {
            "target_report_type": report_type,
            "initial_report_payload": prefill,
            "source_document_id": str(document.id),
            "allowed": True,
            "reason": None,
        }

    async def derive_report(
        self,
        db: AsyncSession,
        document: DocumentAsset,
        report_payload: dict[str, Any],
        report_type: str,
        created_by: Optional[str] = None,
    ) -> dict[str, Any]:
        allowed, reason = self.is_derivable(document)
        if not allowed:
            await self._log_document_event(
                db,
                document_asset=document,
                event_type=IngestEventType.DOCUMENT_DERIVE_REPORT_REJECTED,
                payload={"allowed": False, "reason": reason},
                created_by=created_by,
            )
            raise HTTPException(
                status_code=400, detail=reason or "Document is not derivable"
            )
        existing_reports = await report_service.list_reports(
            db,
            report_type,
            str(document.organization_id),
            document_asset_id=str(document.id),
        )
        if existing_reports:
            await self._log_document_event(
                db,
                document_asset=document,
                event_type=IngestEventType.DOCUMENT_DERIVE_REPORT_REJECTED,
                payload={"reason": "Duplicate report already exists for this document"},
                created_by=created_by,
            )
            raise HTTPException(
                status_code=409,
                detail="A report of this type already exists for this document. Duplicates are not allowed.",
            )
        payload = {
            **report_payload,
            "document_asset_id": str(document.id),
            "media_asset_id": getattr(document, "media_asset_id", None),
        }
        report = await report_service.create_report(
            db,
            report_type,
            payload,
            user_org_id=str(document.organization_id),
            created_by=created_by,
        )
        await self._log_document_event(
            db,
            document_asset=document,
            event_type=IngestEventType.DOCUMENT_DERIVE_REPORT_CREATED,
            payload={
                "report_id": str(report.id),
                "report_type": report_type,
            },
            created_by=created_by,
        )
        await storage_service.log_ingest_event(
            db,
            organization_id=str(document.organization_id),
            project_id=str(document.project_id),
            storage_source_id=str(document.storage_source_id)
            if getattr(document, "storage_source_id", None)
            else None,
            document_asset_id=str(document.id),
            event_type=IngestEventType.REPORT_LINKED_TO_DOCUMENT,
            event_payload={"report_id": str(report.id), "report_type": report_type},
            created_by=created_by,
        )
        return {
            "report_id": str(report.id),
            "report_type": report_type,
            "message": "Report derived and created successfully",
        }


document_service = DocumentService()
