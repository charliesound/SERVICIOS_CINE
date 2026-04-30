import asyncio
import os
import sys
import aiohttp

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/flux_simple_test.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from services.instance_registry import registry
from services.comfyui_client_factory import factory

# Simple FLUX workflow - no LoRA, minimal nodes
# Use standard CheckpointLoader + CLIPTextEncodeFlux + KSampler
wf_simple_flux = {
    "1": {
        "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
        "class_type": "CheckpointLoaderSimple",
    },
    "2": {
        "inputs": {
            "clip": ["1", 1],  # CLIP output from checkpoint
            "clip_l": "cinematic wide shot of a cozy cafe interior, warm morning light, film still",
            "t5xxl": "cinematic wide shot of a cozy cafe interior, warm morning light, film still",
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
            "seed": 42,
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
        "inputs": {"filename_prefix": "flux_simple", "images": ["6", 0]},
        "class_type": "SaveImage",
    },
}


async def test_simple():
    registry.load_config()

    print("=== Testing SIMPLE FLUX workflow on port 8191 ===")
    print("Using: CheckpointLoaderSimple + CLIPTextEncodeFlux + KSampler")

    client = factory.get_client("lab")

    print("\nSubmitting...")
    async with client:
        result = await client.post_prompt(wf_simple_flux, "flux_simple_test")
        print("Result:", result)

        if result.get("prompt_id"):
            pid = result["prompt_id"]
            print(f"Prompt ID: {pid}")

            for i in range(45):
                await asyncio.sleep(3)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:8191/history/{pid}"
                    ) as resp:
                        h = await resp.json()

                if pid in h:
                    data = h[pid]
                    outputs = data.get("outputs", {})
                    status = data.get("status_str")
                    print(f"[{i * 3}s] Status: {status}, outputs: {bool(outputs)}")

                    if outputs:
                        for node, out in outputs.items():
                            if "images" in out and out["images"]:
                                print(f"GENERATED: {out['images'][0]['filename']}")
                                return
                else:
                    print(f"[{i * 3}s] Not in history yet")

            print("TIMEOUT")


if __name__ == "__main__":
    asyncio.run(test_simple())
