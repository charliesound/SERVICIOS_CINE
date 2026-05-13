import os
import uuid
from app.providers.base import BaseTTSProvider, TTSInput, TTSOutput


class MockTTSProvider(BaseTTSProvider):
    async def synthesize(self, input_data: TTSInput) -> TTSOutput:
        output_dir = "./data/storage/tts_mock"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"tts_mock_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(output_dir, filename)

        # Create a minimal valid WAV file header (silence)
        import struct
        sample_rate = 22050
        duration_samples = int(sample_rate * 2)
        with open(output_path, "wb") as f:
            f.write(b"RIFF")
            f.write(struct.pack("<I", 36 + duration_samples * 2))
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write(struct.pack("<I", 16))
            f.write(struct.pack("<H", 1))
            f.write(struct.pack("<H", 1))
            f.write(struct.pack("<I", sample_rate))
            f.write(struct.pack("<I", sample_rate * 2))
            f.write(struct.pack("<H", 2))
            f.write(struct.pack("<H", 16))
            f.write(b"data")
            f.write(struct.pack("<I", duration_samples * 2))
            f.write(b"\x00" * (duration_samples * 2))

        return TTSOutput(
            audio_path=output_path,
            duration_seconds=2.0,
            provider="mock",
            model_used="mock_tts_v1",
        )
