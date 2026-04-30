import asyncio
import aiohttp


async def test_flux_dev():
    """Test FLUX using flux1-dev-fp8 (available in Nunchaku)"""

    # Check available flux models in Nunchaku
    # flux1-dev-fp8 should work

    # Try using proper FLUX clip encode
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
        # FLUX requires special clip handling - check for dual clip loader
        "2": {
            "inputs": {
                "text": "cinematic wide shot, cozy cafe, warm light, film still",
                "clip": ["1", 0],  # Nunchaku outputs only MODEL, not CLIP
                "clip_l": "cinematic wide shot, cozy cafe, warm light, film still",
                "t5xxl": "cinematic wide shot, cozy cafe, warm light, film still",
                "guidance": 3.5,
            },
            "class_type": "CLIPTextEncodeFlux",
        },
    }

    print("=== Testing FLUX dev with Nunchaku + CLIPTextEncodeFlux ===")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8191/prompt",
            json={"prompt": wf, "prompt_id": "flux_dev_test"},
        ) as resp:
            result = await resp.json()
            print("Result:", result)
            print("Errors:", result.get("node_errors", {}))


asyncio.run(test_flux_dev())
