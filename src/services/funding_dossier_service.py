from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.production import ProductionBreakdown
from schemas.auth_schema import TenantContext
from services.budget_estimator_service import budget_estimator_service
from services.funding_matcher_service import funding_matcher_service
from services.project_funding_service import project_funding_service


class DossierRenderError(RuntimeError):
    pass


class FundingDossierService:
    DOSSIER_VERSION = "es-eu-latam-dossier-v1"

    def __init__(self) -> None:
        templates_root = Path(__file__).resolve().parents[2] / "templates"
        self.templates_root = templates_root
        self.environment = Environment(
            loader=FileSystemLoader(str(templates_root)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def _normalize_departments_summary(self, breakdown_data: dict[str, Any]) -> list[dict[str, Any]]:
        departments = breakdown_data.get("department_breakdown", {}) or {}
        if not isinstance(departments, dict):
            return []
        summary: list[dict[str, Any]] = []
        for name, payload in departments.items():
            count = 0
            if isinstance(payload, dict):
                raw_count = payload.get("count") or payload.get("total") or payload.get("items") or 0
                if isinstance(raw_count, (int, float)):
                    count = int(raw_count)
            summary.append({"department": str(name), "count": count})
        summary.sort(key=lambda item: (-item["count"], item["department"]))
        return summary

    def _build_complexity_flags(
        self,
        breakdown_data: dict[str, Any],
        departments_summary: list[dict[str, Any]],
    ) -> list[str]:
        metadata = breakdown_data.get("metadata", {}) or {}
        flags = list(breakdown_data.get("complexity_flags", []) or [])
        scenes = int(metadata.get("total_scenes") or 0)
        locations = int(metadata.get("total_locations") or 0)
        characters = int(metadata.get("total_characters") or 0)
        if scenes >= 35 and "scene_volume_high" not in flags:
            flags.append("scene_volume_high")
        if locations >= 10 and "location_load_high" not in flags:
            flags.append("location_load_high")
        if characters >= 12 and "cast_complexity_high" not in flags:
            flags.append("cast_complexity_high")
        if any(item["department"] == "travel" and item["count"] > 0 for item in departments_summary):
            flags.append("travel_coordination")
        return list(dict.fromkeys(flags))

    def _build_funding_strategy(
        self,
        profile: dict[str, Any],
        private_summary: dict[str, Any],
        top_matches: list[dict[str, Any]],
    ) -> list[str]:
        actions: list[str] = []
        gap = float(private_summary.get("current_funding_gap") or 0.0)
        optimistic_gap = float(private_summary.get("optimistic_funding_gap") or 0.0)
        if gap > 0:
            actions.append(f"Cover the current funding gap of EUR {gap:,.0f} with institutional calls plus private financing.")
        if optimistic_gap > 0:
            actions.append(
                f"Even with projected private funding, EUR {optimistic_gap:,.0f} remains uncovered and needs active packaging."
            )
        if any(match.get("source_region") == "spain" for match in top_matches):
            actions.append("Use Spain-focused calls as the first institutional layer for core development or production support.")
        if any(match.get("source_region") == "europe" for match in top_matches):
            actions.append("Position the project with a clear European cooperation angle and lead applicant structure.")
        if any(match.get("source_region") == "iberoamerica_latam" for match in top_matches):
            actions.append("Activate Ibero-American coproduction or circulation partners to unlock regional eligibility.")
        if not top_matches:
            actions.append("Refresh the matcher after improving project data, budget, and territorial packaging.")
        return actions[:4]

    async def build_dossier(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        tenant: TenantContext | None = None,
    ) -> dict[str, Any]:
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one_or_none()
        if project is None or str(project.organization_id) != str(organization_id):
            return {"error": "Project not found"}

        profile_tenant = tenant or TenantContext(
            user_id="system",
            organization_id=organization_id,
            role="admin",
            is_admin=False,
            is_global_admin=False,
            auth_method="internal",
        )
        profile = await funding_matcher_service.build_project_profile(db, project_id, profile_tenant)
        if profile is None:
            return {"error": "Funding profile not available"}

        matches = await funding_matcher_service.get_matches(db, project_id, organization_id)
        if not matches:
            recomputed = await funding_matcher_service.compute_matches(db, project_id, organization_id)
            matches = recomputed["matches"]
        checklist = await funding_matcher_service.get_checklist(db, project_id, organization_id)

        breakdown_result = await db.execute(
            select(ProductionBreakdown).where(ProductionBreakdown.project_id == project_id)
        )
        breakdown = breakdown_result.scalar_one_or_none()
        breakdown_data = {}
        if breakdown and breakdown.breakdown_json:
            breakdown_data = funding_matcher_service._json_loads(breakdown.breakdown_json) or {}
            if not isinstance(breakdown_data, dict):
                breakdown_data = {}

        budget_summary_raw = await budget_estimator_service.get_budget(db, project_id)
        if "error" in budget_summary_raw:
            budget_summary_raw = {
                "scenario_type": None,
                "grand_total": 0.0,
                "section_totals": {},
            }
        private_summary = await project_funding_service.get_summary(db, project_id, organization_id)

        departments_summary = self._normalize_departments_summary(breakdown_data)
        complexity_flags = self._build_complexity_flags(breakdown_data, departments_summary)

        match_counts = {
            "high_count": len([item for item in matches if item.get("fit_level") == "high"]),
            "medium_count": len([item for item in matches if item.get("fit_level") == "medium"]),
            "low_count": len([item for item in matches if item.get("fit_level") == "low"]),
            "blocked_count": len([item for item in matches if item.get("fit_level") == "blocked"]),
        }

        top_matches = [
            {
                "title": item["title"],
                "source_name": item["source_name"],
                "region_scope": item["source_region"],
                "opportunity_type": item["opportunity_type"],
                "deadline_at": item["deadline_at"],
                "match_score": item["match_score"],
                "fit_level": item["fit_level"],
                "fit_summary": item["fit_summary"],
                "blocking_reasons": item.get("blocking_reasons_json", []),
                "recommended_actions": item.get("recommended_actions_json", []),
                "official_url": item["official_url"],
            }
            for item in matches
            if item.get("fit_level") in {"high", "medium"}
        ][:6]

        low_or_blocked_by_region = {
            "spain": [item for item in matches if item.get("source_region") == "spain" and item.get("fit_level") in {"low", "blocked"}][:3],
            "europe": [item for item in matches if item.get("source_region") == "europe" and item.get("fit_level") in {"low", "blocked"}][:3],
            "iberoamerica_latam": [item for item in matches if item.get("source_region") == "iberoamerica_latam" and item.get("fit_level") in {"low", "blocked"}][:3],
        }

        render_regions = {
            "spain": [item for item in top_matches if item.get("region_scope") == "spain"],
            "europe": [item for item in top_matches if item.get("region_scope") == "europe"],
            "iberoamerica_latam": [item for item in top_matches if item.get("region_scope") == "iberoamerica_latam"],
        }

        generated_at = datetime.now(timezone.utc).isoformat()
        dossier = {
            "project_profile": {
                "project_id": profile["project_id"],
                "organization_id": profile["organization_id"],
                "title": profile["title"],
                "type_of_work": profile["type_of_work"],
                "phase": profile["phase"],
                "logline": profile.get("logline") or "",
                "synopsis": profile.get("synopsis") or "",
                "language": profile.get("language") or "es",
                "countries_involved": profile.get("countries_involved", []),
                "evaluation_version": profile.get("evaluation_version") or funding_matcher_service.EVALUATION_VERSION,
            },
            "production_breakdown_summary": {
                "scenes_count": profile.get("breakdown_summary", {}).get("total_scenes", 0),
                "departments_summary": departments_summary,
                "complexity_flags": complexity_flags,
            },
            "budget_summary": {
                "total_budget": float(budget_summary_raw.get("grand_total") or 0.0),
                "scenario": budget_summary_raw.get("scenario_type"),
                "section_totals": budget_summary_raw.get("section_totals", {}),
                "contingency": float((budget_summary_raw.get("section_totals", {}) or {}).get("contingency", 0.0)),
            },
            "private_funding_summary": {
                "secured": float(private_summary.get("total_secured_private_funds") or 0.0),
                "negotiating": float(private_summary.get("total_negotiating_private_funds") or 0.0),
                "projected": float(private_summary.get("total_projected_private_funds") or 0.0),
                "current_funding_gap": float(private_summary.get("current_funding_gap") or 0.0),
                "optimistic_funding_gap": float(private_summary.get("optimistic_funding_gap") or 0.0),
            },
            "funding_match_summary": {
                "matches_count": len(matches),
                **match_counts,
            },
            "top_matches": top_matches,
            "checklist": {
                "missing_documents": checklist.get("documents", []),
                "priority_actions": checklist.get("priority_actions", []),
                "deadline_risks": checklist.get("deadline_risks", []),
            },
            "funding_strategy": self._build_funding_strategy(profile, private_summary, top_matches),
            "generated_at": generated_at,
            "dossier_version": self.DOSSIER_VERSION,
            "render_context": {
                "recommended_by_region": render_regions,
                "low_or_blocked_by_region": low_or_blocked_by_region,
            },
        }
        return dossier

    def render_dossier_html(self, payload: dict[str, Any]) -> str:
        template = self.environment.get_template("funding/dossier.html")
        return template.render(payload=payload)

    def export_dossier_pdf(self, payload: dict[str, Any]) -> bytes:
        html = self.render_dossier_html(payload)
        try:
            return HTML(string=html, base_url=str(self.templates_root.parent)).write_pdf()
        except Exception as exc:
            raise DossierRenderError(
                f"WeasyPrint failed to render the funding dossier PDF: {exc}"
            ) from exc


funding_dossier_service = FundingDossierService()
