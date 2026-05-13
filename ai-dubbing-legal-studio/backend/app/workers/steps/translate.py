async def translate(segments: list[dict], source_lang: str, target_lang: str) -> dict:
    translated = []
    for seg in segments:
        translated.append({
            "start": seg["start"],
            "end": seg["end"],
            "source_text": seg["text"],
            "target_text": f"[{target_lang.upper()}] " + seg["text"],
        })
    return {
        "segments": translated,
        "raw_text": " ".join(s["target_text"] for s in translated),
        "model_used": "ollama/mock-translate",
        "source_language": source_lang,
        "target_language": target_lang,
    }
