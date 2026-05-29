from __future__ import annotations

import asyncio
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pytest
from services.queue_service import queue_service, QueueItem, QueueStatus
from services.job_scheduler import JobScheduler


def _make_item(job_id: str, backend: str = "still") -> QueueItem:
    return QueueItem(
        job_id=job_id,
        task_type=backend,
        backend=backend,
        priority=0,
        user_plan="pro",
        user_id="test-user",
        created_at=datetime.utcnow(),
        workflow_key="test_workflow",
        prompt={"prompt": "test"},
        metadata={},
        max_retries=0,
    )


async def _drain():
    """Yield control so pending tasks can execute."""
    await asyncio.sleep(0)


@pytest.fixture(autouse=True)
def _reset_queue():
    queue_service._persistence_mode = "memory"
    queue_service._queue = defaultdict(list)
    queue_service._running = defaultdict(list)
    queue_service._completed = {}
    queue_service._job_map = {}
    yield


@pytest.fixture
def scheduler():
    s = JobScheduler()
    s._running_tasks = {}
    s._running = False
    return s


@pytest.mark.asyncio
async def test_process_queues_not_blocked_by_slow_job(scheduler):
    queue_service._queue["still"] = [
        _make_item("job-1"),
        _make_item("job-2"),
    ]
    for jid in ["job-1", "job-2"]:
        queue_service._job_map[jid] = _make_item(jid)

    dispatched = []

    async def mock_execute(item):
        dispatched.append(item.job_id)
        if item.job_id == "job-1":
            await asyncio.sleep(3600)
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()
    assert "job-1" in scheduler._running_tasks

    await scheduler._process_queues()
    await _drain()
    assert "job-2" in scheduler._running_tasks
    assert len(scheduler._running_tasks) == 2
    assert len(dispatched) == 2


@pytest.mark.asyncio
async def test_does_not_dispatch_same_job_twice(scheduler):
    queue_service._queue["still"] = [
        _make_item("job-1"),
    ]
    queue_service._job_map["job-1"] = _make_item("job-1")

    call_count = 0

    async def mock_execute(item):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(3600)
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()
    assert "job-1" in scheduler._running_tasks
    assert call_count == 1

    await scheduler._process_queues()
    assert len(scheduler._running_tasks) == 1
    assert call_count == 1


@pytest.mark.asyncio
async def test_done_tasks_cleaned_up_on_next_cycle(scheduler):
    queue_service._queue["still"] = [
        _make_item("job-1"),
    ]
    queue_service._job_map["job-1"] = _make_item("job-1")

    async def mock_execute(item):
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()
    assert "job-1" in scheduler._running_tasks
    assert scheduler._running_tasks["job-1"].done()

    await scheduler._process_queues()
    assert "job-1" not in scheduler._running_tasks


@pytest.mark.asyncio
async def test_exception_in_task_does_not_kill_scheduler(scheduler):
    queue_service._queue["still"] = [
        _make_item("job-1"),
        _make_item("job-2"),
    ]
    for jid in ["job-1", "job-2"]:
        queue_service._job_map[jid] = _make_item(jid)

    calls = []

    async def mock_execute(item):
        calls.append(item.job_id)
        if item.job_id == "job-1":
            raise RuntimeError("Simulated failure")
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()

    assert "job-1" in scheduler._running_tasks
    assert scheduler._running_tasks["job-1"].done()

    await scheduler._process_queues()
    await _drain()

    assert "job-2" in scheduler._running_tasks
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_respects_max_concurrent_still(scheduler):
    queue_service._queue["still"] = [
        _make_item("job-1"),
        _make_item("job-2"),
        _make_item("job-3"),
    ]
    for i in range(1, 4):
        queue_service._job_map[f"job-{i}"] = _make_item(f"job-{i}")

    dispatched = []

    async def mock_execute(item):
        dispatched.append(item.job_id)
        await asyncio.sleep(3600)
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()
    await scheduler._process_queues()
    await _drain()

    assert len(dispatched) == 2
    assert len(scheduler._running_tasks) == 2

    await scheduler._process_queues()
    await _drain()
    assert len(scheduler._running_tasks) == 2
    assert len(dispatched) == 2


@pytest.mark.asyncio
async def test_can_dispatch_across_multiple_backends(scheduler):
    queue_service._queue["still"] = [_make_item("job-still")]
    queue_service._queue["video"] = [_make_item("job-video", "video")]
    queue_service._queue["dubbing"] = [_make_item("job-dubbing", "dubbing")]
    queue_service._queue["lab"] = [_make_item("job-lab", "lab")]

    for jid in ["job-still", "job-video", "job-dubbing", "job-lab"]:
        queue_service._job_map[jid] = _make_item(jid)

    dispatched = []

    async def mock_execute(item):
        dispatched.append(item.job_id)
        await asyncio.sleep(3600)
        return True, None

    scheduler._execute_job = mock_execute

    await scheduler._process_queues()
    await _drain()

    assert len(dispatched) == 4
    assert "job-still" in scheduler._running_tasks
    assert "job-video" in scheduler._running_tasks
    assert "job-dubbing" in scheduler._running_tasks
    assert "job-lab" in scheduler._running_tasks
