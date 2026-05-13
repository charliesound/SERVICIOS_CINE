import asyncio
import json
import time
import uuid
from typing import Optional
import aiohttp
from app.core.config import settings


class ComfyClient:
    def __init__(self, base_url: str = None, client_id: str = None):
        self.base_url = (base_url or settings.comfyui_base_url).rstrip("/")
        self.client_id = client_id or f"dubbing-legal-studio-{uuid.uuid4().hex[:8]}"
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def submit(self, workflow: dict, timeout: int = 30) -> str:
        session = await self._get_session()
        payload = {"prompt": workflow, "client_id": self.client_id}
        async with session.post(
            f"{self.base_url}/prompt",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=timeout),
        ) as resp:
            data = await resp.json()
            if "prompt_id" not in data:
                raise RuntimeError(f"ComfyUI no devolvió prompt_id: {data}")
            return data["prompt_id"]

    async def poll(self, prompt_id: str, timeout: int = None, interval: int = None) -> dict:
        timeout = timeout or settings.comfyui_poll_timeout
        interval = interval or settings.comfyui_poll_interval
        session = await self._get_session()
        start = time.time()
        while time.time() - start < timeout:
            async with session.get(f"{self.base_url}/history/{prompt_id}") as resp:
                history = await resp.json()
            if prompt_id in history:
                return history[prompt_id]
            await asyncio.sleep(interval)
        raise TimeoutError(f"ComfyUI prompt {prompt_id} no completó en {timeout}s")

    async def get_queue(self) -> dict:
        session = await self._get_session()
        async with session.get(f"{self.base_url}/queue") as resp:
            return await resp.json()

    async def get_system_stats(self) -> dict:
        session = await self._get_session()
        async with session.get(f"{self.base_url}/system_stats") as resp:
            return await resp.json()

    async def delete_queue_item(self, prompt_id: str) -> bool:
        session = await self._get_session()
        async with session.delete(f"{self.base_url}/queue", json={"prompt_id": prompt_id}) as resp:
            return resp.status == 200

    def extract_outputs(self, history: dict, prompt_id: str) -> dict:
        outputs = {"images": [], "videos": [], "audio": [], "files": []}
        prompt_history = history.get(prompt_id, {})
        node_outputs = prompt_history.get("outputs", {})
        for node_id, node_data in node_outputs.items():
            for key, items in node_data.items():
                if not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        item_type = item.get("type", "")
                        folder = item.get("folder", "")
                        filename = item.get("filename", "")
                        if filename:
                            entry = {
                                "filename": filename,
                                "folder": folder,
                                "type": item_type,
                                "node_id": node_id,
                            }
                            if item_type in ("video", "animation", "gif"):
                                outputs["videos"].append(entry)
                            elif item_type in ("audio", "wav", "mp3"):
                                outputs["audio"].append(entry)
                            else:
                                outputs["images"].append(entry)
        return outputs

    async def submit_and_wait(
        self, workflow: dict, timeout: int = None, submit_timeout: int = 30
    ) -> dict:
        prompt_id = await self.submit(workflow, timeout=submit_timeout)
        history = await self.poll(prompt_id, timeout=timeout)
        outputs = self.extract_outputs(history, prompt_id)
        return {
            "prompt_id": prompt_id,
            "history": history,
            "outputs": outputs,
        }

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
