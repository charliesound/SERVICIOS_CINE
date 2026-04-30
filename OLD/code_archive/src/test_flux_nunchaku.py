import asyncio
import aiohttp


async def test_flux_nunchaku():
    """Test FLUX using NunchakuFluxDiTLoader - FLUX-specific loader"""

    # Nunchaku FLUX workflow - uses proper FLUX loader
    wf = {
        "1": {
            "inputs": {
                "model_path": "flux1-dev-fp8.safetensors",
                "cache_threshold": 0,
                "attention": "nunchaku-fp16",
                "cpu_offload": "auto",
                "device_id": 0,
                "data_type": "bfloat16",
            },
            "class_type": "NunchakuFluxDiTLoader",
        },
        "2": {
            "inputs": {
                "text": "cinematic wide shot, cozy cafe, warm light, film still",
                "clip_name1": "1",
                "clip_name2": "1",
            },
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {
                "text": "blurry, low quality, bad anatomy",
                "clip_name1": "1",
                "clip_name2": "1",
            },
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {"width": 768, "height": 512, "batch_size": 1},
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
            "inputs": {"samples": ["5", 0], "vae": ["1", 1]},
            "class_type": "VAEDecode",
        },
        "7": {
            "inputs": {"filename_prefix": "flux_nunchaku", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    print("=== Testing FLUX with NunchakuFluxDiTLoader ===")
    print("Using Nunchaku FLUX loader (FLUX-specific)")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8191/prompt",
            json={"prompt": wf, "prompt_id": "flux_nunchaku"},
        ) as resp:
            result = await resp.json()
            print("Result:", result)
            print("Errors:", result.get("node_errors", {}))

            if result.get("prompt_id"):
                pid = result["prompt_id"]
                print(f"Prompt ID: {pid}")

                for i in range(45):
                    await asyncio.sleep(3)

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

                    # Check queue
                    async with session.get("http://localhost:8191/queue") as resp:
                        q = await resp.json()
                        if not q.get("queue_running"):
                            print("Queue empty - job finished or failed")
                            break

                print("TIMEOUT or finished")


asyncio.run(test_flux_nunchaku())
