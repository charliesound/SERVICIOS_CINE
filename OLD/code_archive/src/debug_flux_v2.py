import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/debug_flux2.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from services.instance_registry import registry
from services.comfyui_client_factory import factory

# Test FLUX workflow with CLIPTextEncodeFlux node
wf_flux = {
    "1": {
        "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
        "class_type": "CheckpointLoaderSimple",
    },
    "2": {
        "inputs": {
            "clip": ["1", 1],
            "clip_l": "cinematic wide shot, cozy cafe interior, warm light, film still",
            "t5xxl": "cinematic wide shot, cozy cafe interior, warm light, film still",
            "guidance": 3.5,
        },
        "class_type": "CLIPTextEncodeFlux",
    },
    "3": {
        "inputs": {
            "clip": ["1", 1],
            "clip_l": "blurry, low quality, bad anatomy",
            "t5xxl": "blurry, low quality, bad anatomy",
            "guidance": 3.5,
        },
        "class_type": "CLIPTextEncodeFlux",
    },
    "4": {
        "inputs": {"width": 960, "height": 540, "batch_size": 1},
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
    "6": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
    "7": {
        "inputs": {"filename_prefix": "flux_v2", "images": ["6", 0]},
        "class_type": "SaveImage",
    },
}


async def test():
    registry.load_config()
    client = factory.get_client("still")

    print("Testing FLUX with CLIPTextEncodeFlux node...")
    async with client:
        result = await client.post_prompt(wf_flux, "flux_v2_test")
        print("Result:", result)

        if result.get("prompt_id"):
            pid = result["prompt_id"]
            print(f"Prompt ID: {pid}")

            for i in range(30):
                await asyncio.sleep(2)
                history = await client.get_history(pid)
                if pid in history:
                    h = history[pid]
                    outputs = h.get("outputs", {})
                    print(f"Status: {h.get('status_str')}, outputs: {bool(outputs)}")
                    if outputs:
                        for node, out in outputs.items():
                            if "images" in out and out["images"]:
                                print(f"Generated: {out['images'][0]['filename']}")
                                break
                        break


if __name__ == "__main__":
    asyncio.run(test())
