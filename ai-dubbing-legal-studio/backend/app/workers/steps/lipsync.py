from app.providers.base import LipSyncInput
from app.providers.mock_lipsync import MockLipSyncProvider
from app.core.config import settings


async def lipsync(video_path: str, audio_path: str) -> dict:
    provider = MockLipSyncProvider()
    if settings.lipsync_provider == "comfyui":
        from app.providers.comfyui_lipsync import ComfyUILipSyncProvider
        provider = ComfyUILipSyncProvider()

    input_data = LipSyncInput(video_path=video_path, audio_path=audio_path)
    output = await provider.process(input_data)

    return {
        "file_path": output.video_path,
        "duration_seconds": output.duration_seconds,
        "provider": output.provider,
        "model_used": output.model_used,
    }
