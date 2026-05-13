import os
import aiofiles
from pathlib import Path
from app.core.config import settings


async def save_file(file_content: bytes, filename: str, subdir: str = "") -> str:
    base = Path(settings.storage_local_path)
    target = base / subdir / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(str(target), "wb") as f:
        await f.write(file_content)
    return str(target)


def get_file_url(file_path: str) -> str:
    if settings.storage_provider == "local":
        return f"/api/files/{os.path.relpath(file_path, settings.storage_local_path)}"
    return file_path
