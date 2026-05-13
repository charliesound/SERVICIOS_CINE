import os
import uuid
import shutil
from app.providers.base import BaseLipSyncProvider, LipSyncInput, LipSyncOutput


class MockLipSyncProvider(BaseLipSyncProvider):
    async def process(self, input_data: LipSyncInput) -> LipSyncOutput:
        output_dir = "./data/storage/lipsync_mock"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"lipsync_mock_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(output_dir, filename)

        # Copy input video as mock output
        if os.path.exists(input_data.video_path):
            shutil.copy2(input_data.video_path, output_path)
        else:
            # Create minimal mock file
            with open(output_path, "wb") as f:
                f.write(b"mock_lipsync_video")

        return LipSyncOutput(
            video_path=output_path,
            duration_seconds=2.0,
            provider="mock",
            model_used="mock_lipsync_v1",
        )
