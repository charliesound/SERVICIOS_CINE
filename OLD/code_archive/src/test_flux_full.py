import asyncio
import aiohttp


async def test_full_flux():
    """Test complete FLUX pipeline with proper FLUX nodes"""

    # Full FLUX workflow using proper FLUX API
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
            "class_type": "NunchakuFluxDiTLoader",  # MODEL only
        },
        "2": {
            "inputs": {
                "text": "cinematic wide shot of cozy cafe interior, warm morning light streaming through windows, wooden tables, film still",
                "clip": ["1", 0],  # Model, need to find proper CLIP source
                "clip_l": "cinematic wide shot of cozy cafe interior, warm morning light streaming through windows, wooden tables, film still",
                "t5xxl": "cinematic wide shot of cozy cafe interior, warm morning light streaming through windows, wooden tables, film still",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
        "3": {
            "inputs": {
                "text": "",
                "clip": ["1", 0],
                "clip_l": "blurry, low quality, bad anatomy, watermark, text",
                "t5xxl": "blurry, low quality, bad anatomy, watermark, text",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
        "4": {
            "inputs": {"width": 1024, "height": 576, "batch_size": 1},
            "class_type": "EmptyFlux2LatentImage",  # FLUX-specific latent
        },
        "5": {
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent": ["4", 0],
                "seed": 42,
                "steps": 16,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "guidance": 1.0,
            },
            "class_type": "FluxSamplerParams+",
        },
        # Need VAE - let's check if FLUX has built-in or need external
    }

    print("=== Testing full FLUX pipeline ===")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8191/prompt",
            json={"prompt": wf, "prompt_id": "flux_full_test"},
        ) as resp:
            result = await resp.json()
            print("Result:", result.get("error", "OK"))
            if result.get("node_errors"):
                print("Errors:", result["node_errors"])


asyncio.run(test_full_flux())
