import os
import uuid
from app.providers.base import TTSInput
from app.providers.mock_tts import MockTTSProvider
from app.core.config import settings


async def generate_voice(text: str, language: str, voice_id: str = None) -> dict:
    provider = MockTTSProvider()
    if settings.tts_provider != "mock":
        pass

    input_data = TTSInput(text=text, language=language, voice_id=voice_id)
    output = await provider.synthesize(input_data)

    return {
        "file_path": output.audio_path,
        "duration_seconds": output.duration_seconds,
        "provider": output.provider,
        "model_used": output.model_used,
    }
