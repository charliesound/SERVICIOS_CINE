from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from scripts.local_media_agent.controlled_fixture_smoke_visible_report_renderer import (
    render_controlled_fixture_smoke_visible_report,
)


def render_controlled_fixture_smoke_result_in_memory(
    smoke_result: Mapping[str, Any],
    *,
    human_review_decision: str = "PENDING_HUMAN_REVIEW",
    next_allowed_phase: str = "PENDING_HUMAN_DECISION",
) -> str:
    """Render structured controlled fixture smoke evidence as Markdown in memory."""
    if not isinstance(smoke_result, Mapping):
        raise TypeError("smoke_result must be a mapping")

    smoke_result_snapshot = dict(smoke_result)

    return render_controlled_fixture_smoke_visible_report(
        smoke_result_snapshot,
        human_review_decision=human_review_decision,
        next_allowed_phase=next_allowed_phase,
    )
