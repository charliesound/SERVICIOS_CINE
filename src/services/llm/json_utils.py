from __future__ import annotations

import json
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLMJSONError(ValueError):
    pass


_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_text(text: str) -> str:
    candidate = (text or "").strip()
    if not candidate:
        raise LLMJSONError("Empty LLM response")

    fenced = _JSON_BLOCK_RE.search(candidate)
    if fenced:
        return fenced.group(1).strip()

    start_object = candidate.find("{")
    start_array = candidate.find("[")
    starts = [pos for pos in (start_object, start_array) if pos != -1]
    if not starts:
        raise LLMJSONError("LLM response does not contain JSON")

    start = min(starts)
    snippet = candidate[start:].strip()
    return snippet


def parse_json_payload(text: str) -> Any:
    snippet = extract_json_text(text)
    try:
        return json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise LLMJSONError(f"Invalid JSON returned by LLM: {exc}") from exc


def parse_model(text: str, model_cls: type[T]) -> T:
    payload = parse_json_payload(text)
    try:
        return model_cls.model_validate(payload)
    except ValidationError as exc:
        raise LLMJSONError(f"LLM JSON does not match expected schema: {exc}") from exc
