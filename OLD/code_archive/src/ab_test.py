import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/ab_test.db"
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
from datetime import datetime

TEST_CASES = [
    {
        "id": "FLUX_1",
        "model": "Realistic_Vision_V2.0.safetensors",
        "prompt": "cinematic wide shot, rainy city street at night, wet pavement reflections, neon lights, urban atmosphere, film still, 4k",
        "width": 960,
        "height": 540,
        "seed": 8001,
        "steps": 16,
        "cfg": 7.0,
    },
    {
        "id": "FLUX_2",
        "model": "Realistic_Vision_V2.0.safetensors",
        "prompt": "cinematic medium shot, man working at desk office, papers, coffee cup, window light, dramatic moment, film still, 4k",
        "width": 960,
        "height": 540,
        "seed": 8002,
        "steps": 16,
        "cfg": 7.0,
    },
]

NEGATIVE = "blurry, low quality, bad anatomy, extra limbs, duplicate, cropped, watermark, text, logo, cartoon"

COMFYUI_OUTPUT = "/home/harliesound/ai/ComfyUI_profiles/image/useroutput"


async def run():
    print("=== A/B TEST INIT ===")
    await init_db()
    registry.load_config()

    print("=== CREATE PROJECT ===")
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="A/B Test Juggernaut")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print("Project:", proj_id)

    results = []

    for tc in TEST_CASES:
        job_id = "job-" + tc["id"]
        print("")
        print("===", tc["id"], "===")
        print("Model:", tc["model"])

        # Create job
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

        # Generate
        prompt = {
            "1": {
                "inputs": {"ckpt_name": tc["model"]},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": tc["prompt"], "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": NEGATIVE, "clip": ["1", 1]},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {
                    "width": tc["width"],
                    "height": tc["height"],
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": tc["seed"],
                    "steps": tc["steps"],
                    "cfg": tc["cfg"],
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
                "inputs": {"images": ["6", 0], "filename_prefix": tc["id"].lower()},
                "class_type": "SaveImage",
            },
        }

        client = factory.get_client("still")
        async with client:
            start = datetime.utcnow()
            result = await client.post_prompt(prompt, tc["id"])
            pid = result.get("prompt_id")
            print("Prompt:", pid)

            if pid:
                for i in range(45):
                    await asyncio.sleep(2)
                    history = await client.get_history(pid)
                    if pid in history:
                        h = history[pid]
                        status = h.get("status_str")
                        elapsed = (datetime.utcnow() - start).total_seconds()
                        print("Status:", status, f"({elapsed:.0f}s)")

                        if status == "success" and h.get("outputs"):
                            for node, out in h.get("outputs", {}).items():
                                if "images" in out and out["images"]:
                                    filename = out["images"][0].get("filename")
                                    print("Generated:", filename)
                                    results.append(
                                        {
                                            "id": tc["id"],
                                            "model": tc["model"],
                                            "filename": filename,
                                            "job_id": job_id,
                                            "time": elapsed,
                                        }
                                    )

                                    # Mark job complete
                                    async with AsyncSessionLocal() as session:
                                        j = await session.get(ProjectJob, job_id)
                                        j.status = "completed"
                                        j.completed_at = datetime.utcnow()
                                        await session.commit()
                                    break
                        elif status == "failed":
                            print("FAILED")
                            break

    # Persist assets
    print("")
    print("=== PERSIST ===")
    for r in results:
        async with AsyncSessionLocal() as session:
            asset = MediaAsset(
                id="asset-" + r["filename"],
                organization_id="demo-org",
                project_id=proj_id,
                file_name=r["filename"],
                relative_path="output/" + r["filename"],
                canonical_path=COMFYUI_OUTPUT + "/" + r["filename"],
                file_extension=".png",
                asset_type="image",
                content_ref=r["id"] + "::" + r["filename"],
                status="completed",
                job_id=r["job_id"],
                asset_source="comfyui",
                file_size=0,
            )
            session.add(asset)
            await session.commit()

    print("")
    print("=== RESULTS ===")
    for r in results:
        print(r["id"], "-", r["model"], "-", r["filename"], "-", r["time"], "s")

    print("")
    print("=== DONE ===")


asyncio.run(run())
