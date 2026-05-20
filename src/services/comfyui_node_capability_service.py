from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any
from urllib.request import urlopen, Request

from schemas.comfyui_workflow_schema import WorkflowCapabilitySnapshot

logger = logging.getLogger(__name__)

OBJECT_INFO_TIMEOUT = 30


def extract_workflow_node_classes(workflow: dict[str, Any]) -> set[str]:
    classes: set[str] = set()
    for node_id, node in workflow.items():
        if isinstance(node, dict) and "class_type" in node:
            classes.add(node["class_type"])
    return classes


def validate_workflow_nodes(
    workflow: dict[str, Any],
    available_nodes: set[str],
) -> list[str]:
    required = extract_workflow_node_classes(workflow)
    return sorted(required - available_nodes)


def build_capability_snapshot(
    backend: str,
    base_url: str,
    object_info: dict[str, Any] | None = None,
) -> WorkflowCapabilitySnapshot:
    available: list[str] = []
    total = 0
    snapshot_at: str | None = None

    if object_info:
        available = sorted(object_info.keys())
        total = len(available)
        snapshot_at = datetime.now(timezone.utc).isoformat()

    return WorkflowCapabilitySnapshot(
        backend=backend,
        base_url=base_url,
        total_nodes=total,
        available_nodes=available,
        object_info_snapshot_at=snapshot_at,
        source="object_info_api" if object_info else "mock",
    )


def fetch_object_info(base_url: str, timeout: int = OBJECT_INFO_TIMEOUT) -> dict[str, Any] | None:
    url = f"{base_url.rstrip('/')}/api/object_info"
    try:
        req = Request(url)
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, dict) and data:
                logger.info("object_info fetched from %s: %d entries", url, len(data))
                return data
            logger.warning("object_info returned empty or non-dict at %s", url)
            return None
    except Exception as exc:
        logger.warning("Failed to fetch object_info from %s: %s", url, exc)
        return None


def get_instance_capability_snapshot(
    backend: str,
    base_url: str,
    *,
    fetch_live: bool = True,
    cached: dict[str, Any] | None = None,
) -> WorkflowCapabilitySnapshot:
    if fetch_live and cached is None:
        object_info = fetch_object_info(base_url)
    else:
        object_info = cached
    return build_capability_snapshot(backend, base_url, object_info)
