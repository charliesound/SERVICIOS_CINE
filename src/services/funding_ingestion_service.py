from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Iterable, List, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.production import FundingCall, FundingRequirement, FundingSource
from models.matcher import MatcherJob, MatcherJobStatus
from schemas.funding_catalog_schema import (
    OPPORTUNITY_TYPE_VALUES,
    PHASE_VALUES,
    REGION_SCOPE_VALUES,
    STATUS_VALUES,
)
from services.queue_service import queue_service


SOURCE_SEED_DATA = [
    {
        "code": "ICAA",
        "name": "ICAA",
        "organization_id": "00000000-0000-0000-0000-000000000001",
        "agency_name": "Instituto de la Cinematografia y de las Artes Audiovisuales",
        "official_url": "https://www.cultura.gob.es/cultura/areas/cine/inicio.html",
        "description": "Catalogo institucional de ayudas cinematograficas de Espana.",
        "region_scope": "spain",
        "country_or_program": "Espana",
    },
    {
        "code": "BOE",
        "name": "BOE Audiovisual",
        "organization_id": "00000000-0000-0000-0000-000000000002",
        "agency_name": "Boletin Oficial del Estado",
        "official_url": "https://www.boe.es/",
        "description": "Publicaciones oficiales y convocatorias vinculadas al sector audiovisual en Espana.",
        "region_scope": "spain",
        "country_or_program": "Espana",
    },
    {
        "code": "CREATIVE_EUROPE_MEDIA",
        "name": "Creative Europe MEDIA",
        "organization_id": "00000000-0000-0000-0000-000000000003",
        "agency_name": "European Commission - Creative Europe Desk",
        "official_url": "https://culture.ec.europa.eu/creative-europe",
        "description": "Programas europeos para desarrollo, distribucion y circulacion audiovisual.",
        "region_scope": "europe",
        "country_or_program": "Creative Europe MEDIA",
    },
    {
        "code": "EURIMAGES",
        "name": "Eurimages",
        "organization_id": "00000000-0000-0000-0000-000000000004",
        "agency_name": "Council of Europe - Eurimages",
        "official_url": "https://www.coe.int/en/web/eurimages",
        "description": "Fondo europeo de apoyo a la coproduccion cinematografica.",
        "region_scope": "europe",
        "country_or_program": "Eurimages",
    },
    {
        "code": "IBERMEDIA",
        "name": "Ibermedia",
        "organization_id": "00000000-0000-0000-0000-000000000005",
        "agency_name": "Programa Ibermedia",
        "official_url": "https://www.programaibermedia.com/",
        "description": "Programa iberoamericano de apoyo a desarrollo y coproduccion.",
        "region_scope": "iberoamerica_latam",
        "country_or_program": "Ibermedia",
    },
]


CALL_SEED_DATA = [
    {
        "source_code": "ICAA",
        "title": "ICAA - Ayudas generales para la produccion de largometrajes sobre proyecto",
        "region_scope": "spain",
        "country_or_program": "Espana",
        "agency_name": "Instituto de la Cinematografia y de las Artes Audiovisuales",
        "official_url": "https://www.cultura.gob.es/cultura/areas/cine/mc/icaa/ayudas/ayudas-produccion-largometrajes.html",
        "description": "Linea estatal para largometrajes y documentales con gasto reconocido y criterios de viabilidad cultural e industrial.",
        "status": "open",
        "open_date": "2026-01-10T00:00:00+00:00",
        "close_date": "2026-03-12T23:59:59+00:00",
        "opportunity_type": "production",
        "phase": "production",
        "max_award_per_project": 1400000.0,
        "total_budget_pool": 30000000.0,
        "currency": "EUR",
        "verification_status": "official",
        "eligibility_json": {
            "eligible_applicants": ["Productoras independientes espanolas"],
            "minimum_nationality": "Obra cinematografica espanola o coproduccion reconocida",
            "minimum_financing": "Financiacion garantizada conforme a convocatoria",
        },
        "requirements_json": {
            "documents": ["Presupuesto", "Plan de financiacion", "Guion o tratamiento", "Acreditacion de derechos"],
            "legal": ["Empresa al corriente de obligaciones tributarias y Seguridad Social"],
        },
        "collaboration_rules_json": {
            "co_production_allowed": True,
            "minimum_partners": 1,
            "notes": ["Compatible con coproducciones oficiales reconocidas"],
        },
        "point_system_json": {
            "criteria": ["Valor cultural", "Solvencia del proyecto", "Impacto industrial"],
        },
        "eligible_formats_json": ["largometraje ficcion", "largometraje documental", "animacion"],
        "notes_json": {
            "source_kind": "institutional_catalog",
            "reference_scope": "representative_real_line",
        },
        "requirement_items": [
            {"category": "legal", "requirement_text": "Empresa productora registrada en Espana", "is_mandatory": True},
            {"category": "finance", "requirement_text": "Plan de financiacion acreditado", "is_mandatory": True},
        ],
    },
    {
        "source_code": "BOE",
        "title": "BOE - Referencia audiovisual a convocatoria de ayudas cinematograficas",
        "region_scope": "spain",
        "country_or_program": "Espana",
        "agency_name": "Boletin Oficial del Estado",
        "official_url": "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-XXXXX",
        "description": "Referencia oficial publicada en BOE para una convocatoria o resolucion con impacto audiovisual.",
        "status": "archived",
        "open_date": "2025-05-01T00:00:00+00:00",
        "close_date": "2025-06-15T23:59:59+00:00",
        "opportunity_type": "industry_support",
        "phase": "development",
        "max_award_per_project": None,
        "total_budget_pool": None,
        "currency": "EUR",
        "verification_status": "official",
        "eligibility_json": {
            "note": "La elegibilidad exacta depende del texto publicado en la resolucion correspondiente.",
        },
        "requirements_json": {
            "documents": ["Consulta de texto BOE aplicable"],
        },
        "collaboration_rules_json": {
            "reference_only": True,
        },
        "point_system_json": {},
        "eligible_formats_json": ["convocatoria audiovisual", "resolucion administrativa"],
        "notes_json": {
            "seed_note": "Registro representativo para enlazar publicaciones BOE con audiovisual.",
        },
        "requirement_items": [
            {"category": "reference", "requirement_text": "Verificar la resolucion y anexos vigentes en BOE", "is_mandatory": True},
        ],
    },
    {
        "source_code": "CREATIVE_EUROPE_MEDIA",
        "title": "Creative Europe MEDIA - European Slate Development",
        "region_scope": "europe",
        "country_or_program": "Creative Europe MEDIA",
        "agency_name": "European Commission - Creative Europe Desk",
        "official_url": "https://culture.ec.europa.eu/funding/creative-europe-media-european-slate-development",
        "description": "Apoyo al desarrollo de paquetes de proyectos audiovisuales con potencial europeo e internacional.",
        "status": "upcoming",
        "open_date": "2026-09-01T00:00:00+00:00",
        "close_date": "2026-12-05T17:00:00+00:00",
        "opportunity_type": "development",
        "phase": "development",
        "max_award_per_project": 510000.0,
        "total_budget_pool": 18000000.0,
        "currency": "EUR",
        "verification_status": "official",
        "eligibility_json": {
            "eligible_applicants": ["Productoras audiovisuales europeas independientes"],
            "portfolio_requirement": "Experiencia reciente en explotacion comercial internacional",
        },
        "requirements_json": {
            "documents": ["Slate de proyectos", "Plan de desarrollo", "Estrategia de audiencias"],
        },
        "collaboration_rules_json": {
            "single_applicant": True,
            "cross_border_dimension": True,
        },
        "point_system_json": {
            "criteria": ["Calidad editorial", "Estrategia europea", "Capacidad operativa"],
        },
        "eligible_formats_json": ["feature film", "animation", "creative documentary", "series"],
        "notes_json": {
            "programme_strand": "MEDIA",
        },
        "requirement_items": [
            {"category": "eligibility", "requirement_text": "Solicitante establecido en pais participante de Creative Europe", "is_mandatory": True},
            {"category": "track_record", "requirement_text": "Demostrar obra distribuida comercialmente", "is_mandatory": True},
        ],
    },
    {
        "source_code": "EURIMAGES",
        "title": "Eurimages - Co-production Support",
        "region_scope": "europe",
        "country_or_program": "Eurimages",
        "agency_name": "Council of Europe - Eurimages",
        "official_url": "https://www.coe.int/en/web/eurimages/co-production-support",
        "description": "Apoyo a coproducciones internacionales entre estados miembros con estructura financiera y artistica validada.",
        "status": "open",
        "open_date": "2026-02-01T00:00:00+00:00",
        "close_date": "2026-04-15T17:00:00+00:00",
        "opportunity_type": "co-production",
        "phase": "production",
        "max_award_per_project": 500000.0,
        "total_budget_pool": 25000000.0,
        "currency": "EUR",
        "verification_status": "official",
        "eligibility_json": {
            "minimum_coproducers": 2,
            "eligible_countries": "Estados miembros de Eurimages",
        },
        "requirements_json": {
            "documents": ["Contrato de coproduccion", "Plan de financiacion", "Cadena de derechos"],
        },
        "collaboration_rules_json": {
            "co_production_required": True,
            "minimum_partners": 2,
            "lead_producer_required": True,
        },
        "point_system_json": {
            "criteria": ["Calidad artistica", "Equilibrio de coproduccion", "Circulacion europea"],
        },
        "eligible_formats_json": ["feature film", "animation", "documentary"],
        "notes_json": {
            "coproduction_focus": "international_european",
        },
        "requirement_items": [
            {"category": "coproduction", "requirement_text": "Al menos dos coproductores de estados miembros distintos", "is_mandatory": True},
            {"category": "finance", "requirement_text": "Financiacion minima asegurada segun reglamento Eurimages", "is_mandatory": True},
        ],
    },
    {
        "source_code": "IBERMEDIA",
        "title": "Ibermedia - Coproduccion",
        "region_scope": "iberoamerica_latam",
        "country_or_program": "Ibermedia",
        "agency_name": "Programa Ibermedia",
        "official_url": "https://www.programaibermedia.com/convocatorias/",
        "description": "Linea iberoamericana orientada a coproduccion cinematografica entre paises miembros del programa.",
        "status": "open",
        "open_date": "2026-01-20T00:00:00+00:00",
        "close_date": "2026-04-30T23:59:59+00:00",
        "opportunity_type": "co-production",
        "phase": "production",
        "max_award_per_project": 150000.0,
        "total_budget_pool": 10000000.0,
        "currency": "USD",
        "verification_status": "official",
        "eligibility_json": {
            "eligible_applicants": ["Productoras de paises miembros de Ibermedia"],
            "minimum_partners": 2,
        },
        "requirements_json": {
            "documents": ["Contrato de coproduccion", "Plan financiero", "Version del guion"],
        },
        "collaboration_rules_json": {
            "co_production_required": True,
            "minimum_partners": 2,
            "territorial_diversity": "iberoamericana",
        },
        "point_system_json": {
            "criteria": ["Viabilidad", "Coproduccion regional", "Potencial de circulacion"],
        },
        "eligible_formats_json": ["largometraje ficcion", "largometraje documental", "animacion"],
        "notes_json": {
            "currency_notice": "El programa puede operar en USD segun convocatoria anual.",
        },
        "requirement_items": [
            {"category": "coproduction", "requirement_text": "Participacion de al menos dos empresas de paises Ibermedia", "is_mandatory": True},
            {"category": "documents", "requirement_text": "Contrato o acuerdo de coproduccion firmado", "is_mandatory": True},
        ],
    },
]


class FundingIngestionService:
    region_scope_values = set(REGION_SCOPE_VALUES)
    opportunity_type_values = set(OPPORTUNITY_TYPE_VALUES)
    phase_values = set(PHASE_VALUES)
    status_values = set(STATUS_VALUES)

    def _json_dumps(self, value: Any) -> str | None:
        if value is None:
            return None
        return json.dumps(value, ensure_ascii=True)

    def _json_loads(self, value: str | None) -> Any:
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    def _normalize_region_scope(self, value: str | None) -> str:
        normalized = (value or "spain").strip().lower()
        if normalized in {"iberoamerica", "latam", "latin_america"}:
            normalized = "iberoamerica_latam"
        return normalized if normalized in self.region_scope_values else "spain"

    def _normalize_opportunity_type(self, value: str | None) -> str:
        normalized = (value or "development").strip().lower()
        if normalized == "distribution":
            normalized = "distribution_circulation"
        return normalized if normalized in self.opportunity_type_values else "development"

    def _normalize_phase(self, value: str | None) -> str:
        normalized = (value or "development").strip().lower()
        return normalized if normalized in self.phase_values else "development"

    def _normalize_status(self, value: str | None) -> str:
        normalized = (value or "open").strip().lower()
        return normalized if normalized in self.status_values else "open"

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return value
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _apply_legacy_fields(self, call: FundingCall) -> None:
        call.region = call.region_scope
        call.territory = call.country_or_program
        call.deadline = call.close_date
        call.amount_min = call.max_award_per_project
        call.amount_max = call.max_award_per_project
        if call.max_award_per_project is None:
            call.amount_range = None
        else:
            call.amount_range = f"{call.currency} {call.max_award_per_project:,.0f}"
        eligibility_payload = self._json_loads(call.eligibility_json)
        if isinstance(eligibility_payload, dict):
            parts = []
            for key, value in eligibility_payload.items():
                if isinstance(value, list):
                    rendered = ", ".join(str(item) for item in value)
                else:
                    rendered = str(value)
                parts.append(f"{key}: {rendered}")
            call.eligibility_summary = "; ".join(parts)[:2000] if parts else None
        else:
            call.eligibility_summary = None
        call.ingested_at = datetime.utcnow()

    async def _upsert_source(self, db: AsyncSession, payload: dict[str, Any]) -> FundingSource:
        result = await db.execute(select(FundingSource).where(FundingSource.code == payload["code"]))
        source = result.scalar_one_or_none()
        now = datetime.utcnow()

        if source is None:
            source = FundingSource(id=str(uuid.uuid4()))
            db.add(source)

        source.code = payload["code"]
        source.name = payload["name"]
        source.organization_id = payload.get("organization_id", "00000000-0000-0000-0000-000000000000")  # Default organization for institutional sources
        source.agency_name = payload.get("agency_name")
        source.official_url = payload.get("official_url")
        source.description = payload.get("description")
        source.region_scope = self._normalize_region_scope(payload.get("region_scope"))
        source.country_or_program = payload.get("country_or_program")
        source.region = source.region_scope
        source.territory = payload.get("country_or_program") or payload.get("name")
        source.source_type = "institutional"
        source.verification_status = payload.get("verification_status", "official")
        source.is_active = bool(payload.get("is_active", True))
        source.last_synced_at = now
        source.updated_at = now

        return source

    async def _replace_requirements(
        self,
        db: AsyncSession,
        call_id: str,
        requirement_items: Iterable[dict[str, Any]],
    ) -> None:
        await db.execute(delete(FundingRequirement).where(FundingRequirement.call_id == call_id))
        for index, item in enumerate(requirement_items):
            db.add(
                FundingRequirement(
                    id=str(uuid.uuid4()),
                    call_id=call_id,
                    category=str(item.get("category") or "general"),
                    requirement_text=str(item.get("requirement_text") or "").strip(),
                    is_mandatory=bool(item.get("is_mandatory", True)),
                    display_order=int(item.get("display_order", index)),
                    notes_json=self._json_dumps(item.get("notes_json")),
                )
            )

    async def _upsert_call(
        self,
        db: AsyncSession,
        payload: dict[str, Any],
        *,
        replace_requirements: bool = True,
    ) -> FundingCall:
        source_result = await db.execute(
            select(FundingSource).where(FundingSource.code == payload["source_code"])
        )
        source = source_result.scalar_one()

        result = await db.execute(
            select(FundingCall).where(
                FundingCall.source_id == source.id,
                FundingCall.title == payload["title"],
            )
        )
        call = result.scalar_one_or_none()
        if call is None:
            call = FundingCall(id=str(uuid.uuid4()), source_id=source.id, title=payload["title"])
            db.add(call)

        call.source_id = source.id
        call.title = payload["title"]
        call.region_scope = self._normalize_region_scope(payload.get("region_scope"))
        call.country_or_program = payload.get("country_or_program") or source.country_or_program or source.name
        call.agency_name = payload.get("agency_name") or source.agency_name or source.name
        call.official_url = payload.get("official_url")
        call.description = payload.get("description")
        call.open_date = self._parse_datetime(payload.get("open_date"))
        call.close_date = self._parse_datetime(payload.get("close_date"))
        call.opportunity_type = self._normalize_opportunity_type(payload.get("opportunity_type"))
        call.phase = self._normalize_phase(payload.get("phase"))
        call.collaboration_mode = (
            "cooperative" if call.opportunity_type in {"co-development", "co-production"} else "single"
        )
        call.max_award_per_project = payload.get("max_award_per_project")
        call.total_budget_pool = payload.get("total_budget_pool")
        call.currency = (payload.get("currency") or "EUR").upper()
        call.status = self._normalize_status(payload.get("status"))
        call.verification_status = payload.get("verification_status") or "official"
        call.eligibility_json = self._json_dumps(payload.get("eligibility_json"))
        call.requirements_json = self._json_dumps(payload.get("requirements_json"))
        call.collaboration_rules_json = self._json_dumps(payload.get("collaboration_rules_json"))
        call.point_system_json = self._json_dumps(payload.get("point_system_json"))
        call.eligible_formats_json = self._json_dumps(payload.get("eligible_formats_json"))
        call.notes_json = self._json_dumps(payload.get("notes_json"))
        self._apply_legacy_fields(call)

        if replace_requirements:
            await self._replace_requirements(db, call.id, payload.get("requirement_items", []))

        # After successfully upserting a funding call, enqueue matcher jobs for affected projects
        await self._enqueue_matcher_jobs_for_call_update(
            db, 
            organization_id=str(source.organization_id),
            call_id=str(call.id)
        )

        return call

    async def sync_sources(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:
        return await self.seed_catalog(db, force=force)

    async def seed_catalog(self, db: AsyncSession, force: bool = False) -> dict[str, Any]:
        sources_before = len((await db.execute(select(FundingSource.id))).all())
        calls_before = len((await db.execute(select(FundingCall.id))).all())

        for source_payload in SOURCE_SEED_DATA:
            await self._upsert_source(db, source_payload)
        await db.flush()

        for call_payload in CALL_SEED_DATA:
            if force:
                existing = await db.execute(
                    select(FundingCall).join(FundingSource, FundingSource.id == FundingCall.source_id).where(
                        FundingSource.code == call_payload["source_code"],
                        FundingCall.title == call_payload["title"],
                    )
                )
                call = existing.scalar_one_or_none()
                if call is not None:
                    await db.execute(delete(FundingRequirement).where(FundingRequirement.call_id == call.id))
                    await db.delete(call)
                    await db.flush()
            await self._upsert_call(db, call_payload)

        await db.commit()

        sources_after = len((await db.execute(select(FundingSource.id))).all())
        calls_after = len((await db.execute(select(FundingCall.id))).all())

        return {
            "sources_total": sources_after,
            "calls_total": calls_after,
            "sources_created": max(0, sources_after - sources_before),
            "calls_created": max(0, calls_after - calls_before),
            "seeded_source_codes": [item["code"] for item in SOURCE_SEED_DATA],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def list_sources(self, db: AsyncSession) -> list[dict[str, Any]]:
        result = await db.execute(select(FundingSource).order_by(FundingSource.region_scope.asc(), FundingSource.name.asc()))
        return [self.serialize_source(item) for item in result.scalars().all()]

    async def create_source(self, db: AsyncSession, payload: dict[str, Any]) -> dict[str, Any]:
        source = await self._upsert_source(db, payload)
        await db.commit()
        await db.refresh(source)
        return self.serialize_source(source)

    async def list_calls(
        self,
        db: AsyncSession,
        *,
        region_scope: str | None = None,
        phase: str | None = None,
        opportunity_type: str | None = None,
        status: str | None = None,
        source_code: str | None = None,
    ) -> list[dict[str, Any]]:
        query = select(FundingCall, FundingSource).join(FundingSource, FundingSource.id == FundingCall.source_id)
        if region_scope:
            query = query.where(FundingCall.region_scope == self._normalize_region_scope(region_scope))
        if phase:
            query = query.where(FundingCall.phase == self._normalize_phase(phase))
        if opportunity_type:
            query = query.where(FundingCall.opportunity_type == self._normalize_opportunity_type(opportunity_type))
        if status:
            query = query.where(FundingCall.status == self._normalize_status(status))
        if source_code:
            query = query.where(FundingSource.code == source_code)
        result = await db.execute(query.order_by(FundingCall.close_date.asc(), FundingCall.title.asc()))
        return [self.serialize_call(call, source=source) for call, source in result.all()]

    async def list_opportunities(
        self,
        db: AsyncSession,
        region: str | None = None,
        phase: str | None = None,
        opportunity_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return await self.list_calls(
            db,
            region_scope=region,
            phase=phase,
            opportunity_type=opportunity_type,
            status=status,
        )

    async def get_call(self, db: AsyncSession, call_id: str) -> dict[str, Any] | None:
        result = await db.execute(
            select(FundingCall, FundingSource).join(FundingSource, FundingSource.id == FundingCall.source_id).where(FundingCall.id == call_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        call, source = row
        requirement_result = await db.execute(
            select(FundingRequirement)
            .where(FundingRequirement.call_id == call.id)
            .order_by(FundingRequirement.display_order.asc(), FundingRequirement.created_at.asc())
        )
        requirements = requirement_result.scalars().all()
        return self.serialize_call(call, source=source, requirements=requirements, include_soft_schema=True)

    async def create_call(self, db: AsyncSession, payload: dict[str, Any]) -> dict[str, Any]:
        source_result = await db.execute(select(FundingSource).where(FundingSource.id == payload["source_id"]))
        source = source_result.scalar_one_or_none()
        if source is None:
            raise ValueError("Funding source not found")
        enriched_payload = {**payload, "source_code": source.code}
        call = await self._upsert_call(db, enriched_payload)
        await db.commit()
        return await self.get_call(db, call.id)

    async def update_call(self, db: AsyncSession, call_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        result = await db.execute(select(FundingCall, FundingSource).join(FundingSource, FundingSource.id == FundingCall.source_id).where(FundingCall.id == call_id))
        row = result.one_or_none()
        if row is None:
            return None
        call, source = row

        merged = {
            "source_code": source.code,
            "title": payload.get("title", call.title),
            "region_scope": payload.get("region_scope", call.region_scope),
            "country_or_program": payload.get("country_or_program", call.country_or_program),
            "agency_name": payload.get("agency_name", call.agency_name),
            "official_url": payload.get("official_url", call.official_url),
            "description": payload.get("description", call.description),
            "status": payload.get("status", call.status),
            "open_date": payload.get("open_date", call.open_date),
            "close_date": payload.get("close_date", call.close_date),
            "opportunity_type": payload.get("opportunity_type", call.opportunity_type),
            "phase": payload.get("phase", call.phase),
            "max_award_per_project": payload.get("max_award_per_project", call.max_award_per_project),
            "total_budget_pool": payload.get("total_budget_pool", call.total_budget_pool),
            "currency": payload.get("currency", call.currency),
            "verification_status": payload.get("verification_status", call.verification_status),
            "eligibility_json": payload.get("eligibility_json", self._json_loads(call.eligibility_json)),
            "requirements_json": payload.get("requirements_json", self._json_loads(call.requirements_json)),
            "collaboration_rules_json": payload.get("collaboration_rules_json", self._json_loads(call.collaboration_rules_json)),
            "point_system_json": payload.get("point_system_json", self._json_loads(call.point_system_json)),
            "eligible_formats_json": payload.get("eligible_formats_json", self._json_loads(call.eligible_formats_json)),
            "notes_json": payload.get("notes_json", self._json_loads(call.notes_json)),
            "requirement_items": payload.get("requirement_items", []),
        }
        await self._upsert_call(db, merged, replace_requirements="requirement_items" in payload)
        await db.commit()
        return await self.get_call(db, call_id)

    def serialize_source(self, source: FundingSource) -> dict[str, Any]:
        return {
            "id": source.id,
            "code": source.code,
            "name": source.name,
            "agency_name": source.agency_name,
            "official_url": source.official_url,
            "description": source.description,
            "region_scope": source.region_scope,
            "country_or_program": source.country_or_program,
            "verification_status": source.verification_status,
            "is_active": source.is_active,
            "last_synced_at": source.last_synced_at.isoformat() if source.last_synced_at else None,
            "created_at": source.created_at.isoformat() if source.created_at else None,
            "updated_at": source.updated_at.isoformat() if source.updated_at else None,
        }

    def serialize_call(
        self,
        call: FundingCall,
        *,
        source: FundingSource | None = None,
        requirements: list[FundingRequirement] | None = None,
        include_soft_schema: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "id": call.id,
            "source_id": call.source_id,
            "source_code": source.code if source else None,
            "source_name": source.name if source else None,
            "title": call.title,
            "region_scope": call.region_scope,
            "country_or_program": call.country_or_program,
            "agency_name": call.agency_name,
            "official_url": call.official_url,
            "status": call.status,
            "open_date": call.open_date.isoformat() if call.open_date else None,
            "close_date": call.close_date.isoformat() if call.close_date else None,
            "opportunity_type": call.opportunity_type,
            "phase": call.phase,
            "max_award_per_project": call.max_award_per_project,
            "total_budget_pool": call.total_budget_pool,
            "currency": call.currency,
            "verification_status": call.verification_status,
            "description": call.description,
            "created_at": call.created_at.isoformat() if call.created_at else None,
            "updated_at": call.updated_at.isoformat() if call.updated_at else None,
        }
        if include_soft_schema:
            payload.update(
                {
                    "eligibility_json": self._json_loads(call.eligibility_json),
                    "requirements_json": self._json_loads(call.requirements_json),
                    "collaboration_rules_json": self._json_loads(call.collaboration_rules_json),
                    "point_system_json": self._json_loads(call.point_system_json),
                    "eligible_formats_json": self._json_loads(call.eligible_formats_json),
                    "notes_json": self._json_loads(call.notes_json),
                    "requirements": [
                        {
                            "id": item.id,
                            "category": item.category,
                            "requirement_text": item.requirement_text,
                            "is_mandatory": item.is_mandatory,
                            "display_order": item.display_order,
                            "notes_json": self._json_loads(item.notes_json),
                        }
                        for item in (requirements or [])
                    ],
                }
            )
        return payload

    async def _enqueue_matcher_jobs_for_call_update(
        self,
        db: AsyncSession,
        *,
        organization_id: str,
        call_id: str
    ) -> None:
        """Enqueue matcher jobs for projects in the organization when a funding call is updated.
        
        This method finds all projects in the organization that have at least one 
        COMPLETED PROJECT-scoped document and enqueues matcher jobs for them.
        """
        from sqlalchemy import select, and_
        
        # Get all projects in the organization that have at least one completed PROJECT-scoped document
        from models.document import ProjectDocument, ProjectDocumentUploadStatus, ProjectDocumentVisibilityScope
        from models.core import Project
        
        # Subquery to find projects with completed documents
        docs_subquery = select(ProjectDocument.project_id).where(
            and_(
                ProjectDocument.organization_id == organization_id,
                ProjectDocument.visibility_scope == ProjectDocumentVisibilityScope.PROJECT,
                ProjectDocument.upload_status == ProjectDocumentUploadStatus.COMPLETED
            )
        ).distinct()
        
        # Get projects that have completed documents
        projects_result = await db.execute(
            select(Project.id, Project.organization_id)
            .where(
                and_(
                    Project.organization_id == organization_id,
                    Project.id.in_(docs_subquery)
                )
            )
        )
        projects = [(str(row.id), str(row.organization_id)) for row in projects_result.fetchall()]
        
        if not projects:
            # No projects with documents, nothing to do
            return
            
        # For each project, compute input hash and enqueue matcher job if needed
        for project_id, org_id in projects:
            await self._enqueue_matcher_job_for_project_and_call(
                db,
                project_id=project_id,
                organization_id=org_id,
                call_id=call_id
            )

    async def _enqueue_matcher_job_for_project_and_call(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        call_id: str
    ) -> None:
        """Enqueue a matcher job for a specific project and funding call update.
        
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
            trigger_type="funding_call_updated",
            trigger_ref_id=call_id,
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


funding_ingestion_service = FundingIngestionService()
