import asyncio
import os
import sys
import json
import uuid
from datetime import datetime

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/flux_backend_test.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from database import init_db, AsyncSessionLocal
from models.core import Project, ProjectJob
from models.storage import MediaAsset
from services.instance_registry import registry
from services.comfyui_client_factory import factory


async def test_flux_from_backend():
    await init_db()
    registry.load_config()

    print("=== Testing FLUX from AILinkCinema Backend ===")

    # Create project
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="FLUX Backend Test")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print(f"Project: {proj_id}")

    job_id = f"job-flux-backend-{uuid.uuid4().hex[:8]}"

    # Create job
    async with AsyncSessionLocal() as session:
        job = ProjectJob(
            id=job_id,
            organization_id="demo-org",
            project_id=proj_id,
            job_type="render:storyboard_flux",
            status="running",
            result_data=json.dumps({"motor": "flux", "test": "backend_integration"}),
        )
        session.add(job)
        await session.commit()

    # FLUX workflow
    wf = {
        "1": {
            "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": "cinematic wide shot of cozy cafe interior, warm morning light, wooden tables, film still",
                "t5xxl": "cinematic wide shot of cozy cafe interior, warm morning light, wooden tables, film still",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
        "3": {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": "blurry, low quality, bad anatomy, watermark, text",
                "t5xxl": "blurry, low quality, bad anatomy, watermark, text",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
        "4": {
            "inputs": {"width": 1024, "height": 576, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "5": {
            "inputs": {
                "seed": 12345,
                "steps": 16,
                "cfg": 1.0,
                "denoise": 1.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
                "model": ["1", 0],
            },
            "class_type": "KSampler",
        },
        "6": {
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode",
        },
        "7": {
            "inputs": {"filename_prefix": "flux_backend", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    client = factory.get_client("still")
    start_time = datetime.now()
    success = False
    generated_filename = None

    print("\nSubmitting FLUX job...")
    async with client:
        result = await client.post_prompt(wf, "flux_backend_test")
        print(f"Result: {result.get('error', 'OK')}")

        pid = result.get("prompt_id")
        print(f"Prompt ID: {pid}")

        if pid:
            for i in range(45):
                await asyncio.sleep(3)
                history = await client.get_history(pid)

                if pid in history:
                    h = history[pid]
                    outputs = h.get("outputs", {})
                    status = h.get("status_str")
                    print(f"[{i * 3}s] Status: {status}, outputs: {bool(outputs)}")

                    if outputs:
                        for node, out in outputs.items():
                            if "images" in out and out["images"]:
                                generated_filename = out["images"][0].get("filename")
                                print(f"GENERATED: {generated_filename}")
                                success = True
                                break
                        break

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Persist results
    if success and generated_filename:
        async with AsyncSessionLocal() as session:
            asset = MediaAsset(
                id=f"asset-{uuid.uuid4().hex[:8]}",
                organization_id="demo-org",
                project_id=proj_id,
                file_name=generated_filename,
                relative_path=f"output/{generated_filename}",
                canonical_path=f"/home/harliesound/ai/ComfyUI_profiles/image/useroutput/{generated_filename}",
                file_extension=".png",
                asset_type="image",
                content_ref="flux_backend_test",
                status="completed",
                job_id=job_id,
                asset_source="comfyui",
                file_size=0,
            )
            session.add(asset)

            job = await session.get(ProjectJob, job_id)
            job.status = "completed"
            job.completed_at = datetime.now()
            await session.commit()

        print(f"\n[OK] Persisted: {generated_filename}")
    else:
        async with AsyncSessionLocal() as session:
            job = await session.get(ProjectJob, job_id)
            job.status = "failed"
            job.error_message = "Image generation failed or timeout"
            job.completed_at = datetime.now()
            await session.commit()
        print(f"\n[FAIL] Job failed or timeout")

    print(f"Duration: {duration:.1f}s")

    # Final state
    print("\n=== FINAL STATE ===")
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        res = await session.execute(
            select(MediaAsset).where(MediaAsset.project_id == proj_id)
        )
        assets = res.scalars().all()
        print(f"Assets: {len(assets)}")
        for a in assets:
            print(f"  - {a.file_name} -> {a.content_ref}")

        res = await session.execute(
            select(ProjectJob).where(ProjectJob.project_id == proj_id)
        )
        jobs = res.scalars().all()
        print(f"Jobs: {len(jobs)}")
        for j in jobs:
            print(f"  - {j.id}: {j.status}")


if __name__ == "__main__":
    asyncio.run(test_flux_from_backend())
