from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.production import FundingCall, ProjectFundingMatch


class FundingAlertService:
    async def check_deadline_alerts(
        self,
        db: AsyncSession,
        organization_id: str,
        days_threshold: int = 30,
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        threshold = now + timezone.utc.utcoffset(datetime.now()) + datetime.timedelta(days=days_threshold)

        result = await db.execute(
            select(FundingCall).where(
                FundingCall.status == "open",
                FundingCall.deadline != None,
                FundingCall.deadline <= threshold,
            )
        )
        calls = result.scalars().all()

        alerts = []
        for call in calls:
            days_left = (call.deadline - now).days
            if days_left < 0:
                alert_type = "deadline_passed"
                severity = "critical"
            elif days_left <= 7:
                alert_type = "deadline_urgent"
                severity = "high"
            elif days_left <= 14:
                alert_type = "deadline_soon"
                severity = "medium"
            else:
                alert_type = "deadline_upcoming"
                severity = "low"

            alerts.append({
                "alert_type": alert_type,
                "severity": severity,
                "funding_call_id": call.id,
                "title": call.title,
                "deadline": call.deadline.isoformat() if call.deadline else None,
                "days_remaining": days_left,
                "region": call.region,
                "opportunity_type": call.opportunity_type,
            })

        return sorted(alerts, key=lambda x: x["days_remaining"])

    async def check_match_alerts(
        self,
        db: AsyncSession,
        project_id: str,
        organization_id: str,
    ) -> list[dict[str, Any]]:
        result = await db.execute(
            select(ProjectFundingMatch)
            .where(
                ProjectFundingMatch.project_id == project_id,
                ProjectFundingMatch.organization_id == organization_id,
                or_(
                    ProjectFundingMatch.matcher_mode == "classic",
                    ProjectFundingMatch.matcher_mode.is_(None),
                ),
            )
            .order_by(ProjectFundingMatch.match_score.desc())
        )
        matches = result.scalars().all()

        high_matches = [m for m in matches if m.match_score >= 60]
        medium_matches = [m for m in matches if 30 <= m.match_score < 60]

        alerts = []

        if high_matches:
            alerts.append({
                "alert_type": "high_match_opportunity",
                "severity": "high",
                "title": f"{len(high_matches)} oportunidades altamente compatibles",
                "description": "Existen oportunidades con alta compatibilidad - revisar y preparar solicitudes",
                "count": len(high_matches),
            })

        if medium_matches:
            alerts.append({
                "alert_type": "medium_match_opportunity",
                "severity": "medium",
                "title": f"{len(medium_matches)} oportunidades parcialmente compatibles",
                "description": "Oportunidades que requieren revisión de requisitos",
                "count": len(medium_matches),
            })

        return alerts

    async def get_funding_dashboard_alerts(
        self,
        db: AsyncSession,
        organization_id: str,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        deadline_alerts = await self.check_deadline_alerts(db, organization_id)

        project_alerts = []
        if project_id:
            project_alerts = await self.check_match_alerts(db, project_id, organization_id)

        critical_count = len([a for a in deadline_alerts if a["severity"] == "critical"])
        high_count = len([a for a in deadline_alerts if a["severity"] == "high"])
        urgent_count = critical_count + high_count

        return {
            "summary": {
                "total_alerts": len(deadline_alerts) + len(project_alerts),
                "critical": critical_count,
                "high": high_count,
                "urgent": urgent_count,
            },
            "deadline_alerts": deadline_alerts[:20],
            "project_alerts": project_alerts,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


funding_alert_service = FundingAlertService()
