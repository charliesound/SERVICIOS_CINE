import asyncio
import os
import sys
import uuid
import json
from datetime import datetime

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/ab_comparison.db"
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

WIDTH = 1344
HEIGHT = 768
NEG = "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin, stock photo, flat lighting"

SHOTS = [
    # SECUENCIA A
    {
        "id": "A1",
        "seq": "A",
        "shot": "establishing",
        "prompt": "cinematic wide shot, cozy neighborhood cafe interior in the morning, warm natural light entering through large windows, wooden tables, cups, subtle bar counter, intimate independent film atmosphere, realistic production design, clear spatial composition, storyboard readability, gentle contrast",
    },
    {
        "id": "A2",
        "seq": "A",
        "shot": "interaction",
        "prompt": "cinematic medium shot, woman entering and noticing the interior of a cozy cafe, warm daylight, natural body language, quiet morning atmosphere, realistic café setting, subtle depth of field, film still composition, storyboard clarity, emotional realism",
    },
    # SECUENCIA B
    {
        "id": "B1",
        "seq": "B",
        "shot": "establishing",
        "prompt": "cinematic wide shot, rainy city street at night, neon reflections on wet pavement, lone figure under umbrella, deep perspective, dramatic urban mood, practical lights, strong atmosphere, clear storyboard composition, visual storytelling",
    },
    {
        "id": "B2",
        "seq": "B",
        "shot": "movement",
        "prompt": "cinematic medium-wide shot, man walking through a rain-soaked street at night under an umbrella, motion implied, glowing reflections on the ground, tense dramatic atmosphere, urban loneliness, readable film blocking, storyboard style frame",
    },
]

MOTORS = {
    "baseline": {
        "name": "Baseline Realistic",
        "checkpoint": "Realistic_Vision_V2.0.safetensors",
        "instance": "still",
        "steps": 20,
        "cfg": 7.0,
    },
    "flux2": {
        "name": "FLUX2 Schnell",
        "checkpoint": "FLUX/flux1-schnell-fp8.safetensors",
        "instance": "still",
        "steps": 16,
        "cfg": 1.0,
        "flux_api": True,
    },
    "krea": {
        "name": "FLUX Krea Dev",
        "checkpoint": "FLUX/flux1-dev-fp8.safetensors",
        "instance": "still",
        "steps": 16,
        "cfg": 1.0,
        "flux_api": True,
    },
}


def build_workflow(checkpoint, positive, negative, steps, cfg, flux_api=False, seed=42):
    wf = {
        "1": {
            "inputs": {"ckpt_name": checkpoint},
            "class_type": "CheckpointLoaderSimple",
        },
    }

    if flux_api:
        wf["2"] = {
            "inputs": {"text": positive, "clip_name1": "1", "clip_name2": "1"},
            "class_type": "CLIPTextEncode",
        }
        wf["3"] = {
            "inputs": {"text": negative, "clip_name1": "1", "clip_name2": "1"},
            "class_type": "CLIPTextEncode",
        }
    else:
        wf["2"] = {
            "inputs": {"text": positive, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        }
        wf["3"] = {
            "inputs": {"text": negative, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        }

    wf["4"] = {
        "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1},
        "class_type": "EmptyLatentImage",
    }
    wf["5"] = {
        "inputs": {
            "seed": seed,
            "steps": steps,
            "cfg": cfg,
            "denoise": 1.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "positive": ["2", 0],
            "negative": ["3", 0],
            "latent_image": ["4", 0],
            "model": ["1", 0],
        },
        "class_type": "KSampler",
    }
    wf["6"] = {
        "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
        "class_type": "VAEDecode",
    }
    wf["7"] = {
        "inputs": {"filename_prefix": "ab_test", "images": ["6", 0]},
        "class_type": "SaveImage",
    }

    return wf


async def run():
    await init_db()
    registry.load_config()

    print("=" * 60)
    print("COMPARATIVA: 3 MOTORES DE STORYBOARD")
    print(f"Resolución: {WIDTH}x{HEIGHT}")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="AB Storyboard Comparison")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print(f"\nProject: {proj_id}")

    results = []

    for motor_key, motor_cfg in MOTORS.items():
        print(f"\n{'=' * 50}")
        print(f"MOTOR: {motor_cfg['name']} ({motor_key})")
        print(f"Checkpoint: {motor_cfg['checkpoint']}")
        print(f"{'=' * 50}")

        for shot in SHOTS:
            job_id = f"job-{motor_key}-{shot['id']}-{uuid.uuid4().hex[:6]}"
            filename_prefix = f"ab_{motor_key}_seq{shot['seq']}_shot{shot['shot']}"

            print(f"\n--- {shot['id']} ({motor_key}) ---")

            async with AsyncSessionLocal() as session:
                job = ProjectJob(
                    id=job_id,
                    organization_id="demo-org",
                    project_id=proj_id,
                    job_type="render:storyboard_ab",
                    status="running",
                    result_data=json.dumps({"motor": motor_key, "shot": shot["id"]}),
                )
                session.add(job)
                await session.commit()

            wf = build_workflow(
                motor_cfg["checkpoint"],
                shot["prompt"],
                NEG,
                motor_cfg["steps"],
                motor_cfg["cfg"],
                flux_api=motor_cfg.get("flux_api", False),
                seed=1000 + int(shot["id"][1]) * 100 + int(shot["id"][-1]) * 10,
            )
            wf["7"]["inputs"]["filename_prefix"] = filename_prefix

            client = factory.get_client(motor_cfg["instance"])
            start_time = datetime.now()
            success = False
            generated_filename = None

            try:
                async with client:
                    result = await client.post_prompt(wf, filename_prefix)
                    pid = result.get("prompt_id")
                    print(f"  Prompt ID: {pid}")

                    if pid:
                        for i in range(60):
                            await asyncio.sleep(2)
                            history = await client.get_history(pid)
                            if pid in history:
                                h = history[pid]
                                outputs = h.get("outputs", {})
                                if outputs:
                                    for node, out in outputs.items():
                                        if "images" in out and out["images"]:
                                            generated_filename = out["images"][0].get(
                                                "filename"
                                            )
                                            print(f"  Generated: {generated_filename}")
                                            success = True
                                            break
                                    break

                        if not generated_filename:
                            print("  TIMEOUT: No image generated")
                    else:
                        print("  ERROR: No prompt_id returned")
            except Exception as e:
                print(f"  EXCEPTION: {str(e)[:100]}")

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

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
                        content_ref=f"ab_test::{motor_key}::{shot['id']}",
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

                print(f"  [OK] Persisted: {generated_filename}")
            else:
                async with AsyncSessionLocal() as session:
                    job = await session.get(ProjectJob, job_id)
                    job.status = "failed"
                    job.error_message = "Image generation failed or timeout"
                    job.completed_at = datetime.now()
                    await session.commit()

            results.append(
                {
                    "motor": motor_key,
                    "shot_id": shot["id"],
                    "success": success,
                    "filename": generated_filename,
                    "duration": duration,
                }
            )

            print(f"  Duration: {duration:.1f}s")

    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)

    for motor_key in MOTORS.keys():
        motor_results = [r for r in results if r["motor"] == motor_key]
        success_count = sum(1 for r in motor_results if r["success"])
        total = len(motor_results)
        avg_time = (
            sum(r["duration"] for r in motor_results) / len(motor_results)
            if motor_results
            else 0
        )
        print(f"\n{motor_key.upper()}:")
        print(f"  Success: {success_count}/{total}")
        print(f"  Avg time: {avg_time:.1f}s")
        for r in motor_results:
            status = "[OK]" if r["success"] else "[FAIL]"
            print(f"    {status} {r['shot_id']}: {r['filename'] or 'FAILED'}")

    print("\n" + "=" * 60)
    print("JOBS CREADOS")
    print("=" * 60)
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        res = await session.execute(
            select(ProjectJob).where(ProjectJob.project_id == proj_id)
        )
        jobs = res.scalars().all()
        for j in jobs:
            print(f"  {j.id}: {j.status}")

    print("\n" + "=" * 60)
    print("ASSETS CREADOS")
    print("=" * 60)
    async with AsyncSessionLocal() as session:
        res = await session.execute(
            select(MediaAsset).where(MediaAsset.project_id == proj_id)
        )
        assets = res.scalars().all()
        for a in assets:
            print(f"  {a.file_name} -> {a.content_ref}")


if __name__ == "__main__":
    asyncio.run(run())
