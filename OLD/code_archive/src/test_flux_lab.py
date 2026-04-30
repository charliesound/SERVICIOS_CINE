import asyncio
import os
import sys
import aiohttp

os.environ["DATABASE_URL"] = (
    "sqlite+aiosqlite:///C:/Users/Charliesound/AppData/Local/flux_lab_test.db"
)
os.environ["QUEUE_PERSISTENCE_MODE"] = "memory"

for m in list(sys.modules.keys()):
    if any(x in m for x in ["services", "models", "database"]):
        del sys.modules[m]

from services.instance_registry import registry
from services.comfyui_client_factory import factory

# Easy FLUX workflow using easy-use nodes
wf_easy_flux = {
    "1": {
        "inputs": {
            "ckpt_name": "FLUX/flux1-schnell-fp8.safetensors",
            "vae_name": "Baked VAE",
            "lora_name": "None",
            "lora_model_strength": 1.0,
            "lora_clip_strength": 1.0,
            "resolution": "1344 x 768",
            "empty_latent_width": 1344,
            "empty_latent_height": 768,
            "positive": "cinematic wide shot, cozy cafe interior, warm light, film still, high quality",
            "batch_size": 1,
        },
        "class_type": "easy fluxLoader",
    },
    "2": {
        "inputs": {
            "pipe": ["1", 0],
            "seed": 42,
            "steps": 16,
            "cfg": 1.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
            "image_output": "Save",
            "link_id": 0,
            "save_prefix": "flux_lab_test",
        },
        "class_type": "easy kSampler",
    },
}


async def test_lab():
    registry.load_config()

    print("=== Testing FLUX on port 8191 (lab) ===")
    print("VRAM available: ~30GB")

    async with aiohttp.ClientSession() as session:
        # Check queue first
        async with session.get("http://localhost:8191/queue") as resp:
            queue = await resp.json()
            print(f"Queue running: {len(queue.get('queue_running', []))}")
            print(f"Queue pending: {len(queue.get('queue_pending', []))}")

    # Use lab instance
    client = factory.get_client("lab")

    print("\nSubmitting FLUX job to lab...")
    async with client:
        result = await client.post_prompt(wf_easy_flux, "flux_lab_test")
        print("Result:", result)

        if result.get("prompt_id"):
            pid = result["prompt_id"]
            print(f"Prompt ID: {pid}")

            for i in range(60):
                await asyncio.sleep(2)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:8191/history/{pid}"
                    ) as resp:
                        h = await resp.json()

                if pid in h:
                    data = h[pid]
                    outputs = data.get("outputs", {})
                    status = data.get("status_str")
                    print(f"[{i * 2}s] Status: {status}, outputs: {bool(outputs)}")

                    if outputs:
                        for node, out in outputs.items():
                            if "images" in out and out["images"]:
                                print(f"GENERATED: {out['images'][0]['filename']}")
                                return
                    break

                # Check queue
                async with aiohttp.ClientSession() as session:
                    async with session.get("http://localhost:8191/queue") as resp:
                        queue = await resp.json()
                        running = queue.get("queue_running", [])
                        if not running:
                            print("Queue empty - job may have failed silently")
            else:
                print("TIMEOUT after 120s")


if __name__ == "__main__":
    asyncio.run(test_lab())
