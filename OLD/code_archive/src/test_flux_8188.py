import asyncio
import aiohttp


async def test_flux_8188():
    """Test FLUX on 8188 (main instance) with clean queue"""

    # Use CheckpointLoaderSimple + CLIPTextEncodeFlux (standard workflow)
    wf = {
        "1": {
            "inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {
                "clip": ["1", 1],
                "clip_l": "cinematic wide shot, cozy cafe interior, warm morning light, wooden tables, film still",
                "t5xxl": "cinematic wide shot, cozy cafe interior, warm morning light, wooden tables, film still",
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
            "inputs": {"filename_prefix": "flux_8188_test", "images": ["6", 0]},
            "class_type": "SaveImage",
        },
    }

    print("=== Testing FLUX on 8188 (main, clean queue) ===")
    print("Workflow: CheckpointLoaderSimple + CLIPTextEncodeFlux + KSampler")

    async with aiohttp.ClientSession() as session:
        # Check VRAM first
        async with session.get("http://localhost:8188/system_stats") as resp:
            stats = await resp.json()
            vram = stats["devices"][0]
            print(
                f"VRAM: {vram['vram_free'] / 1e9:.1f}GB free / {vram['vram_total'] / 1e9:.1f}GB"
            )

        async with session.post(
            "http://localhost:8188/prompt",
            json={"prompt": wf, "prompt_id": "flux_8188"},
        ) as resp:
            result = await resp.json()
            print("Submit result:", result.get("error", "OK"))
            errors = result.get("node_errors", {})
            if errors:
                print("Node errors:", errors)

            if result.get("prompt_id"):
                pid = result["prompt_id"]
                print(f"Prompt ID: {pid}")

                for i in range(45):
                    await asyncio.sleep(3)

                    async with session.get(
                        f"http://localhost:8188/history/{pid}"
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
                    async with session.get("http://localhost:8188/queue") as resp:
                        q = await resp.json()
                        if not q.get("queue_running"):
                            print("Queue empty - job finished")
                            break

                print("TIMEOUT")


asyncio.run(test_flux_8188())
