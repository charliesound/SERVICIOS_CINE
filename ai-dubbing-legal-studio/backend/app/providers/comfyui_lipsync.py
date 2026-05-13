import os
from typing import Optional
from app.providers.base import BaseLipSyncProvider, LipSyncInput, LipSyncOutput
from app.providers.comfy_client import ComfyClient
from app.core.config import settings


class ComfyUILipSyncProvider(BaseLipSyncProvider):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.comfyui_dubbing

    async def process(self, input_data: LipSyncInput) -> LipSyncOutput:
        client = ComfyClient(base_url=self.base_url)
        try:
            workflow = {
                "3": {
                    "class_type": "LoadVideo",
                    "inputs": {"video": input_data.video_path},
                },
                "7": {
                    "class_type": "LoadAudio",
                    "inputs": {"audio": input_data.audio_path},
                },
                "20": {
                    "class_type": "Wav2Lip",
                    "inputs": {
                        "video": ["3", 0],
                        "audio": ["7", 0],
                    },
                },
                "30": {
                    "class_type": "SaveVideo",
                    "inputs": {
                        "video": ["20", 0],
                        "filename_prefix": f"lipsync_{os.path.basename(input_data.video_path).split('.')[0]}",
                    },
                },
            }

            result = await client.submit_and_wait(workflow, timeout=300)
            outputs = result["outputs"]
            video_files = outputs.get("videos", [])

            if video_files:
                output_path = os.path.join(
                    settings.storage_local_path, "lipsync",
                    video_files[0]["filename"]
                )
            else:
                output_path = os.path.join(
                    settings.storage_local_path, "lipsync",
                    f"lipsync_output_{result['prompt_id']}.mp4"
                )

            return LipSyncOutput(
                video_path=output_path,
                duration_seconds=0.0,
                provider="comfyui",
                model_used="Wav2Lip",
            )
        finally:
            await client.close()
