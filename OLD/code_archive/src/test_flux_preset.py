import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/flux_preset_test.db"
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

# FLUX workflow - uses clip_name1 and clip_name2 instead of just 'clip'
CHECKPOINT = "FLUX/flux1-schnell-fp8.safetensors"
WIDTH, HEIGHT = 960, 540
STEPS = 16
CFG = 1.0  # FLUX uses CFG=1 typically

TESTS = [
    ("flux_test_1", "cinematic wide shot, cozy cafe interior, warm light, film still"),
    (
        "flux_test_2",
        "cinematic medium shot, man at desk, dramatic lighting, film still",
    ),
]

NEG = "blurry, low quality, bad anatomy, watermark, text, cartoon"

COMFYUI_OUT = "/home/harliesound/ai/ComfyUI_profiles/image/useroutput"


async def run():
    await init_db()
    registry.load_config()

    print("=== FLUX PRESET TEST ===")

    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="FLUX Preset Test")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print("Project:", proj_id)

    for name, prompt in TESTS:
        job_id = "job-" + name
        print("")
        print("===", name, "===")

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

        # FLUX workflow - dual CLIP inputs
        wf = {
            "1": {
                "inputs": {"ckpt_name": CHECKPOINT},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {
                    "text": prompt + ", cinematic film still",
                    "clip_name1": "1",
                    "clip_name2": "1",
                },
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {"text": NEG, "clip_name1": "1", "clip_name2": "1"},
                "class_type": "CLIPTextEncode",
            },
            "4": {
                "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": 10000,
                    "steps": STEPS,
                    "cfg": CFG,
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
                "inputs": {"images": ["6", 0], "filename_prefix": "flux_" + name},
                "class_type": "SaveImage",
            },
        }

        client = factory.get_client("still")
        async with client:
            start = datetime.utcnow()
            result = await client.post_prompt(wf, name)
            pid = result.get("prompt_id")
            print("Prompt:", pid)

            if pid:
                for i in range(45):
                    await asyncio.sleep(2)
                    h = await client.get_history(pid)
                    if pid in h:
                        status = h[pid].get("status_str")
                        elapsed = (datetime.utcnow() - start).total_seconds()
                        print("Status:", status, f"({elapsed:.0f}s)")

                        if status == "success" and h[pid].get("outputs"):
                            for node, out in h[pid]["outputs"].items():
                                if "images" in out and out["images"]:
                                    fn = out["images"][0].get("filename")
                                    print("Generated:", fn)

                                    async with AsyncSessionLocal() as session:
                                        j = await session.get(ProjectJob, job_id)
                                        j.status = "completed"
                                        j.completed_at = datetime.utcnow()
                                        await session.commit()

                                    async with AsyncSessionLocal() as session:
                                        a = MediaAsset(
                                            id="asset-" + fn,
                                            organization_id="demo-org",
                                            project_id=proj_id,
                                            file_name=fn,
                                            relative_path="output/" + fn,
                                            canonical_path=COMFYUI_OUT + "/" + fn,
                                            file_extension=".png",
                                            asset_type="image",
                                            content_ref="flux_cinematic::" + fn,
                                            status="completed",
                                            job_id=job_id,
                                            asset_source="comfyui",
                                            file_size=0,
                                        )
                                        session.add(a)
                                        await session.commit()
                                    print("Asset persisted")
                        elif status == "failed":
                            print("FAILED")
                        break

    print("")
    print("=== FLUX TEST COMPLETE ===")


asyncio.run(run())
