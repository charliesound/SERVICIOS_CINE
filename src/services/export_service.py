import asyncio
import json
import os
import zipfile
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.core import ProjectJob, Project
from models.storage import MediaAsset
from models.delivery import Deliverable, DeliverableStatus
from services.delivery_service import delivery_service
from services.job_tracking_service import job_tracking_service
from services.logging_service import logger
from database import AsyncSessionLocal


class ExportService:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def trigger_project_export(
        self,
        project_id: str,
        organization_id: str,
        user_id: str,
        export_name: str = None,
    ) -> ProjectJob:
        """
        Registers a new project export job and triggers the background task.
        """
        async with AsyncSessionLocal() as db:
            # 1. Create the Deliverable entry (DRAFT)
            name = export_name or f"Export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Using a modified delivery_service or direct creation if service constraint is too tight
            deliverable = Deliverable(
                project_id=project_id,
                organization_id=organization_id,
                source_review_id=None,  # Project level
                name=name,
                format_type="ZIP",
                delivery_payload={"status": "initializing"},
                status=DeliverableStatus.DRAFT,
            )
            db.add(deliverable)
            await db.commit()
            await db.refresh(deliverable)

            # 2. Create the ProjectJob
            job = ProjectJob(
                organization_id=organization_id,
                project_id=project_id,
                job_type="export_zip",
                status="pending",
                created_by=user_id,
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)

            # 3. Track the initiation
            await job_tracking_service.record_project_job_event(
                db,
                job=job,
                event_type="job_started",
                status_from="pending",
                status_to="running",
                message="Project export initiated",
                detail=f"Target deliverable: {deliverable.id}",
            )
            job.status = "running"
            await db.commit()

            # 4. Fire and forget the background process
            # In a real production app with Celery/Redis this would be a task.
            # Here we follow the async task pattern of the JobScheduler.
            asyncio.create_task(
                self.process_export_job(str(job.id), str(deliverable.id))
            )

            return job

    async def process_export_job(self, job_id: str, deliverable_id: str):
        """
        Core logic for gathering assets and creating the ZIP file.
        """
        logger.info(f"Processing export job {job_id} for deliverable {deliverable_id}")

        async with AsyncSessionLocal() as db:
            job_result = await db.execute(
                select(ProjectJob).where(ProjectJob.id == job_id)
            )
            job = job_result.scalar_one_or_none()
            if not job:
                logger.error(f"Job {job_id} not found for export")
                return

            deliverable_result = await db.execute(
                select(Deliverable).where(Deliverable.id == deliverable_id)
            )
            deliverable = deliverable_result.scalar_one_or_none()
            if not deliverable:
                logger.error(f"Deliverable {deliverable_id} not found for export")
                job.status = "failed"
                job.error_message = "Target deliverable not found"
                await db.commit()
                return

            try:
                project_id = job.project_id

                # Update status
                deliverable.delivery_payload = {
                    "status": "gathering_assets",
                    "progress": 10,
                }
                await db.commit()

                # Get all media assets
                assets_result = await db.execute(
                    select(MediaAsset).where(MediaAsset.project_id == project_id)
                )
                assets = assets_result.scalars().all()

                if not assets:
                    logger.warning(f"No assets found for project {project_id}")

                # Prepare ZIP with Org Segregation
                org_dir = self.export_dir / str(deliverable.organization_id)
                org_dir.mkdir(parents=True, exist_ok=True)
                
                zip_filename = f"ALC_Export_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                zip_path = org_dir / zip_filename

                # Group assets by sequence_id
                assets_by_sequence: Dict[str, List[MediaAsset]] = {}
                for asset in assets:
                    meta = (
                        json.loads(asset.metadata_json) if asset.metadata_json else {}
                    )
                    seq_id = meta.get("sequence_id", "no_sequence")
                    if seq_id not in assets_by_sequence:
                        assets_by_sequence[seq_id] = []
                    assets_by_sequence[seq_id].append(asset)

                manifest = {
                    "project_id": project_id,
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "asset_count": len(assets),
                    "sequences": list(assets_by_sequence.keys()),
                    "assets": [],
                }

                deliverable.delivery_payload = {"status": "zipping", "progress": 30}
                await db.commit()

                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for seq_id, seq_assets in assets_by_sequence.items():
                        # Create sequence folder in ZIP
                        seq_folder = f"sequence_{seq_id}"

                        for i, asset in enumerate(seq_assets):
                            file_path = Path(asset.canonical_path)
                            meta = (
                                json.loads(asset.metadata_json)
                                if asset.metadata_json
                                else {}
                            )
                            shot_order = meta.get("shot_order", 0)
                            visual_mode = meta.get("visual_mode", "unknown")
                            prompt_summary = meta.get("prompt_summary", "")

                            # Build path: sequence_A/shot_1_filename.png
                            ext = asset.file_extension or ".png"
                            arcname = (
                                f"{seq_folder}/shot_{shot_order}_{asset.file_name}"
                            )

                            if file_path.exists():
                                zf.write(file_path, arcname=arcname)
                                manifest["assets"].append(
                                    {
                                        "id": asset.id,
                                        "file_name": asset.file_name,
                                        "sequence_id": seq_id,
                                        "shot_order": shot_order,
                                        "visual_mode": visual_mode,
                                        "prompt_summary": prompt_summary[:200]
                                        if prompt_summary
                                        else "",
                                        "arcname": arcname,
                                    }
                                )
                            else:
                                logger.warning(f"Asset file not found: {file_path}")

                        # Update progress occasionally
                        if i % 5 == 0:
                            progress = (
                                30 + int((i / len(assets)) * 50) if assets else 80
                            )
                            deliverable.delivery_payload = {
                                "status": "zipping",
                                "progress": progress,
                            }
                            await db.commit()

                    # Add manifest
                    zf.writestr("manifest.json", json.dumps(manifest, indent=2))

                # Finalize
                file_size = zip_path.stat().st_size

                deliverable.status = DeliverableStatus.READY
                deliverable.delivery_payload = {
                    "status": "ready",
                    "progress": 100,
                    "file_path": str(zip_path.absolute()),
                    "file_name": zip_filename,
                    "file_size": file_size,
                    "manifest": manifest,
                }

                job.status = "completed"
                job.completed_at = datetime.utcnow()
                job.result_data = json.dumps(
                    {"deliverable_id": deliverable_id, "zip_file": zip_filename}
                )

                await job_tracking_service.record_project_job_event(
                    db,
                    job=job,
                    event_type="job_completed",
                    status_from="running",
                    status_to="completed",
                    message="Project export completed successfully",
                    detail=f"ZIP size: {file_size} bytes",
                )

                await db.commit()
                logger.info(f"Export Job {job_id} COMPLETED. ZIP saved at {zip_path}")

            except Exception as e:
                logger.error(f"Error in export job {job_id}: {str(e)}", exc_info=True)
                job.status = "failed"
                job.error_message = str(e)
                deliverable.status = "error"
                deliverable.delivery_payload = {"status": "failed", "error": str(e)}

                await job_tracking_service.record_project_job_event(
                    db,
                    job=job,
                    event_type="job_failed",
                    status_from="running",
                    status_to="failed",
                    message="Project export failed",
                    detail=str(e),
                )
                await db.commit()


export_service = ExportService()
