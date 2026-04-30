import asyncio
import os
import sys

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/debug_flux.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from services.instance_registry import registry
from services.comfyui_client_factory import factory

# Test FLUX workflow with clip_name1/clip_name2
wf_flux = {
    "1": {
        "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
        "class_type": "CheckpointLoaderSimple",
    },
    "2": {
        "inputs": {"text": "test prompt", "clip_name1": "1", "clip_name2": "1"},
        "class_type": "CLIPTextEncode",
    },
    "3": {
        "inputs": {"text": "negative", "clip_name1": "1", "clip_name2": "1"},
        "class_type": "CLIPTextEncode",
    },
    "4": {
        "inputs": {"width": 1344, "height": 768, "batch_size": 1},
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
        "inputs": {"filename_prefix": "flux_debug", "images": ["6", 0]},
        "class_type": "SaveImage",
    },
}


async def test():
    registry.load_config()
    client = factory.get_client("still")

    print("Testing FLUX workflow...")
    async with client:
        result = await client.post_prompt(wf_flux, "flux_debug_test")
        print("Result:", result)


if __name__ == "__main__":
    asyncio.run(test())
