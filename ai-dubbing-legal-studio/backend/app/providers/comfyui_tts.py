import os
import uuid
from typing import Optional
from app.providers.base import BaseTTSProvider, TTSInput, TTSOutput
from app.providers.comfy_client import ComfyClient
from app.core.config import settings


class ComfyUITTSProvider(BaseTTSProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.comfyui_dubbing

    async def synthesize(self, input_data: TTSInput) -> TTSOutput:
        client = ComfyClient(base_url=self.base_url)
        try:
            filename_prefix = f"tts_{uuid.uuid4().hex[:8]}"
            workflow = {
                "1": {
                    "class_type": "TextToSpeechNode",
                    "inputs": {
                        "text": input_data.text,
                        "language": input_data.language,
                        "speed": input_data.speed,
                    },
                },
                "2": {
                    "class_type": "SaveAudio",
                    "inputs": {
                        "audio": ["1", 0],
                        "filename_prefix": filename_prefix,
                    },
                },
            }

            result = await client.submit_and_wait(workflow, timeout=120)
            outputs = result["outputs"]
            audio_files = outputs.get("audio", []) or outputs.get("files", [])

            if audio_files:
                output_path = os.path.join(
                    settings.storage_local_path, "tts",
                    audio_files[0]["filename"]
                )
            else:
                output_path = os.path.join(settings.storage_local_path, "tts", f"{filename_prefix}.wav")

            return TTSOutput(
                audio_path=output_path,
                duration_seconds=0.0,
                provider="comfyui",
                model_used="TextToSpeechNode",
            )
        finally:
            await client.close()


class ComfyUIVoiceCloneProvider(BaseTTSProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.comfyui_dubbing

    async def synthesize(self, input_data: TTSInput) -> TTSOutput:
        client = ComfyClient(base_url=self.base_url)
        try:
            filename_prefix = f"vclone_{uuid.uuid4().hex[:8]}"
            workflow = {
                "1": {
                    "class_type": "LoadAudio",
                    "inputs": {
                        "audio": input_data.voice_id or "",
                    },
                },
                "2": {
                    "class_type": "VoiceCloneNode",
                    "inputs": {
                        "reference_audio": ["1", 0],
                        "text": input_data.text,
                        "similarity": 0.8,
                        "stability": 0.7,
                    },
                },
                "3": {
                    "class_type": "SaveAudio",
                    "inputs": {
                        "audio": ["2", 0],
                        "filename_prefix": filename_prefix,
                    },
                },
            }

            result = await client.submit_and_wait(workflow, timeout=180)
            outputs = result["outputs"]
            audio_files = outputs.get("audio", []) or outputs.get("files", [])

            if audio_files:
                output_path = os.path.join(
                    settings.storage_local_path, "voice_clone",
                    audio_files[0]["filename"]
                )
            else:
                output_path = os.path.join(settings.storage_local_path, "voice_clone", f"{filename_prefix}.wav")

            return TTSOutput(
                audio_path=output_path,
                duration_seconds=0.0,
                provider="comfyui",
                model_used="VoiceCloneNode",
            )
        finally:
            await client.close()
