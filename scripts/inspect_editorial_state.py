from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("DATABASE_URL", f"sqlite+aiosqlite:///{(ROOT / 'smoke_editorial_mvp.db').resolve()}")
os.environ.setdefault("USE_ALEMBIC", "0")

from sqlalchemy import func, select

from database import AsyncSessionLocal
from models.core import Project
from models.delivery import Deliverable
from models.postproduction import AssemblyCut, Take
from models.production import ProductionBreakdown
from services.assembly_service import assembly_service
from services.fcpxml_export_service import fcpxml_export_service
from services.fcpxml_validation_service import fcpxml_validation_service
from services.media_path_resolver_service import media_path_resolver_service
from models.storage import MediaAsset, StorageSource


async def main(project_id: str) -> None:
    async with AsyncSessionLocal() as session:
        project_result = await session.execute(select(Project).where(Project.id == project_id))
        project = project_result.scalar_one_or_none()
        if project is None:
            raise SystemExit(f"Project not found: {project_id}")
        scenes_count = 0
        breakdown_result = await session.execute(select(ProductionBreakdown).where(ProductionBreakdown.project_id == project_id))
        breakdown = breakdown_result.scalar_one_or_none()
        if breakdown and breakdown.breakdown_json:
            payload = json.loads(breakdown.breakdown_json)
            scenes_count = len(payload.get("scenes", []))

        takes_count = (await session.execute(select(func.count(Take.id)).where(Take.project_id == project_id))).scalar_one() or 0
        recommended_count = (
            await session.execute(select(func.count(Take.id)).where(Take.project_id == project_id, Take.is_recommended.is_(True)))
        ).scalar_one() or 0
        dual_system_takes = (
            await session.execute(select(func.count(Take.id)).where(Take.project_id == project_id, Take.dual_system_status == "matched"))
        ).scalar_one() or 0
        audio_metadata_parsed = (
            await session.execute(select(func.count(Take.id)).where(Take.project_id == project_id, Take.audio_metadata_status == "parsed"))
        ).scalar_one() or 0
        sync_confidence_avg = (
            await session.execute(select(func.avg(Take.sync_confidence)).where(Take.project_id == project_id, Take.sync_confidence.is_not(None)))
        ).scalar_one()
        sync_conflicts = (
            await session.execute(select(func.count(Take.id)).where(Take.project_id == project_id, Take.dual_system_status == "conflict"))
        ).scalar_one() or 0
        assemblies_count = (
            await session.execute(select(func.count(AssemblyCut.id)).where(AssemblyCut.project_id == project_id))
        ).scalar_one() or 0
        latest_assembly = await assembly_service.get_latest_assembly(session, project_id=project_id)
        assembly_present = latest_assembly.get("assembly_cut") is not None
        shots_count = sum(len(latest_assembly.get("assembly_cut", {}).get("items", [])) for _ in [0]) if assembly_present else 0
        fcpxml_valid = False
        resolved_media_count = 0
        offline_media_count = 0
        relink_report_status = "missing_assembly"
        if assembly_present:
            asset_ids = {
                str(asset_id)
                for item in latest_assembly.get("assembly_cut", {}).get("items", [])
                for asset_id in [item.get("source_media_asset_id"), item.get("audio_media_asset_id")]
                if asset_id
            }
            assets_by_id = {}
            storage_sources_by_id = {}
            if asset_ids:
                assets_result = await session.execute(select(MediaAsset).where(MediaAsset.id.in_(asset_ids)))
                assets = list(assets_result.scalars().all())
                assets_by_id = {str(asset.id): asset for asset in assets}
                source_ids = {str(asset.storage_source_id) for asset in assets if asset.storage_source_id}
                if source_ids:
                    sources_result = await session.execute(select(StorageSource).where(StorageSource.id.in_(source_ids)))
                    storage_sources_by_id = {str(source.id): source for source in sources_result.scalars().all()}
            resolved_assets = {
                asset_id: media_path_resolver_service.resolve_asset(
                    asset,
                    storage_source=storage_sources_by_id.get(str(asset.storage_source_id)) if asset.storage_source_id else None,
                )
                for asset_id, asset in assets_by_id.items()
            }
            fcpxml_bytes, _file_name, _manifest = fcpxml_export_service.build_fcpxml(
                project_name=str(project.name),
                assembly_cut=latest_assembly,
                resolved_assets=resolved_assets,
            )
            validation = fcpxml_validation_service.validate(fcpxml_bytes)
            fcpxml_valid = bool(validation.get("valid"))
            resolved_media_count = sum(1 for item in resolved_assets.values() if item.get("status") == "resolved")
            offline_media_count = sum(1 for item in resolved_assets.values() if item.get("status") == "offline")
            relink_report_status = "ready"

        package_result = await session.execute(
            select(Deliverable)
            .where(Deliverable.project_id == project_id, Deliverable.format_type == "ZIP")
            .order_by(Deliverable.created_at.desc(), Deliverable.id.desc())
            .limit(1)
        )
        package_deliverable = package_result.scalars().first()

        print(json.dumps(
            {
                "project_id": project_id,
                "scenes": scenes_count,
                "shots": shots_count,
                "takes": int(takes_count),
                "recommended_takes": int(recommended_count),
                "dual_system_takes": int(dual_system_takes),
                "audio_metadata_parsed": int(audio_metadata_parsed),
                "sync_confidence_avg": float(sync_confidence_avg or 0.0),
                "sync_conflicts": int(sync_conflicts),
                "assembly_cuts": int(assemblies_count),
                "fcpxml_export_status": "ready" if assembly_present else "missing_assembly",
                "fcpxml_valid": fcpxml_valid,
                "resolved_media_count": resolved_media_count,
                "offline_media_count": offline_media_count,
                "relink_report_status": relink_report_status,
                "dual_system_export_status": "partial_safe" if offline_media_count == 0 and fcpxml_valid else "review",
                "editorial_package_status": "ready" if package_deliverable is not None else "missing",
            },
            ensure_ascii=False,
            indent=2,
        ))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/inspect_editorial_state.py <project_id>")
    asyncio.run(main(sys.argv[1]))
