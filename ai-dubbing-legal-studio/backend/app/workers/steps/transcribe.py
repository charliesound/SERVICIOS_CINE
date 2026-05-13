import json
from app.core.config import settings


async def transcribe(audio_path: str, language: str) -> dict:
    segments = [
        {"start": 0.0, "end": 2.0, "text": "Hola, esto es una prueba de transcripción."},
        {"start": 2.0, "end": 4.5, "text": "Estamos probando el sistema de doblaje legal."},
    ]
    return {
        "segments": segments,
        "raw_text": " ".join(s["text"] for s in segments),
        "model_used": f"whisper-{settings.whisper_model}",
        "language": language,
    }
