import asyncio
import aiohttp


async def test_flux_direct():
    wf = {
        "1": {
            "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": "test prompt",
                "t5xxl": "test prompt",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
        "3": {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": "blurry",
                "t5xxl": "blurry",
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
            "inputs": {"filename_prefix": "test_flux_debug", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    print("Testing FLUX directly...")
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8188/prompt",
            json={"prompt": wf, "prompt_id": "flux_debug"},
        ) as resp:
            result = await resp.json()
            print("Result:", result.get("error", "OK"))
            if result.get("node_errors"):
                print("Errors:", result["node_errors"])
            if result.get("prompt_id"):
                pid = result["prompt_id"]
                print(f"Prompt: {pid}")

                for i in range(30):
                    await asyncio.sleep(2)
                    async with session.get(
                        f"http://localhost:8188/history/{pid}"
                    ) as resp:
                        h = await resp.json()
                    if pid in h and h[pid].get("outputs"):
                        print(f"Generated: {h[pid]['outputs']}")
                        return


asyncio.run(test_flux_direct())
