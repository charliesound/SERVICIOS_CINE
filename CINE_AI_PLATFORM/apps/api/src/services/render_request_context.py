from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from src.schemas.render_context import RenderContextFlags


def apply_render_context_to_request_payload(
    request_payload: Dict[str, Any],
    context: Optional[RenderContextFlags],
) -> Dict[str, Any]:
    payload = request_payload if isinstance(request_payload, dict) else {}
    explicit_context = _context_to_dict(context)

    if not explicit_context:
        return payload

    merged_context = _merge_with_payload_fallbacks(payload, explicit_context)
    if not merged_context:
        return payload

    next_payload = deepcopy(payload)
    metadata = next_payload.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    metadata["render_context"] = merged_context
    next_payload["metadata"] = metadata
    return next_payload


def _context_to_dict(context: Optional[RenderContextFlags]) -> Dict[str, Any]:
    if context is None:
        return {}
    return context.model_dump(exclude_none=True)


def _merge_with_payload_fallbacks(payload: Dict[str, Any], explicit_context: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(explicit_context)

    if "character_id" not in merged:
        fallback_character_id = _read_optional_text(payload.get("character_id"))
        if fallback_character_id is not None:
            merged["character_id"] = fallback_character_id

    if "scene_id" not in merged:
        fallback_scene_id = _read_optional_text(payload.get("scene_id"))
        if fallback_scene_id is not None:
            merged["scene_id"] = fallback_scene_id

    if merged.get("use_ipadapter") is True and "character_id" not in merged:
        # Fallback de seguridad: si no hay referencia de personaje, no forzamos IPAdapter.
        merged["use_ipadapter"] = False

    return merged


def _read_optional_text(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None

    trimmed = value.strip()
    return trimmed or None
