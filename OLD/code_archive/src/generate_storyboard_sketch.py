import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/storyboard_sketch.db"
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

SCENES = [
    {
        "num": 1,
        "heading": "INT. CAFE - DIA",
        "positive": "hand-drawn cinematic storyboard, young woman entering cafe, monochrome sketch style, strong line work, clear silhouette, film blocking readability, concept art aesthetic, loose pencil texture, minimal detail, storyboard frame, 2d artwork, simple shading",
        "negative": "blurry, oversaturated, cartoon, anime style, flat color, fully rendered, photorealistic, digital art, 3d render",
        "prefix": "sketch_scene_1_cafe",
    },
    {
        "num": 2,
        "heading": "EXT. CALLE - NOCHE",
        "positive": "hand-drawn cinematic storyboard, man with umbrella walking city street night, monochrome sketch style, strong silhouette, rough line work, film blocking readability, concept art aesthetic, urban atmosphere, storyboard frame, 2d artwork, simple shading, dramatic composition",
        "negative": "blurry, oversaturated, cartoon, anime style, flat color, fully rendered, photorealistic, digital art, 3d render",
        "prefix": "sketch_scene_2_street",
    },
    {
        "num": 3,
        "heading": "INT. OFICINA - DIA",
        "positive": "hand-drawn cinematic storyboard, man working at desk office, monochrome sketch style, strong line work, clear silhouette, film blocking readability, concept art aesthetic, loose pencil texture, minimal detail, storyboard frame, 2d artwork, simple shading, character focus",
        "negative": "blurry, oversaturated, cartoon, anime style, flat color, fully rendered, photorealistic, digital art, 3d render",
        "prefix": "sketch_scene_3_office",
    },
]


async def run():
    print("=== INIT SKETCH ===")
    await init_db()
    registry.load_config()

    print("=== CREATE PROJECT ===")
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="Storyboard Sketch")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print(f"Project: {proj_id}")

    generated = []

    for scene in SCENES:
        job_id = f"job-sketch-scene-{scene['num']}"
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

        # Sketch: simpler workflow, 512x512
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
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "5": {
                "inputs": {
                    "seed": 5000 + scene["num"] * 100,
                    "steps": 12,
                    "cfg": 6.0,
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
                "inputs": {"images": ["6", 0], "filename_prefix": scene["prefix"]},
                "class_type": "SaveImage",
            },
        }

        client = factory.get_client("lab")
        async with client:
            result = await client.post_prompt(prompt, f"sketch_{scene['num']}")
            pid = result.get("prompt_id")
            print(f"Prompt: {pid}")

            if pid:
                for i in range(45):
                    await asyncio.sleep(2)
                    history = await client.get_history(pid)
                    if pid in history:
                        h = history[pid]
                        status = h.get("status_str")
                        print(f"Status: {status}")

                        if status == "success" and h.get("outputs"):
                            for node, out in h.get("outputs", {}).items():
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
                        elif status == "failed":
                            print("FAILED")
                            break

    # Persist assets
    print("")
    print("=== PERSIST ASSETS ===")
    for g in generated:
        async with AsyncSessionLocal() as session:
            asset = MediaAsset(
                id=f"asset-{g['filename']}",
                organization_id="demo-org",
                project_id=proj_id,
                file_name=g["filename"],
                relative_path=f"output/{g['filename']}",
                canonical_path=f"/home/harliesound/ai/ComfyUI_profiles/restoration/useroutput/{g['filename']}",
                file_extension=".png",
                asset_type="image",
                content_ref=f"sketch://{g['filename']}",
                status="completed",
                job_id=g["job_id"],
                asset_source="comfyui",
                file_size=0,
            )
            session.add(asset)
            await session.commit()
            print(f"Asset: {g['filename']}")

    print("")
    print(f"=== SKETCH COMPLETE: {len(generated)} ===")
    for g in generated:
        print(f"  Scene {g['scene']}: {g['filename']}")


asyncio.run(run())
