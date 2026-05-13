from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import Project
from models.document import ProjectDocument
from models.production import (
    FundingCall,
    FundingRequirement,
    FundingSource,
    ProductionBreakdown,
    ProjectBudget,
    ProjectFundingMatch,
    ProjectFundingSource,
)
from schemas.auth_schema import TenantContext
from services.project_document_rag_service import project_document_rag_service


class FundingMatcherService:
    EVALUATION_VERSION = "es-eu-latam-mvp-v1"
    RAG_EVALUATION_VERSION = "rag-v2"
    CLASSIC_MODE = "classic"
    RAG_MODE = "rag_enriched"
    SPAIN_COUNTRIES = {"espana", "españa", "spain"}
    EUROPE_COUNTRIES = {
        "espana",
        "españa",
        "spain",
        "france",
        "francia",
        "italy",
        "italia",
        "germany",
        "alemania",
        "portugal",
        "belgium",
        "belgica",
        "netherlands",
        "paises bajos",
        "ireland",
        "irlanda",
        "poland",
        "polonia",
        "sweden",
        "suecia",
        "denmark",
        "dinamarca",
        "finland",
        "finlandia",
        "europe",
        "europa",
    }
    LATAM_COUNTRIES = {
        "argentina",
        "bolivia",
        "brasil",
        "brazil",
        "chile",
        "colombia",
        "costa rica",
        "cuba",
        "dominican republic",
        "ecuador",
        "el salvador",
        "guatemala",
        "honduras",
        "iberoamerica",
        "iberoamerica_latam",
        "latam",
        "latin america",
        "latin-america",
        "mexico",
        "méxico",
        "nicaragua",
        "panama",
        "panamá",
        "paraguay",
        "peru",
        "peru",
        "perú",
        "puerto rico",
        "rep dominicana",
        "republica dominicana",
        "república dominicana",
        "uruguay",
        "venezuela",
    }
    DOCUMENT_HINTS = (
        ("presupuesto", "Budget breakdown"),
        ("budget", "Budget breakdown"),
        ("guion", "Script or treatment"),
        ("screenplay", "Script or treatment"),
        ("tratamiento", "Script or treatment"),
        ("plan de financiacion", "Financing plan"),
        ("plan financiero", "Financing plan"),
        ("financing plan", "Financing plan"),
        ("rights", "Chain of title"),
        ("derechos", "Chain of title"),
        ("coprodu", "Coproduction agreement or LOI"),
        ("carta", "Letter of intent"),
        ("letter", "Letter of intent"),
        ("audien", "Audience strategy"),
        ("distrib", "Distribution strategy"),
    )

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

    def _normalize_text(self, value: Any) -> str:
        return str(value or "").strip().lower()

    def _tokenize_text(self, value: Any) -> list[str]:
        return re.findall(r"[a-zA-Z0-9_\-]{3,}", self._normalize_text(value))

    def _phase_rank(self, phase: str | None) -> int:
        mapping = {
            "writing": 0,
            "development": 1,
            "production": 2,
            "postproduction": 3,
            "distribution": 4,
        }
        return mapping.get(self._normalize_text(phase), 1)

    def _infer_type_of_work(self, project: Project, text_blob: str) -> str:
        text = self._normalize_text(f"{project.name} {project.description or ''} {text_blob}")
        if any(token in text for token in ("documentary", "documental")):
            return "documentary"
        if any(token in text for token in ("animation", "animacion", "animación")):
            return "animation"
        if any(token in text for token in ("short", "cortometraje", "corto")):
            return "short"
        if any(token in text for token in ("series", "serie", "episod")):
            return "series"
        if "experimental" in text:
            return "experimental"
        return "feature"

    def _infer_phase(
        self,
        project: Project,
        breakdown_data: dict[str, Any],
        budget_total: float,
        private_summary: dict[str, Any],
    ) -> str:
        status_text = self._normalize_text(project.status)
        combined = self._normalize_text(
            f"{status_text} {project.description or ''} {project.script_text or ''}"
        )
        if "distribution" in combined or "sales" in combined:
            return "distribution"
        if any(token in combined for token in ("post", "postproduction", "rough cut", "picture lock")):
            return "postproduction"
        if any(token in combined for token in ("shoot", "rodaje", "filming", "production")):
            return "production"
        if budget_total > 0 and private_summary.get("total_secured_private_funds", 0) > 0:
            return "production"
        if breakdown_data:
            return "development"
        return "writing"

    def _extract_countries(self, text_blob: str) -> list[str]:
        normalized_text = self._normalize_text(text_blob)
        detected = []
        labels = {
            "Espana": self.SPAIN_COUNTRIES,
            "France": {"france", "francia"},
            "Portugal": {"portugal"},
            "Italy": {"italy", "italia"},
            "Germany": {"germany", "alemania"},
            "Mexico": {"mexico", "méxico"},
            "Argentina": {"argentina"},
            "Colombia": {"colombia"},
            "Chile": {"chile"},
            "Brazil": {"brazil", "brasil"},
            "Uruguay": {"uruguay"},
            "Peru": {"peru", "perú"},
        }
        for label, aliases in labels.items():
            if any(alias in normalized_text for alias in aliases):
                detected.append(label)
        return detected or ["Espana"]

    def _collect_keywords(self, project: Project, breakdown_data: dict[str, Any]) -> list[str]:
        raw_parts: list[str] = [project.name, project.description or "", project.script_text or ""]
        metadata = breakdown_data.get("metadata", {}) if breakdown_data else {}
        department_breakdown = breakdown_data.get("department_breakdown", {}) if breakdown_data else {}
        raw_parts.extend(str(item) for item in metadata.values())
        raw_parts.extend(str(key) for key in department_breakdown.keys())
        tokens: list[str] = []
        for part in raw_parts:
            for token in self._normalize_text(part).replace("/", " ").replace(",", " ").split():
                if len(token) >= 4 and token not in tokens:
                    tokens.append(token)
        return tokens[:20]

    def _funding_gap_band(self, funding_gap: float) -> str:
        if funding_gap <= 0:
            return "covered"
        if funding_gap < 50000:
            return "small_gap"
        if funding_gap < 250000:
            return "medium_gap"
        return "large_gap"

    async def build_project_profile(
        self,
        db: AsyncSession,
        project_id: str,
        tenant: TenantContext,
    ) -> dict[str, Any] | None:
        project_result = await db.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one_or_none()
        
        if project is None:
            return None
            
        # Hardened multi-tenant check
        if not tenant.is_global_admin and str(project.organization_id) != str(tenant.organization_id):
            return None

        breakdown_result = await db.execute(
            select(ProductionBreakdown).where(ProductionBreakdown.project_id == project_id)
        )
        breakdown = breakdown_result.scalar_one_or_none()
        breakdown_data = self._json_loads(breakdown.breakdown_json) if breakdown and breakdown.breakdown_json else {}
        if not isinstance(breakdown_data, dict):
            breakdown_data = {}

        budget_result = await db.execute(
            select(ProjectBudget).where(ProjectBudget.project_id == project_id)
        )
        budget = budget_result.scalar_one_or_none()
        budget_total = float(budget.grand_total if budget else 0.0)

        private_sources_result = await db.execute(
            select(ProjectFundingSource).where(
                ProjectFundingSource.project_id == project_id,
                ProjectFundingSource.organization_id == project.organization_id,
            )
        )
        private_sources = list(private_sources_result.scalars().all())

        total_secured = sum(source.amount for source in private_sources if source.status == "secured")
        total_negotiating = sum(source.amount for source in private_sources if source.status == "negotiating")
        total_projected = sum(source.amount for source in private_sources if source.status == "projected")
        current_gap = max(0.0, budget_total - total_secured)
        optimistic_gap = max(0.0, budget_total - (total_secured + total_negotiating + total_projected))
        private_summary = {
            "total_sources": len(private_sources),
            "total_secured_private_funds": total_secured,
            "total_negotiating_private_funds": total_negotiating,
            "total_projected_private_funds": total_projected,
            "current_funding_gap": current_gap,
            "optimistic_funding_gap": optimistic_gap,
        }

        text_blob = " ".join(
            [
                project.description or "",
                project.script_text or "",
                json.dumps(breakdown_data, ensure_ascii=False),
            ]
        )
        countries = self._extract_countries(text_blob)
        collaboration_interest = "yes" if len(countries) > 1 or "coprodu" in self._normalize_text(text_blob) else "no"
        if collaboration_interest == "no" and any(country in {"France", "Portugal", "Italy", "Germany", "Mexico", "Argentina", "Colombia", "Chile", "Brazil", "Uruguay", "Peru"} for country in countries):
            collaboration_interest = "maybe"

        synopsis = (project.script_text or "")[:400]
        profile = {
            "project_id": str(project.id),
            "organization_id": str(project.organization_id),
            "title": project.name,
            "type_of_work": self._infer_type_of_work(project, text_blob),
            "phase": self._infer_phase(project, breakdown_data, budget_total, private_summary),
            "logline": project.description or "",
            "synopsis": synopsis,
            "language": "es",
            "countries_involved": countries,
            "breakdown_summary": {
                "total_scenes": breakdown_data.get("metadata", {}).get("total_scenes", 0),
                "total_characters": breakdown_data.get("metadata", {}).get("total_characters", 0),
                "total_locations": breakdown_data.get("metadata", {}).get("total_locations", 0),
                "department_breakdown": breakdown_data.get("department_breakdown", {}),
            },
            "budget_total": budget_total,
            "funding_gap": current_gap,
            "funding_gap_band": self._funding_gap_band(current_gap),
            "private_funding_status": private_summary,
            "keywords": self._collect_keywords(project, breakdown_data),
            "coproduction_interest": collaboration_interest,
            "has_breakdown": bool(breakdown_data),
            "has_budget": budget_total > 0,
            "has_synopsis": bool(project.script_text or project.description),
        }
        return profile

    def _phase_compatibility(self, project_phase: str, call_phase: str | None) -> tuple[int, list[str], list[str]]:
        actions: list[str] = []
        blockers: list[str] = []
        if not call_phase:
            return 8, blockers, actions
        call_rank = self._phase_rank(call_phase)
        project_rank = self._phase_rank(project_phase)
        if project_rank == call_rank:
            return 18, blockers, actions
        if abs(project_rank - call_rank) == 1:
            actions.append(f"Align phase package toward {call_phase}")
            return 10, blockers, actions
        blockers.append(f"Phase mismatch: project in {project_phase}, call targets {call_phase}")
        return -18, blockers, actions

    def _work_type_compatibility(self, project_type: str, call: FundingCall) -> tuple[int, list[str]]:
        formats = self._json_loads(call.eligible_formats_json)
        if not isinstance(formats, list) or not formats:
            return 8, []
        normalized_formats = [self._normalize_text(item) for item in formats]
        aliases = {
            "feature": ["feature", "largometraje"],
            "short": ["short", "cortometraje"],
            "documentary": ["documentary", "documental"],
            "animation": ["animation", "animacion", "animación"],
            "series": ["series", "serie"],
            "experimental": ["experimental"],
        }
        if any(alias in fmt for fmt in normalized_formats for alias in aliases.get(project_type, [project_type])):
            return 14, []
        return -8, [f"Work type likely outside eligible formats for {call.title}"]

    def _territory_compatibility(
        self,
        countries: list[str],
        call: FundingCall,
    ) -> tuple[int, list[str], list[str]]:
        normalized_countries = {self._normalize_text(country) for country in countries}
        blockers: list[str] = []
        actions: list[str] = []
        if call.region_scope == "spain":
            if normalized_countries & self.SPAIN_COUNTRIES:
                return 18, blockers, actions
            blockers.append("Spanish territorial eligibility not evidenced")
            return -25, blockers, actions
        if call.region_scope == "europe":
            if normalized_countries & self.EUROPE_COUNTRIES:
                score = 14
                if len(normalized_countries & self.EUROPE_COUNTRIES) >= 2:
                    score += 4
                else:
                    actions.append("Add a second European coproduction territory if required")
                return score, blockers, actions
            blockers.append("European territorial eligibility not evidenced")
            return -18, blockers, actions
        if call.region_scope == "iberoamerica_latam":
            if normalized_countries & (self.SPAIN_COUNTRIES | self.LATAM_COUNTRIES):
                score = 12
                if len(normalized_countries & self.LATAM_COUNTRIES) >= 1:
                    score += 6
                else:
                    actions.append("Add an Ibero-American partner territory")
                return score, blockers, actions
            blockers.append("Ibero-American territorial eligibility not evidenced")
            return -18, blockers, actions
        return 8, blockers, actions

    def _collaboration_compatibility(
        self,
        profile: dict[str, Any],
        call: FundingCall,
    ) -> tuple[int, list[str], list[str]]:
        rules = self._json_loads(call.collaboration_rules_json)
        rules = rules if isinstance(rules, dict) else {}
        actions: list[str] = []
        blockers: list[str] = []
        coproduction_interest = self._normalize_text(profile.get("coproduction_interest"))
        countries = profile.get("countries_involved", [])
        country_count = len(countries)
        minimum_partners = int(rules.get("minimum_partners") or 1)
        requires_coproduction = bool(rules.get("co_production_required") or rules.get("co_production_allowed") or minimum_partners > 1)
        if not requires_coproduction:
            return 8, blockers, actions
        if country_count >= minimum_partners and coproduction_interest in {"yes", "maybe"}:
            return 14, blockers, actions
        if country_count < minimum_partners:
            blockers.append(f"Needs at least {minimum_partners} territories or partners")
        if coproduction_interest == "no":
            actions.append("Define coproduction strategy and target partners")
        return -14, blockers, actions

    def _budget_compatibility(self, profile: dict[str, Any], call: FundingCall) -> tuple[int, list[str], list[str]]:
        budget_total = float(profile.get("budget_total") or 0.0)
        funding_gap = float(profile.get("funding_gap") or 0.0)
        blockers: list[str] = []
        actions: list[str] = []
        score = 0
        max_award = float(call.max_award_per_project or 0.0)
        if budget_total <= 0:
            blockers.append("Budget not generated yet")
            actions.append("Generate a project budget before applying")
            return -10, blockers, actions
        if max_award > 0:
            coverage_ratio = funding_gap / max_award if max_award else 0.0
            if funding_gap <= 0:
                score += 6
            elif coverage_ratio <= 1.2:
                score += 12
            elif coverage_ratio <= 3.0:
                score += 8
                actions.append("Stack this call with complementary funding sources")
            else:
                score += 3
                actions.append("Large gap: combine with multiple funds or private capital")
        else:
            score += 6
        if call.total_budget_pool and budget_total > call.total_budget_pool * 5:
            blockers.append("Project budget is oversized relative to this line")
            score -= 10
        return score, blockers, actions

    def _applicant_hints(self, profile: dict[str, Any], call: FundingCall) -> tuple[int, list[str], list[str]]:
        eligibility = self._json_loads(call.eligibility_json)
        eligibility_text = self._normalize_text(json.dumps(eligibility, ensure_ascii=False))
        actions: list[str] = []
        blockers: list[str] = []
        score = 0
        if "independent" in eligibility_text and profile.get("type_of_work") in {"feature", "documentary", "animation", "short"}:
            score += 6
        if "track record" in eligibility_text or "experiencia" in eligibility_text:
            actions.append("Prepare producer track record references")
            score += 3
        if "single applicant" in eligibility_text and profile.get("coproduction_interest") == "yes":
            actions.append("Confirm lead applicant structure for single-applicant call")
        return score, blockers, actions

    def _deadline_signal(self, call: FundingCall) -> tuple[int, list[str], list[str], str]:
        blockers: list[str] = []
        actions: list[str] = []
        if call.status in {"closed", "archived"}:
            blockers.append("Call is no longer active")
            return -25, blockers, actions, "closed"
        if call.close_date is None:
            return 4, blockers, actions, "unknown"
        close_date = call.close_date
        if close_date.tzinfo is None:
            close_date = close_date.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days_left = (close_date - now).days
        if days_left < 0:
            actions.append("Validate the current edition date before applying")
            return -4, blockers, actions, "stale"
        if days_left <= 14:
            actions.append("Urgent deadline: finalize package immediately")
            return 2, blockers, actions, "urgent"
        if days_left <= 45:
            actions.append("Near deadline: lock budget and documents this sprint")
            return 6, blockers, actions, "near"
        actions.append(f"Prepare application before {close_date.date().isoformat()}")
        return 8, blockers, actions, "healthy"

    def _detect_missing_documents(
        self,
        profile: dict[str, Any],
        call: FundingCall,
        requirements: list[FundingRequirement],
    ) -> list[str]:
        missing: list[str] = []
        haystack_parts = [
            call.title,
            call.description,
            json.dumps(self._json_loads(call.requirements_json), ensure_ascii=False),
            json.dumps(self._json_loads(call.eligibility_json), ensure_ascii=False),
            " ".join(item.requirement_text for item in requirements),
        ]
        haystack = self._normalize_text(" ".join(part or "" for part in haystack_parts))
        has_budget = bool(profile.get("has_budget"))
        has_synopsis = bool(profile.get("has_synopsis"))
        has_breakdown = bool(profile.get("has_breakdown"))
        for needle, label in self.DOCUMENT_HINTS:
            if needle in haystack and label not in missing:
                if label == "Budget breakdown" and has_budget:
                    continue
                if label == "Script or treatment" and has_synopsis:
                    continue
                if label == "Distribution strategy" and profile.get("phase") not in {"distribution", "postproduction"}:
                    missing.append(label)
                    continue
                if label == "Audience strategy" and has_breakdown:
                    missing.append(label)
                    continue
                missing.append(label)
        return missing

    def _build_fit_summary(
        self,
        fit_level: str,
        call: FundingCall,
        blockers: list[str],
        actions: list[str],
    ) -> str:
        if fit_level == "high":
            return f"Strong fit for {call.title} with current project profile."
        if fit_level == "medium":
            return f"Viable fit for {call.title} if the main gaps are closed."
        if fit_level == "low":
            return f"Limited fit for {call.title}; targeted adjustments are needed."
        if blockers:
            return f"Blocked for {call.title}: {blockers[0]}."
        if actions:
            return f"Blocked for {call.title} until core requirements are aligned."
        return f"Blocked for {call.title}."

    def _fit_level_from_score(self, match_score: float, blockers: list[str]) -> str:
        if blockers and any(
            token in reason.lower()
            for reason in blockers
            for token in ("not evidenced", "mismatch", "no longer active", "budget not generated", "missing documented evidence")
        ):
            return "blocked" if match_score < 45 else "low"
        if match_score >= 75:
            return "high"
        if match_score >= 55:
            return "medium"
        if match_score >= 35:
            return "low"
        return "blocked"

    def _confidence_from_profile(self, profile: dict[str, Any], blockers: list[str], deadline_state: str) -> str:
        confidence_level = "high"
        if not profile.get("has_breakdown") or not profile.get("has_budget"):
            confidence_level = "medium"
        if len(blockers) >= 3 or deadline_state == "unknown":
            confidence_level = "low" if confidence_level == "medium" else confidence_level
        return confidence_level

    def _document_type_hint(self, requirement_text: str) -> str | None:
        normalized = self._normalize_text(requirement_text)
        hints = (
            (("budget", "presupuesto", "coste", "cost"), "budget", "Budget breakdown"),
            (("treatment", "tratamiento", "synopsis", "guion", "script", "screenplay"), "treatment", "Script or treatment"),
            (("finance", "financi", "funding plan", "plan de financiacion", "plan financiero"), "finance_plan", "Financing plan"),
            (("coprodu", "partner", "co-production", "co production", "agreement", "letter of intent", "loi"), "contract", "Coproduction agreement or LOI"),
            (("rights", "chain of title", "option agreement", "derechos"), "contract", "Chain of title"),
            (("distribution", "sales", "audience", "marketing"), None, "Distribution strategy"),
        )
        for needles, document_type, label in hints:
            if any(needle in normalized for needle in needles):
                return document_type or label
        return None

    def _document_label_hint(self, requirement_text: str) -> str | None:
        normalized = self._normalize_text(requirement_text)
        hints = (
            (("budget", "presupuesto", "coste", "cost"), "Budget breakdown"),
            (("treatment", "tratamiento", "synopsis", "guion", "script", "screenplay"), "Script or treatment"),
            (("finance", "financi", "funding plan", "plan de financiacion", "plan financiero"), "Financing plan"),
            (("coprodu", "partner", "co-production", "co production", "agreement", "letter of intent", "loi"), "Coproduction agreement or LOI"),
            (("rights", "chain of title", "option agreement", "derechos"), "Chain of title"),
            (("distribution", "sales", "audience", "marketing"), "Distribution strategy"),
        )
        for needles, label in hints:
            if any(needle in normalized for needle in needles):
                return label
        return None

    def _extract_structured_requirements(
        self,
        call: FundingCall,
        requirements: list[FundingRequirement],
    ) -> list[dict[str, Any]]:
        structured: list[dict[str, Any]] = []
        for requirement in requirements:
            structured.append(
                {
                    "requirement": requirement.requirement_text,
                    "category": requirement.category,
                    "is_mandatory": bool(requirement.is_mandatory),
                }
            )

        if structured:
            return structured

        fallback = self._json_loads(call.requirements_json)
        if isinstance(fallback, list):
            for item in fallback:
                if isinstance(item, str) and item.strip():
                    structured.append(
                        {
                            "requirement": item.strip(),
                            "category": "general",
                            "is_mandatory": True,
                        }
                    )
                elif isinstance(item, dict) and item.get("requirement"):
                    structured.append(
                        {
                            "requirement": str(item["requirement"]),
                            "category": str(item.get("category") or "general"),
                            "is_mandatory": bool(item.get("is_mandatory", True)),
                        }
                    )
        return structured

    def _build_rag_queries(
        self,
        profile: dict[str, Any],
        call: FundingCall,
        structured_requirements: list[dict[str, Any]],
    ) -> list[str]:
        queries = [
            f"{call.title} eligibility evidence for project {profile['title']}",
            f"{call.title} {call.region_scope} funding requirements documents",
        ]
        for item in structured_requirements[:4]:
            label = self._document_label_hint(item["requirement"]) or item["requirement"]
            queries.append(f"{call.title} {label} {item['requirement']}")

        unique_queries: list[str] = []
        for query in queries:
            if query not in unique_queries:
                unique_queries.append(query)
        return unique_queries[:6]

    async def _get_project_documents(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
    ) -> list[ProjectDocument]:
        result = await db.execute(
            select(ProjectDocument).where(
                ProjectDocument.project_id == project_id,
                ProjectDocument.organization_id == organization_id,
            )
        )
        return list(result.scalars().all())

    async def _retrieve_document_evidence(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        queries: list[str],
    ) -> dict[str, Any]:
        aggregated: dict[str, dict[str, Any]] = {}
        for query in queries:
            result = await project_document_rag_service.ask(
                db,
                project_id=project_id,
                organization_id=organization_id,
                query_text=query,
                top_k=4,
            )
            for chunk in result.get("retrieved_chunks", []):
                chunk_id = str(chunk.get("chunk_id"))
                if not chunk_id:
                    continue
                current = aggregated.get(chunk_id)
                normalized = {
                    "chunk_id": chunk_id,
                    "document_id": chunk.get("document_id"),
                    "file_name": chunk.get("file_name"),
                    "document_type": chunk.get("document_type"),
                    "chunk_index": chunk.get("chunk_index"),
                    "score": float(chunk.get("score") or 0.0),
                    "chunk_text": chunk.get("chunk_text") or "",
                    "metadata_json": chunk.get("metadata_json"),
                    "queries": [query],
                }
                if current is None:
                    aggregated[chunk_id] = normalized
                    continue
                current["score"] = max(float(current.get("score") or 0.0), normalized["score"])
                if query not in current["queries"]:
                    current["queries"].append(query)

        chunks = sorted(aggregated.values(), key=lambda item: item["score"], reverse=True)[:12]
        return {
            "queries": queries,
            "retrieved_chunks": chunks,
        }

    def _evaluate_document_requirement(
        self,
        requirement: dict[str, Any],
        retrieved_chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        requirement_text = str(requirement.get("requirement") or "")
        requirement_tokens = set(self._tokenize_text(requirement_text))
        preferred_document_hint = self._document_type_hint(requirement_text)

        best_chunk: dict[str, Any] | None = None
        best_score = 0.0
        for chunk in retrieved_chunks:
            chunk_tokens = set(self._tokenize_text(chunk.get("chunk_text")))
            overlap_ratio = 0.0
            if requirement_tokens:
                overlap_ratio = len(requirement_tokens & chunk_tokens) / max(1, len(requirement_tokens))
            type_bonus = 0.0
            document_type = self._normalize_text(chunk.get("document_type"))
            if preferred_document_hint and preferred_document_hint in {document_type, self._document_label_hint(requirement_text)}:
                type_bonus = 0.18
            score = float(chunk.get("score") or 0.0) + overlap_ratio + type_bonus
            if score > best_score:
                best_score = score
                best_chunk = chunk

        status = "unknown"
        confidence = "low"
        evidence_excerpt = ""
        reasoning = "No project evidence retrieved for this requirement."
        if best_chunk is not None:
            evidence_excerpt = str(best_chunk.get("chunk_text") or "")[:320]
            if best_score >= 0.95:
                status = "met"
                confidence = "high"
                reasoning = "Project documents contain strong matching evidence for this requirement."
            elif best_score >= 0.6:
                status = "partially_met"
                confidence = "medium"
                reasoning = "Project documents contain partial or indirect evidence for this requirement."
            elif requirement.get("is_mandatory", True):
                status = "unmet"
                confidence = "low"
                reasoning = "Retrieved project documents do not substantiate the mandatory requirement."
            else:
                reasoning = "Evidence exists but remains too weak to confirm compliance."
        elif requirement.get("is_mandatory", True):
            status = "unmet"
            reasoning = "Mandatory requirement lacks project-specific documented evidence."

        return {
            "requirement": requirement_text,
            "status": status,
            "evidence_excerpt": evidence_excerpt,
            "reasoning": reasoning,
            "confidence": confidence,
            "category": requirement.get("category"),
            "is_mandatory": bool(requirement.get("is_mandatory", True)),
            "supporting_chunk_id": best_chunk.get("chunk_id") if best_chunk else None,
        }

    def _build_rag_fit_summary(
        self,
        call: FundingCall,
        fit_level: str,
        evaluations: list[dict[str, Any]],
        blockers: list[str],
    ) -> str:
        met_count = len([item for item in evaluations if item.get("status") == "met"])
        partial_count = len([item for item in evaluations if item.get("status") == "partially_met"])
        mandatory_total = len([item for item in evaluations if item.get("is_mandatory")])
        if blockers:
            return f"{call.title} remains constrained after document review: {blockers[0]}."
        return (
            f"{call.title} is a {fit_level} fit after document review with {met_count} met and "
            f"{partial_count} partially met requirements across {mandatory_total or len(evaluations)} key checks."
        )

    def _build_rag_evaluation(
        self,
        *,
        baseline: dict[str, Any],
        call: FundingCall,
        structured_requirements: list[dict[str, Any]],
        evidence_payload: dict[str, Any],
        project_documents: list[ProjectDocument],
    ) -> dict[str, Any]:
        evaluations = [
            self._evaluate_document_requirement(requirement, evidence_payload.get("retrieved_chunks", []))
            for requirement in structured_requirements
        ]
        mandatory_evaluations = [item for item in evaluations if item.get("is_mandatory")]
        met_weight = 0.0
        max_weight = 0.0
        blocking_reasons = list(baseline.get("blocking_reasons_json", []))
        recommended_actions = list(baseline.get("recommended_actions_json", []))
        missing_documents = list(baseline.get("missing_documents_json", []))
        rag_missing_requirements: list[str] = []

        for item in evaluations:
            weight = 1.5 if item.get("is_mandatory") else 1.0
            max_weight += weight
            if item["status"] == "met":
                met_weight += weight
            elif item["status"] == "partially_met":
                met_weight += weight * 0.6
            elif item["status"] == "unknown":
                met_weight += weight * 0.25
            else:
                rag_missing_requirements.append(item["requirement"])
                if item.get("is_mandatory"):
                    blocking_reasons.append(f"Missing documented evidence: {item['requirement']}")
            label_hint = self._document_label_hint(item["requirement"])
            if item["status"] in {"unmet", "unknown"} and label_hint and label_hint not in missing_documents:
                missing_documents.append(label_hint)

        evidence_score = 0.0 if max_weight <= 0 else (met_weight / max_weight) * 100.0
        baseline_score = float(baseline.get("match_score") or 0.0)
        adjusted_score = baseline_score + ((evidence_score - 50.0) * 0.25)
        supportive_evidence = any(
            item.get("status") in {"met", "partially_met"} for item in evaluations
        )
        if project_documents and supportive_evidence:
            adjusted_score = max(adjusted_score, baseline_score + min(10.0, evidence_score * 0.08))
        if project_documents:
            adjusted_score = max(adjusted_score, baseline_score)
        if not project_documents:
            adjusted_score = min(adjusted_score, baseline_score - 8.0)
            recommended_actions.append("Upload and index project documents before relying on RAG enrichment")

        final_score = max(0, min(100, round(adjusted_score)))
        unique_blockers = list(dict.fromkeys(item for item in blocking_reasons if item))
        unique_missing_documents = list(dict.fromkeys(item for item in missing_documents if item))
        unique_actions = list(dict.fromkeys(item for item in recommended_actions if item))
        fit_level = self._fit_level_from_score(final_score, unique_blockers)

        met_count = len([item for item in mandatory_evaluations if item.get("status") == "met"])
        partial_count = len([item for item in mandatory_evaluations if item.get("status") == "partially_met"])
        rag_confidence = "high"
        if not evidence_payload.get("retrieved_chunks") or len(rag_missing_requirements) >= 2:
            rag_confidence = "medium"
        if not project_documents or len(rag_missing_requirements) >= max(1, len(mandatory_evaluations)):
            rag_confidence = "low"

        return {
            **baseline,
            "baseline_score": baseline_score,
            "rag_enriched_score": final_score,
            "match_score": final_score,
            "fit_level": fit_level,
            "fit_summary": self._build_rag_fit_summary(call, fit_level, evaluations, unique_blockers),
            "blocking_reasons_json": unique_blockers,
            "missing_documents_json": unique_missing_documents,
            "recommended_actions_json": unique_actions,
            "confidence_level": rag_confidence,
            "rag_confidence_level": rag_confidence,
            "rag_rationale": (
                f"Baseline score {baseline_score:.0f}; document evidence supports {met_count} mandatory requirements "
                f"and partially supports {partial_count}."
            ),
            "rag_missing_requirements": rag_missing_requirements,
            "evidence_chunks_json": {
                "queries": evidence_payload.get("queries", []),
                "retrieved_chunks": evidence_payload.get("retrieved_chunks", []),
                "requirement_evaluations": evaluations,
                "document_inventory": [
                    {
                        "document_id": str(document.id),
                        "document_type": str(document.document_type),
                        "file_name": str(document.file_name),
                    }
                    for document in project_documents
                ],
            },
            "matcher_mode": self.RAG_MODE,
            "evaluation_version": self.RAG_EVALUATION_VERSION,
        }

    def _evaluate_match(
        self,
        profile: dict[str, Any],
        call: FundingCall,
        source: FundingSource,
        requirements: list[FundingRequirement],
    ) -> dict[str, Any]:
        score = 20
        blocking_reasons: list[str] = []
        recommended_actions: list[str] = []

        phase_score, phase_blockers, phase_actions = self._phase_compatibility(
            profile["phase"], call.phase
        )
        score += phase_score
        blocking_reasons.extend(phase_blockers)
        recommended_actions.extend(phase_actions)

        work_type_score, work_type_blockers = self._work_type_compatibility(
            profile["type_of_work"], call
        )
        score += work_type_score
        blocking_reasons.extend(work_type_blockers)

        territory_score, territory_blockers, territory_actions = self._territory_compatibility(
            profile["countries_involved"], call
        )
        score += territory_score
        blocking_reasons.extend(territory_blockers)
        recommended_actions.extend(territory_actions)

        collaboration_score, collaboration_blockers, collaboration_actions = self._collaboration_compatibility(
            profile, call
        )
        score += collaboration_score
        blocking_reasons.extend(collaboration_blockers)
        recommended_actions.extend(collaboration_actions)

        budget_score, budget_blockers, budget_actions = self._budget_compatibility(profile, call)
        score += budget_score
        blocking_reasons.extend(budget_blockers)
        recommended_actions.extend(budget_actions)

        applicant_score, applicant_blockers, applicant_actions = self._applicant_hints(profile, call)
        score += applicant_score
        blocking_reasons.extend(applicant_blockers)
        recommended_actions.extend(applicant_actions)

        deadline_score, deadline_blockers, deadline_actions, deadline_state = self._deadline_signal(call)
        score += deadline_score
        blocking_reasons.extend(deadline_blockers)
        recommended_actions.extend(deadline_actions)

        if call.region_scope == "spain" and profile["type_of_work"] in {"feature", "documentary", "animation", "short"}:
            score += 6
        if call.region_scope == "europe" and len(profile["countries_involved"]) >= 2:
            score += 6
        if call.region_scope == "iberoamerica_latam" and any(
            self._normalize_text(country) in self.LATAM_COUNTRIES for country in profile["countries_involved"]
        ):
            score += 6
        if profile.get("funding_gap", 0) <= 0:
            score -= 6

        missing_documents = self._detect_missing_documents(profile, call, requirements)
        if missing_documents:
            score -= min(12, len(missing_documents) * 3)
            recommended_actions.append("Close the missing application documents")

        unique_blockers = list(dict.fromkeys(reason for reason in blocking_reasons if reason))
        unique_missing = list(dict.fromkeys(item for item in missing_documents if item))
        unique_actions = list(dict.fromkeys(action for action in recommended_actions if action))
        match_score = max(0, min(100, score))

        fit_level = self._fit_level_from_score(match_score, unique_blockers)
        confidence_level = self._confidence_from_profile(profile, unique_blockers, deadline_state)

        fit_summary = self._build_fit_summary(fit_level, call, unique_blockers, unique_actions)

        return {
            "funding_call_id": call.id,
            "source_id": source.id,
            "source_code": source.code,
            "source_name": source.name,
            "source_region": call.region_scope,
            "title": call.title,
            "status": call.status,
            "opportunity_type": call.opportunity_type,
            "phase": call.phase,
            "deadline_at": call.close_date.isoformat() if call.close_date else None,
            "official_url": call.official_url,
            "match_score": match_score,
            "baseline_score": match_score,
            "rag_enriched_score": None,
            "fit_level": fit_level,
            "fit_summary": fit_summary,
            "blocking_reasons_json": unique_blockers,
            "missing_documents_json": unique_missing,
            "recommended_actions_json": unique_actions,
            "confidence_level": confidence_level,
            "rag_confidence_level": None,
            "rag_rationale": None,
            "rag_missing_requirements": [],
            "evidence_chunks_json": {"queries": [], "retrieved_chunks": [], "requirement_evaluations": []},
            "matcher_mode": self.CLASSIC_MODE,
            "evaluation_version": self.EVALUATION_VERSION,
        }

    async def _load_call_requirements(
        self,
        db: AsyncSession,
    ) -> tuple[list[tuple[FundingCall, FundingSource]], dict[str, list[FundingRequirement]]]:
        calls_result = await db.execute(
            select(FundingCall, FundingSource)
            .join(FundingSource, FundingSource.id == FundingCall.source_id)
            .order_by(FundingCall.close_date.asc(), FundingCall.title.asc())
        )
        call_rows = list(calls_result.all())
        requirement_rows = await db.execute(select(FundingRequirement))
        requirements_by_call: dict[str, list[FundingRequirement]] = {}
        for requirement in requirement_rows.scalars().all():
            requirements_by_call.setdefault(requirement.call_id, []).append(requirement)
        return call_rows, requirements_by_call

    async def _replace_matches(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        matches: list[dict[str, Any]],
        matcher_mode: str,
    ) -> None:
        filters = [
            ProjectFundingMatch.project_id == project_id,
            ProjectFundingMatch.organization_id == organization_id,
        ]
        if matcher_mode == self.CLASSIC_MODE:
            filters.append(
                or_(
                    ProjectFundingMatch.matcher_mode == self.CLASSIC_MODE,
                    ProjectFundingMatch.matcher_mode.is_(None),
                )
            )
        else:
            filters.append(ProjectFundingMatch.matcher_mode == matcher_mode)

        await db.execute(delete(ProjectFundingMatch).where(*filters))
        await db.flush()

        for evaluation in matches:
            db.add(
                ProjectFundingMatch(
                    id=str(uuid.uuid4()),
                    project_id=project_id,
                    organization_id=organization_id,
                    funding_call_id=evaluation["funding_call_id"],
                    match_score=evaluation["match_score"],
                    baseline_score=evaluation.get("baseline_score"),
                    rag_enriched_score=evaluation.get("rag_enriched_score"),
                    fit_level=evaluation["fit_level"],
                    fit_summary=evaluation["fit_summary"],
                    blocking_reasons=self._json_dumps(evaluation["blocking_reasons_json"]),
                    missing_documents=self._json_dumps(evaluation["missing_documents_json"]),
                    recommended_actions=self._json_dumps(evaluation["recommended_actions_json"]),
                    evidence_chunks_json=self._json_dumps(evaluation.get("evidence_chunks_json")),
                    rag_rationale=evaluation.get("rag_rationale"),
                    rag_missing_requirements=self._json_dumps(evaluation.get("rag_missing_requirements") or []),
                    confidence_level=evaluation.get("confidence_level"),
                    rag_confidence_level=evaluation.get("rag_confidence_level"),
                    matcher_mode=evaluation.get("matcher_mode", matcher_mode),
                    evaluation_version=evaluation["evaluation_version"],
                )
            )

    async def compute_matches(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> dict[str, Any]:
        from schemas.auth_schema import TenantContext
        profile = await self.build_project_profile(
            db, project_id,
            TenantContext(
                user_id="compute_matches",
                organization_id=organization_id,
                role="admin",
                is_admin=False,
                is_global_admin=False,
                auth_method="internal",
            ),
        )
        if profile is None:
            return {
                "project_id": project_id,
                "organization_id": organization_id,
                "project_profile": None,
                "matches": [],
                "checklist": self._build_empty_checklist(project_id),
            }

        call_rows, requirements_by_call = await self._load_call_requirements(db)

        matches: list[dict[str, Any]] = []
        for call, source in call_rows:
            evaluation = self._evaluate_match(
                profile,
                call,
                source,
                requirements_by_call.get(call.id, []),
            )
            matches.append(evaluation)

        await self._replace_matches(
            db,
            project_id=project_id,
            organization_id=organization_id,
            matches=matches,
            matcher_mode=self.CLASSIC_MODE,
        )
        await db.commit()
        matches.sort(key=lambda item: item["match_score"], reverse=True)
        return {
            "project_id": project_id,
            "organization_id": organization_id,
            "project_profile": profile,
            "matches": matches,
            "checklist": self._build_checklist_payload(project_id, matches),
        }

    async def compute_rag_matches(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> dict[str, Any]:
        from schemas.auth_schema import TenantContext
        profile = await self.build_project_profile(
            db, project_id,
            TenantContext(
                user_id="compute_rag_matches",
                organization_id=organization_id,
                role="admin",
                is_admin=False,
                is_global_admin=False,
                auth_method="internal",
            ),
        )
        if profile is None:
            return {
                "project_id": project_id,
                "organization_id": organization_id,
                "project_profile": None,
                "matches": [],
                "checklist": self._build_empty_checklist(project_id),
            }

        call_rows, requirements_by_call = await self._load_call_requirements(db)
        project_documents = await self._get_project_documents(
            db,
            project_id=project_id,
            organization_id=organization_id,
        )

        matches: list[dict[str, Any]] = []
        for call, source in call_rows:
            call_requirements = requirements_by_call.get(call.id, [])
            baseline = self._evaluate_match(profile, call, source, call_requirements)
            structured_requirements = self._extract_structured_requirements(call, call_requirements)
            queries = self._build_rag_queries(profile, call, structured_requirements)
            evidence_payload = await self._retrieve_document_evidence(
                db,
                project_id=project_id,
                organization_id=organization_id,
                queries=queries,
            )
            matches.append(
                self._build_rag_evaluation(
                    baseline=baseline,
                    call=call,
                    structured_requirements=structured_requirements,
                    evidence_payload=evidence_payload,
                    project_documents=project_documents,
                )
            )

        await self._replace_matches(
            db,
            project_id=project_id,
            organization_id=organization_id,
            matches=matches,
            matcher_mode=self.RAG_MODE,
        )
        await db.commit()
        matches.sort(key=lambda item: item["match_score"], reverse=True)
        return {
            "project_id": project_id,
            "organization_id": organization_id,
            "project_profile": profile,
            "matches": matches,
            "checklist": self._build_checklist_payload(project_id, matches),
        }

    async def get_matches(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        matcher_mode: str = CLASSIC_MODE,
    ) -> list[dict[str, Any]]:
        mode_filter = (
            or_(
                ProjectFundingMatch.matcher_mode == self.CLASSIC_MODE,
                ProjectFundingMatch.matcher_mode.is_(None),
            )
            if matcher_mode == self.CLASSIC_MODE
            else ProjectFundingMatch.matcher_mode == matcher_mode
        )
        result = await db.execute(
            select(ProjectFundingMatch, FundingCall, FundingSource)
            .join(FundingCall, FundingCall.id == ProjectFundingMatch.funding_call_id)
            .join(FundingSource, FundingSource.id == FundingCall.source_id)
            .where(
                ProjectFundingMatch.project_id == project_id,
                ProjectFundingMatch.organization_id == organization_id,
                mode_filter,
            )
            .order_by(ProjectFundingMatch.match_score.desc(), FundingCall.title.asc())
        )
        matches: list[dict[str, Any]] = []
        for match, call, source in result.all():
            matches.append(
                {
                    "funding_call_id": call.id,
                    "source_id": source.id,
                    "source_code": source.code,
                    "source_name": source.name,
                    "source_region": call.region_scope,
                    "title": call.title,
                    "status": call.status,
                    "opportunity_type": call.opportunity_type,
                    "phase": call.phase,
                    "deadline_at": call.close_date.isoformat() if call.close_date else None,
                    "official_url": call.official_url,
                    "match_score": match.match_score,
                    "baseline_score": match.baseline_score,
                    "rag_enriched_score": match.rag_enriched_score,
                    "fit_level": match.fit_level,
                    "fit_summary": match.fit_summary,
                    "blocking_reasons_json": self._json_loads(match.blocking_reasons) or [],
                    "missing_documents_json": self._json_loads(match.missing_documents) or [],
                    "recommended_actions_json": self._json_loads(match.recommended_actions) or [],
                    "evidence_chunks_json": self._json_loads(match.evidence_chunks_json) or {},
                    "rag_rationale": match.rag_rationale,
                    "rag_missing_requirements": self._json_loads(match.rag_missing_requirements) or [],
                    "confidence_level": match.confidence_level,
                    "rag_confidence_level": match.rag_confidence_level,
                    "matcher_mode": match.matcher_mode or self.CLASSIC_MODE,
                    "match_id": str(match.id),
                    "evaluation_version": match.evaluation_version,
                    "computed_at": match.computed_at.isoformat() if match.computed_at else None,
                }
            )
        return matches

    async def get_match_evidence(
        self,
        db: AsyncSession,
        *,
        project_id: str,
        organization_id: str,
        match_id: str,
    ) -> dict[str, Any] | None:
        result = await db.execute(
            select(ProjectFundingMatch, FundingCall, FundingSource)
            .join(FundingCall, FundingCall.id == ProjectFundingMatch.funding_call_id)
            .join(FundingSource, FundingSource.id == FundingCall.source_id)
            .where(
                ProjectFundingMatch.id == match_id,
                ProjectFundingMatch.project_id == project_id,
                ProjectFundingMatch.organization_id == organization_id,
                ProjectFundingMatch.matcher_mode == self.RAG_MODE,
            )
        )
        row = result.one_or_none()
        if row is None:
            return None
        match, call, source = row
        return {
            "match_id": str(match.id),
            "project_id": project_id,
            "organization_id": organization_id,
            "funding_call_id": str(call.id),
            "title": str(call.title),
            "source_code": str(source.code),
            "source_name": str(source.name),
            "baseline_score": match.baseline_score,
            "rag_enriched_score": match.rag_enriched_score,
            "match_score": match.match_score,
            "fit_level": match.fit_level,
            "fit_summary": match.fit_summary,
            "rag_rationale": match.rag_rationale,
            "rag_missing_requirements": self._json_loads(match.rag_missing_requirements) or [],
            "blocking_reasons_json": self._json_loads(match.blocking_reasons) or [],
            "missing_documents_json": self._json_loads(match.missing_documents) or [],
            "recommended_actions_json": self._json_loads(match.recommended_actions) or [],
            "evidence_chunks_json": self._json_loads(match.evidence_chunks_json) or {},
            "confidence_level": match.confidence_level,
            "rag_confidence_level": match.rag_confidence_level,
            "matcher_mode": match.matcher_mode or self.RAG_MODE,
            "evaluation_version": match.evaluation_version,
            "computed_at": match.computed_at.isoformat() if match.computed_at else None,
        }

    def _build_empty_checklist(self, project_id: str) -> dict[str, Any]:
        return {
            "project_id": project_id,
            "total_opportunities": 0,
            "high_matches": 0,
            "medium_matches": 0,
            "low_matches": 0,
            "blocked_matches": 0,
            "documents": [],
            "blockers": [],
            "priority_actions": [],
            "deadline_risks": [],
        }

    def _build_checklist_payload(
        self,
        project_id: str,
        matches: list[dict[str, Any]],
    ) -> dict[str, Any]:
        documents: list[str] = []
        blockers: list[str] = []
        actions: list[str] = []
        deadline_risks: list[dict[str, Any]] = []
        for match in matches:
            documents.extend(match.get("missing_documents_json", []))
            blockers.extend(match.get("blocking_reasons_json", []))
            actions.extend(match.get("recommended_actions_json", []))
            if match.get("deadline_at") and match.get("fit_level") in {"high", "medium"}:
                deadline_risks.append(
                    {
                        "funding_call_id": match["funding_call_id"],
                        "title": match["title"],
                        "deadline_at": match["deadline_at"],
                        "fit_level": match["fit_level"],
                    }
                )

        unique_documents = list(dict.fromkeys(documents))[:20]
        unique_blockers = list(dict.fromkeys(blockers))[:20]
        unique_actions = list(dict.fromkeys(actions))[:20]
        return {
            "project_id": project_id,
            "total_opportunities": len(matches),
            "high_matches": len([item for item in matches if item.get("fit_level") == "high"]),
            "medium_matches": len([item for item in matches if item.get("fit_level") == "medium"]),
            "low_matches": len([item for item in matches if item.get("fit_level") == "low"]),
            "blocked_matches": len([item for item in matches if item.get("fit_level") == "blocked"]),
            "documents": unique_documents,
            "blockers": unique_blockers,
            "priority_actions": unique_actions,
            "deadline_risks": sorted(deadline_risks, key=lambda item: item["deadline_at"])[:10],
        }

    async def get_checklist(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
        matcher_mode: str = CLASSIC_MODE,
    ) -> dict[str, Any]:
        matches = await self.get_matches(db, project_id, organization_id, matcher_mode=matcher_mode)
        return self._build_checklist_payload(project_id, matches)


funding_matcher_service = FundingMatcherService()
