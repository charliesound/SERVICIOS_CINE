from typing import Optional
from app.providers.comfy_client import ComfyClient
from app.core.config import settings


class ComfyUIASRProvider:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.comfyui_dubbing

    async def transcribe(self, audio_path: str, language: str = "es") -> dict:
        client = ComfyClient(base_url=self.base_url)
        try:
            workflow = {
                "1": {
                    "class_type": "LoadAudio",
                    "inputs": {"audio": audio_path},
                },
                "2": {
                    "class_type": "SpeechToText",
                    "inputs": {
                        "audio": ["1", 0],
                        "language": language,
                    },
                },
                "3": {
                    "class_type": "SaveText",
                    "inputs": {
                        "text": ["2", 0],
                        "filename_prefix": "transcript",
                    },
                },
            }

            result = await client.submit_and_wait(workflow, timeout=120)
            outputs = result["outputs"]

            transcript_text = ""
            for node_out in outputs.get("files", []):
                if "transcript" in node_out.get("filename", ""):
                    transcript_text = node_out.get("text", "")

            segments = [
                {"start": 0.0, "end": 0.0, "text": transcript_text}
            ] if transcript_text else []

            return {
                "segments": segments,
                "raw_text": transcript_text,
                "model_used": "SpeechToText",
                "language": language,
            }
        finally:
            await client.close()
