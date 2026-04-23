import json
import re
from datetime import date
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.core import Project
from models.document import DocumentAsset, StructuredReviewStatus
from models.report import CameraReport, DirectorNote, ScriptNote, SoundReport
from models.storage import IngestEventType, MediaAsset
from services.storage_service import storage_service


class ReportService:
    REPORT_CONFIG = {
        "camera": {
            "model": CameraReport,
            "document_type": "camera_report",
            "defaults": {
                "camera_label": "",
                "card_or_mag": "",
                "notes": "",
                "incidents": "",
            },
        },
        "sound": {
            "model": SoundReport,
            "document_type": "sound_report",
            "defaults": {
                "sound_roll": "",
                "notes": "",
                "incidents": "",
            },
        },
        "script": {
            "model": ScriptNote,
            "document_type": "script_note",
            "defaults": {
                "continuity_notes": "",
            },
        },
        "director": {
            "model": DirectorNote,
            "document_type": "director_note",
            "defaults": {
                "intention_note": "",
            },
        },
    }

    async def list_reports(
        self,
        db: AsyncSession,
        report_type: str,
        organization_id: str,
        *,
        project_id: Optional[str] = None,
        document_asset_id: Optional[str] = None,
        media_asset_id: Optional[str] = None,
    ) -> list[Any]:
        config = self._get_config(report_type)
        model = config["model"]
        query = select(model).where(model.organization_id == organization_id)
        if project_id:
            query = query.where(model.project_id == project_id)
        if document_asset_id:
            query = query.where(model.document_asset_id == document_asset_id)
        if media_asset_id:
            query = query.where(model.media_asset_id == media_asset_id)
        query = query.order_by(
            model.report_date.desc(), model.created_at.desc(), model.id.desc()
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_report(
        self,
        db: AsyncSession,
        report_type: str,
        report_id: str,
        organization_id: str,
    ) -> Optional[Any]:
        model = self._get_config(report_type)["model"]
        result = await db.execute(
            select(model).where(
                model.id == report_id, model.organization_id == organization_id
            )
        )
        return result.scalar_one_or_none()

    async def create_report(
        self,
        db: AsyncSession,
        report_type: str,
        payload: dict[str, Any],
        *,
        user_org_id: str,
        created_by: Optional[str] = None,
    ) -> Any:
        config = self._get_config(report_type)
        model = config["model"]
        document_asset = await self._resolve_document_asset(
            db, payload.get("document_asset_id"), user_org_id
        )
        media_asset = await self._resolve_media_asset(
            db, payload.get("media_asset_id"), user_org_id
        )
        if document_asset is None and media_asset is not None:
            document_asset = await self._find_latest_document_for_media_asset(
                db, str(media_asset.id), user_org_id
            )

        if (
            document_asset
            and media_asset
            and getattr(document_asset, "media_asset_id", None)
            and str(document_asset.media_asset_id) != str(media_asset.id)
        ):
            raise HTTPException(
                status_code=400,
                detail="document_asset_id and media_asset_id do not refer to the same media asset",
            )

        organization_id, project_id = await self._resolve_ownership(
            db, payload, user_org_id, document_asset, media_asset
        )
        prefill_payload = self._build_prefill(report_type, document_asset)

        values = {
            **config["defaults"],
            **prefill_payload,
            **self._sanitize_payload(payload),
        }
        values.update(
            {
                "organization_id": organization_id,
                "project_id": project_id,
                "document_asset_id": str(document_asset.id)
                if document_asset
                else payload.get("document_asset_id"),
                "media_asset_id": str(media_asset.id)
                if media_asset
                else (
                    str(document_asset.media_asset_id)
                    if document_asset
                    and getattr(document_asset, "media_asset_id", None)
                    else payload.get("media_asset_id")
                ),
                "created_by": created_by,
            }
        )
        if values.get("report_date") is None:
            values.pop("report_date", None)

        report = model(**values)
        db.add(report)
        await db.commit()
        await db.refresh(report)

        await self._log_report_event(
            db,
            event_type=IngestEventType.REPORT_CREATED,
            report_type=report_type,
            report_id=str(report.id),
            organization_id=organization_id,
            project_id=project_id,
            created_by=created_by,
            document_asset_id=getattr(report, "document_asset_id", None),
            storage_source_id=getattr(document_asset, "storage_source_id", None)
            if document_asset
            else getattr(media_asset, "storage_source_id", None),
        )
        return report

    async def update_report(
        self,
        db: AsyncSession,
        report_type: str,
        report: Any,
        payload: dict[str, Any],
        *,
        updated_by: Optional[str] = None,
    ) -> Any:
        model = type(report)
        del model

        document_asset = await self._resolve_document_asset(
            db,
            payload.get("document_asset_id")
            if "document_asset_id" in payload
            else getattr(report, "document_asset_id", None),
            str(report.organization_id),
        )
        media_asset = await self._resolve_media_asset(
            db,
            payload.get("media_asset_id")
            if "media_asset_id" in payload
            else getattr(report, "media_asset_id", None),
            str(report.organization_id),
        )

        if (
            document_asset
            and media_asset
            and getattr(document_asset, "media_asset_id", None)
            and str(document_asset.media_asset_id) != str(media_asset.id)
        ):
            raise HTTPException(
                status_code=400,
                detail="document_asset_id and media_asset_id do not refer to the same media asset",
            )

        sanitized = self._sanitize_payload(payload)
        for key, value in sanitized.items():
            setattr(report, key, value)

        if document_asset is not None:
            setattr(report, "document_asset_id", str(document_asset.id))
            setattr(report, "project_id", str(document_asset.project_id))
        if media_asset is not None:
            setattr(report, "media_asset_id", str(media_asset.id))
            setattr(report, "project_id", str(media_asset.project_id))

        await db.commit()
        await db.refresh(report)

        await self._log_report_event(
            db,
            event_type=IngestEventType.REPORT_UPDATED,
            report_type=report_type,
            report_id=str(report.id),
            organization_id=str(report.organization_id),
            project_id=str(report.project_id),
            created_by=updated_by,
            document_asset_id=getattr(report, "document_asset_id", None),
            storage_source_id=getattr(document_asset, "storage_source_id", None)
            if document_asset
            else None,
        )
        return report

    def _get_config(self, report_type: str) -> dict[str, Any]:
        normalized = report_type.strip().lower()
        config = self.REPORT_CONFIG.get(normalized)
        if not config:
            raise HTTPException(status_code=400, detail="Unsupported report type")
        return config

    async def _resolve_document_asset(
        self,
        db: AsyncSession,
        document_asset_id: Optional[str],
        organization_id: str,
    ) -> Optional[DocumentAsset]:
        if not document_asset_id:
            return None
        result = await db.execute(
            select(DocumentAsset)
            .options(selectinload(DocumentAsset.structured_data))
            .where(
                DocumentAsset.id == document_asset_id,
                DocumentAsset.organization_id == organization_id,
            )
        )
        document_asset = result.scalar_one_or_none()
        if document_asset is None:
            raise HTTPException(status_code=404, detail="Document asset not found")
        return document_asset

    async def _resolve_media_asset(
        self,
        db: AsyncSession,
        media_asset_id: Optional[str],
        organization_id: str,
    ) -> Optional[MediaAsset]:
        if not media_asset_id:
            return None
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.id == media_asset_id,
                MediaAsset.organization_id == organization_id,
            )
        )
        media_asset = result.scalar_one_or_none()
        if media_asset is None:
            raise HTTPException(status_code=404, detail="Media asset not found")
        return media_asset

    async def _find_latest_document_for_media_asset(
        self,
        db: AsyncSession,
        media_asset_id: str,
        organization_id: str,
    ) -> Optional[DocumentAsset]:
        result = await db.execute(
            select(DocumentAsset)
            .options(selectinload(DocumentAsset.structured_data))
            .where(
                DocumentAsset.media_asset_id == media_asset_id,
                DocumentAsset.organization_id == organization_id,
            )
            .order_by(DocumentAsset.created_at.desc(), DocumentAsset.id.desc())
        )
        return result.scalars().first()

    async def _resolve_ownership(
        self,
        db: AsyncSession,
        payload: dict[str, Any],
        user_org_id: str,
        document_asset: Optional[DocumentAsset],
        media_asset: Optional[MediaAsset],
    ) -> tuple[str, str]:
        organization_id = (
            payload.get("organization_id")
            or (str(document_asset.organization_id) if document_asset else None)
            or (str(media_asset.organization_id) if media_asset else None)
            or user_org_id
        )
        if organization_id != user_org_id:
            raise HTTPException(
                status_code=403,
                detail="Cannot create report for a different organization",
            )

        project_id = (
            payload.get("project_id")
            or (str(document_asset.project_id) if document_asset else None)
            or (str(media_asset.project_id) if media_asset else None)
        )
        if not project_id:
            raise HTTPException(status_code=400, detail="project_id is required")

        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if str(project.organization_id) != user_org_id:
            raise HTTPException(status_code=403, detail="Access denied to this project")

        if document_asset and str(document_asset.project_id) != project_id:
            raise HTTPException(
                status_code=400,
                detail="document_asset_id does not belong to the provided project",
            )
        if media_asset and str(media_asset.project_id) != project_id:
            raise HTTPException(
                status_code=400,
                detail="media_asset_id does not belong to the provided project",
            )

        return organization_id, project_id

    def _sanitize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        sanitized = {}
        for key, value in payload.items():
            if value is None:
                continue
            sanitized[key] = value
        return sanitized

    def _build_prefill(
        self, report_type: str, document_asset: Optional[DocumentAsset]
    ) -> dict[str, Any]:
        if document_asset is None:
            return {}
        structured_data = getattr(document_asset, "structured_data", None)
        if (
            structured_data is None
            or getattr(structured_data, "review_status", None)
            != StructuredReviewStatus.APPROVED
        ):
            return {}

        try:
            payload = json.loads(structured_data.structured_payload_json)
        except Exception:
            return {}

        if (
            payload.get("schema_type")
            != self.REPORT_CONFIG[report_type]["document_type"]
        ):
            return {}

        if report_type == "camera":
            return self._prefill_camera_report(payload)
        if report_type == "sound":
            return self._prefill_sound_report(payload)
        if report_type == "script":
            return self._prefill_script_note(payload)
        if report_type == "director":
            return self._prefill_director_note(payload)
        return {}

    def _prefill_camera_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        row = self._first_table_row(payload)
        text = self._payload_text(payload)
        return {
            "camera_label": self._pick_value(
                row, ["camera", "camera_label", "camera label", "cam"]
            )
            or self._extract_label(text, "camera")
            or "",
            "operator_name": self._pick_value(
                row, ["operator", "operator_name", "camera operator"]
            ),
            "card_or_mag": self._pick_value(row, ["card", "card_or_mag", "mag"])
            or self._extract_label(text, "card")
            or self._extract_label(text, "mag")
            or "",
            "take_reference": self._pick_value(
                row, ["take", "take_reference", "take ref", "take_reference", "shot"]
            ),
            "notes": self._pick_value(row, ["notes"])
            or payload.get("text_preview")
            or "",
            "incidents": self._pick_value(row, ["incidents"]) or "",
        }

    def _prefill_sound_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._payload_text(payload)
        row = self._first_table_row(payload)
        return {
            "sound_roll": self._pick_value(row, ["roll", "sound_roll", "sound roll"])
            or self._extract_label(text, "roll")
            or "",
            "mixer_name": self._pick_value(row, ["mixer", "mixer_name"])
            or self._extract_label(text, "mixer"),
            "boom_operator": self._pick_value(
                row, ["boom", "boom_operator", "boom operator"]
            )
            or self._extract_label(text, "boom"),
            "sample_rate": self._pick_value(row, ["sample_rate", "sample rate"])
            or self._extract_label(text, "sample rate"),
            "bit_depth": self._pick_value(row, ["bit_depth", "bit depth"])
            or self._extract_label(text, "bit depth"),
            "timecode_notes": self._pick_value(row, ["timecode_notes", "timecode"])
            or self._extract_label(text, "timecode"),
            "notes": payload.get("text_preview") or "",
            "incidents": self._pick_value(row, ["incidents"]) or "",
        }

    def _prefill_script_note(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._payload_text(payload)
        row = self._first_table_row(payload)
        return {
            "best_take": self._pick_value(row, ["best_take", "best take"])
            or self._extract_label(text, "best take"),
            "continuity_notes": self._pick_value(
                row, ["continuity_notes", "continuity"]
            )
            or self._extract_label(text, "continuity")
            or payload.get("text_preview")
            or "",
            "editor_note": self._pick_value(row, ["editor_note", "editor note"])
            or self._extract_label(text, "editor note"),
        }

    def _prefill_director_note(self, payload: dict[str, Any]) -> dict[str, Any]:
        text = self._payload_text(payload)
        row = self._first_table_row(payload)
        return {
            "preferred_take": self._pick_value(
                row, ["preferred_take", "preferred take"]
            )
            or self._extract_label(text, "preferred take"),
            "intention_note": self._pick_value(row, ["intention_note", "intention"])
            or self._extract_label(text, "intention")
            or payload.get("text_preview")
            or "",
            "pacing_note": self._pick_value(row, ["pacing_note", "pacing"])
            or self._extract_label(text, "pacing"),
            "coverage_note": self._pick_value(row, ["coverage_note", "coverage"])
            or self._extract_label(text, "coverage"),
        }

    def _first_table_row(self, payload: dict[str, Any]) -> dict[str, str]:
        table = payload.get("table_preview")
        if not isinstance(table, dict):
            return {}
        headers = table.get("headers")
        rows = table.get("rows")
        if isinstance(headers, list) and isinstance(rows, list) and rows:
            first = rows[0]
            if isinstance(first, list):
                return {
                    str(header).strip().lower(): str(first[index]).strip()
                    for index, header in enumerate(headers)
                    if index < len(first)
                }
        return {}

    def _payload_text(self, payload: dict[str, Any]) -> str:
        return str(payload.get("text_preview") or "")

    def _pick_value(self, row: dict[str, str], keys: list[str]) -> Optional[str]:
        normalized = {key.strip().lower(): value for key, value in row.items()}
        for key in keys:
            value = normalized.get(key.strip().lower())
            if value:
                return value
        return None

    def _extract_label(self, text: str, label: str) -> Optional[str]:
        pattern = re.compile(
            rf"{re.escape(label)}\s*[:\-]?\s*([^\n\r,;]+)", re.IGNORECASE
        )
        match = pattern.search(text)
        if not match:
            return None
        return match.group(1).strip() or None

    async def _log_report_event(
        self,
        db: AsyncSession,
        *,
        event_type: str,
        report_type: str,
        report_id: str,
        organization_id: str,
        project_id: str,
        created_by: Optional[str],
        document_asset_id: Optional[str],
        storage_source_id: Optional[str],
    ) -> None:
        await storage_service.log_ingest_event(
            db,
            organization_id=organization_id,
            project_id=project_id,
            storage_source_id=storage_source_id,
            document_asset_id=document_asset_id,
            event_type=event_type,
            event_payload={"report_type": report_type, "report_id": report_id},
            created_by=created_by,
        )


report_service = ReportService()
