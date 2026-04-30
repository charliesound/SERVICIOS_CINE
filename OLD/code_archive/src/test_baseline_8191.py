import asyncio
import aiohttp


async def test_baseline():
    """Test Realistic_Vision on 8191 to verify instance is functional"""

    wf = {
        "1": {
            "inputs": {"ckpt_name": "Realistic_Vision_V2.0.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {"text": "test prompt", "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {"text": "blurry", "clip": ["1", 1]},
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        },
        "5": {
            "inputs": {
                "seed": 42,
                "steps": 10,
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
            "inputs": {"filename_prefix": "test_baseline", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    print("=== Testing Realistic_Vision on 8191 ===")
    print("Submitting...")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8191/prompt",
            json={"prompt": wf, "prompt_id": "test_baseline"},
        ) as resp:
            result = await resp.json()
            print("Result:", result)

            if result.get("prompt_id"):
                pid = result["prompt_id"]

                for i in range(30):
                    await asyncio.sleep(2)

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


asyncio.run(test_baseline())
