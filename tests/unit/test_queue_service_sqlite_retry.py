from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy.exc import OperationalError


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.queue_service import QueueItem, QueueService  # noqa: E402


def test_record_transition_retries_when_sqlite_locked(monkeypatch) -> None:
    service = QueueService()
    monkeypatch.setattr(service, "_is_db_mode", lambda: True)

    calls = {"count": 0}

    def fake_run_db(_coroutine):
        try:
            _coroutine.close()
        except Exception:
            pass
        calls["count"] += 1
        if calls["count"] < 3:
            raise OperationalError("INSERT", {}, Exception("database is locked"))
        return None

    monkeypatch.setattr(service, "_run_db", fake_run_db)
    monkeypatch.setattr("services.queue_service.time.sleep", lambda _s: None)

    item = QueueItem(
        job_id="job-1",
        task_type="still",
        backend="still",
        priority=1,
        user_plan="free",
        user_id="user-1",
        created_at=__import__("datetime").datetime.utcnow(),
    )

    service._record_transition(item, "enqueue")
    assert calls["count"] == 3
