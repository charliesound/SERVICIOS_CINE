from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import Dict, Set
from datetime import datetime

router = APIRouter(prefix="/api/events", tags=["events"])


class EventBroadcaster:
    def __init__(self):
        self._subscribers: Dict[str, Set[str]] = {}

    def subscribe(self, user_id: str, client_id: str):
        if user_id not in self._subscribers:
            self._subscribers[user_id] = set()
        self._subscribers[user_id].add(client_id)

    def unsubscribe(self, user_id: str, client_id: str):
        if user_id in self._subscribers:
            self._subscribers[user_id].discard(client_id)

    async def broadcast(self, user_id: str, event: dict):
        if user_id in self._subscribers:
            for client_id in self._subscribers[user_id]:
                await self._send_to_client(client_id, event)

    async def _send_to_client(self, client_id: str, event: dict):
        pass


broadcaster = EventBroadcaster()


@router.get("/subscribe/{user_id}")
async def sse_subscribe(user_id: str, request: Request):
    client_id = getattr(request.client, "host", None) or "unknown"

    async def event_stream():
        broadcaster.subscribe(user_id, client_id)
        try:
            while True:
                await asyncio.sleep(30)
                yield f"data: {json.dumps({'type': 'ping', 'time': datetime.utcnow().isoformat()})}\n\n"
        finally:
            broadcaster.unsubscribe(user_id, client_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@router.post("/job-status")
async def notify_job_status(user_id: str, job_id: str, status: str):
    await broadcaster.broadcast(
        user_id,
        {
            "type": "job_status",
            "job_id": job_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
    return {"status": "notified"}
