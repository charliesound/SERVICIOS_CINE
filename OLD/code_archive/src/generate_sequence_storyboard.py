import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/sequence_storyboard.db"
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

SEQUENCES = [
    {
        "id": "A",
        "heading": "INT. CAFE - DIA",
        "shots": [
            {
                "beat": "establishing",
                "prompt": "wide shot, cozy neighborhood cafe exterior in morning, warm sunlight, wooden facade, inviting entrance, establishing shot, cinematic film still",
            },
            {
                "beat": "entrance",
                "prompt": "medium shot, young woman entering cafe looking around, natural morning light from windows, thoughtful expression, cinematic composition, realistic style",
            },
            {
                "beat": "interaction",
                "prompt": "medium shot, woman noticing man sitting at corner table, first visual contact, subtle curiosity, natural lighting, film still aesthetic",
            },
            {
                "beat": "establishing_space",
                "prompt": "wide shot, cafe interior atmosphere, morning light through large windows, wooden tables, ceramic cups, warm golden highlights, production design",
            },
        ],
    },
    {
        "id": "B",
        "heading": "EXT. STREET - NOCHE",
        "shots": [
            {
                "beat": "establishing",
                "prompt": "wide shot, rainy city street at night, wet pavement reflections, deep perspective, urban atmosphere, neon lights, cinematic thriller aesthetic",
            },
            {
                "beat": "movement",
                "prompt": "medium shot, lone man walking down street under umbrella, rainy atmosphere, silhouette, realistic rain texture, film still",
            },
            {
                "beat": "insert",
                "prompt": "close-up, wet pavement with neon reflections, raindrops, moody atmospheric detail, cinematic lighting",
            },
        ],
    },
    {
        "id": "C",
        "heading": "INT. OFFICE - DIA",
        "shots": [
            {
                "beat": "establishing",
                "prompt": "medium shot, modest home office interior, desk with papers, window side light, daytime, realistic production design",
            },
            {
                "beat": "insert",
                "prompt": "close-up, scattered papers on desk, coffee cup, focused work atmosphere, character-driven detail",
            },
            {
                "beat": "closing",
                "prompt": "medium shot, man looking toward phone with tension, slight worry, muted neutral palette, quiet dramatic moment",
            },
        ],
    },
]

NEGATIVE = "blurry, low quality, bad anatomy, extra limbs, duplicate, cropped, watermark, text, logo, cartoon, anime, oversaturated, stock photo"

COMFYUI_OUTPUT = "/home/harliesound/ai/ComfyUI_profiles/image/useroutput"


async def run():
    print("=== INIT ===")
    await init_db()
    registry.load_config()

    print("=== CREATE PROJECT ===")
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="Sequence Storyboard Test")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print("Project:", proj_id)

    all_images = []
    global_seed = 7000

    for seq in SEQUENCES:
        seq_id = seq["id"]
        heading = seq["heading"]
        shots = seq["shots"]

        print("")
        print("=== SEQUENCE", seq_id, ":", heading, "===")
        print("Shots:", len(shots))

        for idx, shot in enumerate(shots):
            job_id = "job-seq-" + seq_id + "-shot-" + str(idx + 1)
            print("  Generating shot", idx + 1, ":", shot["beat"])

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

            # Record history
            async with AsyncSessionLocal() as session:
                msg = (
                    "Sequence "
                    + seq_id
                    + ", shot "
                    + str(idx + 1)
                    + ": "
                    + shot["beat"]
                )
                await job_tracking_service.record_project_job_event(
                    session,
                    job=job,
                    event_type="job_created",
                    status_from=None,
                    status_to="running",
                    message=msg,
                )
                await session.commit()

            # Cinematic 960x540
            prompt = {
                "1": {
                    "inputs": {"ckpt_name": "Realistic_Vision_V2.0.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                },
                "2": {
                    "inputs": {
                        "text": shot["prompt"] + ", cinematic film still, 4k",
                        "clip": ["1", 1],
                    },
                    "class_type": "CLIPTextEncode",
                },
                "3": {
                    "inputs": {"text": NEGATIVE, "clip": ["1", 1]},
                    "class_type": "CLIPTextEncode",
                },
                "4": {
                    "inputs": {"width": 960, "height": 540, "batch_size": 1},
                    "class_type": "EmptyLatentImage",
                },
                "5": {
                    "inputs": {
                        "seed": global_seed + idx * 100,
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
                        "images": ["6", 0],
                        "filename_prefix": "seq_" + seq_id + "_shot_" + str(idx + 1),
                    },
                    "class_type": "SaveImage",
                },
            }

            client = factory.get_client("still")
            async with client:
                result = await client.post_prompt(
                    prompt, "seq_" + seq_id + "_" + str(idx + 1)
                )
                pid = result.get("prompt_id")

                if pid:
                    for i in range(45):
                        await asyncio.sleep(2)
                        history = await client.get_history(pid)
                        if pid in history:
                            h = history[pid]
                            status = h.get("status_str")

                            if status == "success" and h.get("outputs"):
                                for node, out in h.get("outputs", {}).items():
                                    if "images" in out and out["images"]:
                                        filename = out["images"][0].get("filename")
                                        print("    Generated:", filename)
                                        all_images.append(
                                            {
                                                "seq": seq_id,
                                                "heading": heading,
                                                "shot": idx + 1,
                                                "beat": shot["beat"],
                                                "filename": filename,
                                                "job_id": job_id,
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
                                print("    FAILED")
                                break

    # Persist all assets
    print("")
    print("=== PERSIST ASSETS ===")
    for img in all_images:
        async with AsyncSessionLocal() as session:
            asset = MediaAsset(
                id="asset-" + img["filename"],
                organization_id="demo-org",
                project_id=proj_id,
                file_name=img["filename"],
                relative_path="output/" + img["filename"],
                canonical_path=COMFYUI_OUTPUT + "/" + img["filename"],
                file_extension=".png",
                asset_type="image",
                content_ref="seq_"
                + img["seq"]
                + "_"
                + img["beat"]
                + "::"
                + img["filename"],
                status="completed",
                job_id=img["job_id"],
                asset_source="comfyui",
                file_size=0,
            )
            session.add(asset)
            await session.commit()

    # Final summary
    print("")
    print("=== SUMMARY ===")
    for seq in SEQUENCES:
        seq_id = seq["id"]
        count = len([i for i in all_images if i["seq"] == seq_id])
        print("Sequence", seq_id, ":", count, "images")

    print("")
    print("TOTAL:", len(all_images), "images")
    for img in all_images:
        print(
            " ", img["seq"], "-", img["shot"], ":", img["beat"], "->", img["filename"]
        )

    print("")
    print("=== COMPLETE ===")


asyncio.run(run())
