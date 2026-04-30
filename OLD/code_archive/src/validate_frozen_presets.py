import asyncio
import os
import sys
import json
import uuid
from datetime import datetime
import importlib.util

# Load storyboard_presets module directly
spec = importlib.util.spec_from_file_location(
    "storyboard_presets", "src/config/storyboard_presets.py"
)
storyboard_presets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storyboard_presets)

PRESETS = storyboard_presets.PRESETS
NEGATIVE_PROMPTS = storyboard_presets.NEGATIVE_PROMPTS

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/frozen_presets_test.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database", "config"]):
        del sys.modules[m]

from database import init_db, AsyncSessionLocal
from models.core import Project, ProjectJob
from models.storage import MediaAsset
from services.instance_registry import registry
from services.comfyui_client_factory import factory


async def build_workflow(
    preset_key, sequence_id, shot_order, shot_type, positive_prompt
):
    preset = PRESETS[preset_key]
    neg = NEGATIVE_PROMPTS.get("flux" if "flux" in preset_key else "cinematic", "")

    encoder_node = preset.get("encoder_node", "CLIPTextEncode")
    settings = preset["settings"]

    # Convert sequence_id to numeric for seed (A=1, B=2, etc.)
    seq_num = (
        ord(sequence_id.upper()) - ord("A") + 1
        if isinstance(sequence_id, str)
        else int(sequence_id)
    )
    filename_prefix = f"s{sequence_id}_shot{shot_order}_{preset_key}"

    wf = {
        "1": {
            "inputs": {"ckpt_name": preset["checkpoint"]},
            "class_type": "CheckpointLoaderSimple",
        },
    }

    if encoder_node == "CLIPTextEncodeFlux":
        wf["2"] = {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": positive_prompt,
                "t5xxl": positive_prompt,
                "guidance": settings.get("guidance", 3.5),
            },
            "class_type": "CLIPTextEncodeFlux",
        }
        wf["3"] = {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": neg,
                "t5xxl": neg,
                "guidance": settings.get("guidance", 3.5),
            },
            "class_type": "CLIPTextEncodeFlux",
        }
    else:
        wf["2"] = {
            "inputs": {"text": positive_prompt, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        }
        wf["3"] = {
            "inputs": {"text": neg, "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        }

    wf["4"] = {
        "inputs": {
            "width": settings.get("width", 1024),
            "height": settings.get("height", 576),
            "batch_size": 1,
        },
        "class_type": "EmptyLatentImage",
    }
    wf["5"] = {
        "inputs": {
            "seed": 1000 + seq_num * 100 + int(shot_order) * 10,
            "steps": settings.get("steps", 20),
            "cfg": settings.get("cfg", 7.0),
            "denoise": settings.get("denoise", 1.0),
            "sampler_name": settings.get("sampler_name", "euler"),
            "scheduler": settings.get("scheduler", "normal"),
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
        "inputs": {"filename_prefix": filename_prefix, "images": ["6", 0]},
        "class_type": "SaveImage",
    }

    return wf, filename_prefix


async def test_preset(preset_key, sequence_id, shot_order, shot_type, prompt):
    print(f"\n--- Testing {preset_key} ---")

    preset = PRESETS[preset_key]
    wf, filename_prefix = await build_workflow(
        preset_key, sequence_id, shot_order, shot_type, prompt
    )

    client = factory.get_client(preset["target_instance"])
    success = False
    filename = None

    # FLUX needs longer timeout due to model loading
    max_iterations = 60 if "flux" in preset_key else 30

    async with client:
        result = await client.post_prompt(wf, filename_prefix)
        pid = result.get("prompt_id")
        print(f"  Prompt: {pid}")

        if pid:
            for i in range(max_iterations):
                await asyncio.sleep(2)
                history = await client.get_history(pid)
                if pid in history:
                    h = history[pid]
                    outputs = h.get("outputs", {})
                    if outputs:
                        for node, out in outputs.items():
                            if "images" in out and out["images"]:
                                filename = out["images"][0]["filename"]
                                print(f"  Generated: {filename}")
                                success = True
                                break
                        break

    return success, filename, preset["role"]


async def run():
    await init_db()
    registry.load_config()

    print("=" * 60)
    print("FROZEN PRESETS VALIDATION")
    print("=" * 60)

    # Create project
    async with AsyncSessionLocal() as session:
        proj = Project(organization_id="demo-org", name="Frozen Presets Test")
        session.add(proj)
        await session.commit()
        proj_id = proj.id
        print(f"Project: {proj_id}")

    test_cases = [
        (
            "storyboard_realistic",
            "A",
            1,
            "establishing",
            "cinematic wide shot, cozy cafe interior, warm morning light",
        ),
        (
            "storyboard_realistic",
            "A",
            2,
            "medium",
            "cinematic medium shot, woman enters cafe, looks around",
        ),
        (
            "storyboard_cinematic_premium",
            "B",
            1,
            "establishing",
            "cinematic wide shot, rainy city street at night, neon lights",
        ),
        (
            "storyboard_cinematic_premium",
            "B",
            2,
            "movement",
            "cinematic medium shot, man walks under umbrella, rain-soaked street",
        ),
    ]

    results = []

    for preset_key, seq_id, shot_order, shot_type, prompt in test_cases:
        job_id = f"job-{preset_key}-{seq_id}-{shot_order}-{uuid.uuid4().hex[:6]}"

        # Create job with metadata
        async with AsyncSessionLocal() as session:
            job = ProjectJob(
                id=job_id,
                organization_id="demo-org",
                project_id=proj_id,
                job_type="render:storyboard",
                status="running",
                result_data=json.dumps(
                    {
                        "preset": preset_key,
                        "sequence_id": seq_id,
                        "shot_order": shot_order,
                        "shot_type": shot_type,
                        "visual_mode": "realistic"
                        if "realistic" in preset_key
                        else "flux",
                    }
                ),
            )
            session.add(job)
            await session.commit()

        # Run generation
        success, filename, role = await test_preset(
            preset_key, seq_id, shot_order, shot_type, prompt
        )

        # Persist asset with metadata
        if success and filename:
            metadata = {
                "sequence_id": seq_id,
                "shot_order": shot_order,
                "shot_type": shot_type,
                "visual_mode": "realistic" if "realistic" in preset_key else "flux",
                "preset_role": role,
                "prompt_summary": prompt[:100],
            }

            async with AsyncSessionLocal() as session:
                asset = MediaAsset(
                    id=f"asset-{uuid.uuid4().hex[:8]}",
                    organization_id="demo-org",
                    project_id=proj_id,
                    file_name=filename,
                    relative_path=f"output/{filename}",
                    canonical_path=f"/home/harliesound/ai/ComfyUI_profiles/image/useroutput/{filename}",
                    file_extension=".png",
                    asset_type="image",
                    content_ref=f"storyboard::{seq_id}::{shot_order}::{preset_key}",
                    metadata_json=json.dumps(metadata),
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

            print(f"  [OK] Persisted with metadata")
        else:
            async with AsyncSessionLocal() as session:
                job = await session.get(ProjectJob, job_id)
                job.status = "failed"
                job.completed_at = datetime.now()
                await session.commit()
            print(f"  [FAIL] Job failed")

        results.append(
            {
                "preset": preset_key,
                "sequence": seq_id,
                "shot": shot_order,
                "success": success,
                "filename": filename,
            }
        )

    # Final state
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for r in results:
        status = "[OK]" if r["success"] else "[FAIL]"
        print(
            f"{status} {r['preset']} | Seq {r['sequence']} | Shot {r['shot']} | {r['filename']}"
        )

    # Verify metadata in DB
    print("\n" + "=" * 60)
    print("METADATA VERIFICATION")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        from sqlalchemy import select

        res = await session.execute(
            select(MediaAsset).where(MediaAsset.project_id == proj_id)
        )
        assets = res.scalars().all()

        for a in assets:
            meta = json.loads(a.metadata_json or "{}")
            print(f"  {a.file_name}")
            print(f"    sequence_id: {meta.get('sequence_id')}")
            print(f"    shot_order: {meta.get('shot_order')}")
            print(f"    visual_mode: {meta.get('visual_mode')}")
            print(f"    content_ref: {a.content_ref}")

    success_count = sum(1 for r in results if r["success"])
    print(f"\nTotal: {success_count}/{len(results)} passed")


if __name__ == "__main__":
    asyncio.run(run())
