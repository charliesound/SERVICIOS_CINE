from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.queue_service import QueueItem, QueueService, QueueStatus  # noqa: E402


def test_invalid_render_payload_is_failed_without_retry() -> None:
    service = QueueService()
    service._reset_runtime_state()
    service._record_transition = lambda *_args, **_kwargs: None  # type: ignore[method-assign]
    item = QueueItem(
        job_id="job-invalid-render",
        task_type="analyze",
        backend="still",
        priority=1,
        user_plan="pro",
        user_id="user-1",
        created_at=datetime.utcnow(),
        workflow_key=None,
        prompt=None,
    )
    service._job_map[item.job_id] = item
    service._queue[item.backend] = []

    ok = service.mark_failed(item.job_id, "Missing render payload: prompt/workflow_key not found")

    assert ok is True
    assert item.status == QueueStatus.FAILED
    assert item.retry_count == 0
    assert item.job_id in service._completed
    assert not service._queue[item.backend]


def test_recover_on_startup_does_not_requeue_invalid_render_payload(monkeypatch) -> None:
    service = QueueService()
    service._reset_runtime_state()
    monkeypatch.setattr(service, "_is_db_mode", lambda: True)
    transitions: list[tuple[str, str | None]] = []

    def fake_record_transition(item: QueueItem, event: str, recovery_reason: str | None = None) -> None:
        transitions.append((event, recovery_reason))

    monkeypatch.setattr(service, "_record_transition", fake_record_transition)

    record = SimpleNamespace(
        id="job-stale-render",
        status="queued",
        job_type="render:storyboard",
        result_data=json.dumps(
            {
                "task_type": "storyboard",
                "backend": "still",
                "workflow_key": None,
                "prompt": None,
                "priority": 0,
                "user_plan": "pro",
                "project_id": "project-1",
                "organization_id": "org-1",
            }
        ),
        error_message=None,
        created_by="user-1",
        project_id="project-1",
        organization_id="org-1",
        created_at=datetime.utcnow(),
        completed_at=None,
    )
    def fake_run_db(coroutine):
        try:
            coroutine.close()
        except Exception:
            pass
        return [record]

    monkeypatch.setattr(service, "_run_db", fake_run_db)

    summary = service.recover_on_startup()

    assert summary["loaded"] == 1
    assert summary["requeued"] == 0
    assert summary["failed"] == 1
    assert service._job_map[record.id].status == QueueStatus.FAILED
    assert service._queue["still"] == []
    assert transitions == [("startup_failed", "invalid_payload")]
