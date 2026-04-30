import asyncio
import os
import sys
import uuid

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/mini_storyboard_v2.db"
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
from services.job_tracking_service import job_tracking_service
from datetime import datetime

SCENES = [
    {
        "num": 1,
        "heading": "INT. CAFE - DIA",
        "positive": "cinematic medium shot, young woman entering a cozy neighborhood cafe in the morning, warm natural sunlight streaming through large front windows, wooden tables, ceramic cups, small plants, subtle bar counter in background, soft golden highlights, realistic cafe atmosphere, intimate independent film style, natural posture, thoughtful expression, shallow depth of field, 35mm film still, gentle contrast, production design details, lived-in interior",
        "negative": "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin, stock photo, flat lighting",
        "prefix": "storyboard_scene_1_cafe",
    },
    {
        "num": 2,
        "heading": "EXT. CALLE - NOCHE",
        "positive": "cinematic wide shot, lone man walking down a rainy city street at night under a yellow umbrella, neon reflections on wet pavement, moody urban atmosphere, deep perspective, strong color contrast, practical lights, subtle silhouettes in distance, tense dramatic feeling, independent thriller aesthetic, realistic rain sheen, film still, high contrast lighting, carefully framed composition, emotionally charged night exterior",
        "negative": "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin, stock photo, flat lighting",
        "prefix": "storyboard_scene_2_street_hero",
    },
    {
        "num": 3,
        "heading": "INT. OFICINA - DIA",
        "positive": "cinematic medium shot, man working intensely at his desk in a modest office during daytime, papers spread across the desk, coffee cup, window side light, focused and slightly tense mood, realistic office production design, muted neutral palette, motivated natural light, shallow depth of field, film still, character-driven composition, quiet dramatic atmosphere, subtle visual storytelling, independent drama aesthetic",
        "negative": "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin, stock photo, flat lighting",
        "prefix": "storyboard_scene_3_office",
    },
]


async def run():
    print("=== INIT ===")
    await init_db()
    registry.load_config()

    print("=== CREATE PROJECT ===")
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="Mini Storyboard V2")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print(f"Project: {proj_id}")

    generated = []

    for scene in SCENES:
        job_id = f"job-v2-scene-{scene['num']}-{uuid.uuid4().hex[:8]}"
        print(f"")
        print(f"=== GENERATING {scene['heading']} ===")

        async with AsyncSessionLocal() as session:
            job = ProjectJob(
                id=job_id,
                organization_id="demo-org",
                project_id=proj_id,
                job_type="render:storyboard",
                status="running",
            )
            session.add(job)
            await session.commit()

        async with AsyncSessionLocal() as session:
            await job_tracking_service.record_project_job_event(
                session,
                job=job,
                event_type="job_created",
                status_from=None,
                status_to="running",
                message=f"Generating {scene['heading']}",
            )
            await session.commit()

        prompt = {
            "1": {
                "inputs": {"ckpt_name": "Realistic_Vision_V2.0.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": scene["positive"], "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": scene["negative"], "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {"width": 960, "height": 540, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": 2000 + scene["num"] * 100,
                    "steps": 16,
                    "cfg": 7.0,
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
                "inputs": {
                    "filename_prefix": scene["prefix"],
                    "images": ["6", 0],
                },
                "class_type": "SaveImage",
            },
        }

        client = factory.get_client("still")
        async with client:
            result = await client.post_prompt(prompt, f"v2_scene_{scene['num']}")
            pid = result.get("prompt_id")
            print(f"Prompt: {pid}")

            if pid:
                for i in range(45):
                    await asyncio.sleep(2)
                    history = await client.get_history(pid)
                    if pid in history:
                        h = history[pid]
                        outputs = h.get("outputs", {})
                        print(
                            f"Status: {h.get('status_str')}, outputs: {bool(outputs)}"
                        )

                        if outputs:
                            for node, out in outputs.items():
                                if "images" in out and out["images"]:
                                    img = out["images"][0]
                                    filename = img.get("filename")
                                    print(f"Generated: {filename}")
                                    generated.append(
                                        {
                                            "scene": scene["num"],
                                            "heading": scene["heading"],
                                            "filename": filename,
                                            "job_id": job_id,
                                        }
                                    )

                                    async with AsyncSessionLocal() as session:
                                        j = await session.get(ProjectJob, job_id)
                                        j.status = "completed"
                                        j.completed_at = datetime.utcnow()
                                        await session.commit()
                                    break
                            break

    print("")
    print("=== PERSIST ASSETS ===")
    for g in generated:
        async with AsyncSessionLocal() as session:
            asset_id = f"asset-{uuid.uuid4().hex[:8]}-{g['filename']}"
            asset = MediaAsset(
                id=asset_id,
                organization_id="demo-org",
                project_id=proj_id,
                file_name=g["filename"],
                relative_path=f"output/{g['filename']}",
                canonical_path=f"/home/harliesound/ai/ComfyUI_profiles/image/useroutput/{g['filename']}",
                file_extension=".png",
                asset_type="image",
                content_ref=f"file://{g['filename']}",
                status="completed",
                job_id=g["job_id"],
                asset_source="comfyui",
                file_size=0,
            )
            session.add(asset)
            await session.commit()
            print(f"Asset: {g['filename']}")

    print("")
    print("=== FINAL STATE ===")
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        res = await session.execute(
            select(MediaAsset).where(MediaAsset.project_id == proj_id)
        )
        assets = res.scalars().all()
        print(f"MediaAssets: {len(assets)}")
        for a in assets:
            print(f"  - {a.file_name}")

        res = await session.execute(
            select(ProjectJob).where(ProjectJob.project_id == proj_id)
        )
        jobs = res.scalars().all()
        print(f"Jobs: {len(jobs)}")
        for j in jobs:
            print(f"  - {j.id}: {j.status}")

    print("")
    print(f"=== GENERATED: {len(generated)} ===")
    for g in generated:
        print(f"  Scene {g['scene']}: {g['filename']}")


if __name__ == "__main__":
    asyncio.run(run())
