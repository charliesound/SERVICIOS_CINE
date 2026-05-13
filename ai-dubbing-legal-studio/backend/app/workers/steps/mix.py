import subprocess
import os


async def mix_audio(audio_paths: list[str], output_path: str = None) -> dict:
    if not output_path:
        output_dir = "./data/storage/mixed"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "mixed_output.wav")

    if len(audio_paths) == 1:
        import shutil
        shutil.copy2(audio_paths[0], output_path)
    else:
        filter_parts = []
        for i, ap in enumerate(audio_paths):
            filter_parts.append(f"[{i}:a]")
        filter_str = "".join(filter_parts)
        for i in range(len(audio_paths)):
            filter_str += f"[{i}:a]" if i == 0 else f"[{i}:a]"
        filter_str = f"amix=inputs={len(audio_paths)}:duration=longest"

        cmd = ["ffmpeg", "-y"]
        for ap in audio_paths:
            cmd.extend(["-i", ap])
        cmd.extend(["-filter_complex", filter_str, "-ac", "2", output_path])
        subprocess.run(cmd, capture_output=True)

    return {"output_path": output_path, "format": "wav", "channels": 2}
