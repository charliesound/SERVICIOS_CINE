"""Deterministic, read-only producer editorial evidence query (Siruela pilot).

Selects previously proven producer evidence records by exact topic alias and
an optional interview subject filter. No LLM, no embeddings, no network, no
media decoding. Produces a stable projection of the evidence fields consumed
by producers and downstream DA-VINCI navigation.
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

PROJECT = "Siruela"

SOURCE = "final_producer_evidence_v2.json"

QUERY_TYPE = "DETERMINISTIC_TOPIC_ALIAS"

STATUS_RESULTS = "RESULTS"
STATUS_NO_RESULTS = "NO_RESULTS"
STATUS_UNSUPPORTED_TOPIC = "UNSUPPORTED_TOPIC"
STATUS_UNSUPPORTED_CHARACTER = "UNSUPPORTED_CHARACTER"

AUDIO_ONLY_STATUS = "AUDIO_ONLY_VIDEO_UNMAPPED"
MAPPED_STATUS = "MAPPED"

NAVIGATION_AVAILABLE = "NAVIGATION_AVAILABLE"
NAVIGATION_UNAVAILABLE = "NAVIGATION_UNAVAILABLE"
NAVIGATION_REASON_AUDIO_ONLY = "AUDIO_ONLY_VIDEO_UNMAPPED"
NAVIGATION_REASON_CANDIDATE_NOT_FOUND = "CANDIDATE_NOT_FOUND"

TOPIC_FAMILIES = (
    "pastor/pastoreo",
    "ganado/ganadería",
    "ovejas/ovino",
    "campo",
    "jóvenes/relevo generacional",
    "problemas/dificultades",
)

CHARACTER_ALIASES = {
    "Kiko Traza": ("kiko", "kiko traza"),
    "Pruden": ("pruden",),
}

# Normalized (accent-stripped, casefolded) alias -> canonical topic family.
_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "pastor/pastoreo": ("pastor", "pastores", "pastoreo"),
    "ganado/ganadería": ("ganado", "ganadería", "ganadero", "ganadera"),
    "ovejas/ovino": ("oveja", "ovejas", "ovino", "rebaño"),
    "campo": ("campo",),
    "jóvenes/relevo generacional": ("joven", "jóvenes", "relevo", "relevo generacional"),
    "problemas/dificultades": ("problema", "problemas", "dificultad", "dificultades"),
}


class ProducerQueryError(ValueError):
    """Sanitized validation failure for producer evidence queries."""


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


_TOPIC_ALIASES: dict[str, str] = {}
for _family in TOPIC_FAMILIES:
    for _alias in _ALIAS_GROUPS[_family]:
        _TOPIC_ALIASES[_normalize(_alias)] = _family

_CHARACTER_CANONICAL: dict[str, str] = {}
for _canonical, _aliases in CHARACTER_ALIASES.items():
    for _alias in _aliases:
        _CHARACTER_CANONICAL[_normalize(_alias)] = _canonical


@dataclass(frozen=True, slots=True)
class ProducerEvidenceItem:
    """Immutable projection of one producer evidence record."""

    candidate_id: str
    interview_subject: str
    topic: str
    producer_context_excerpt: str
    excerpt_audio_start: float
    excerpt_audio_end: float
    excerpt_video_mapping_status: str
    video_clip: str | None
    excerpt_video_relative_start: float | None
    excerpt_video_relative_end: float | None
    speaker_attribution: str
    editorial_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "interview_subject": self.interview_subject,
            "topic": self.topic,
            "producer_context_excerpt": self.producer_context_excerpt,
            "excerpt_audio_start": self.excerpt_audio_start,
            "excerpt_audio_end": self.excerpt_audio_end,
            "excerpt_video_mapping_status": self.excerpt_video_mapping_status,
            "video_clip": self.video_clip,
            "excerpt_video_relative_start": self.excerpt_video_relative_start,
            "excerpt_video_relative_end": self.excerpt_video_relative_end,
            "speaker_attribution": self.speaker_attribution,
            "editorial_note": self.editorial_note,
        }


@dataclass(frozen=True, slots=True)
class ProducerEvidenceQueryResult:
    """Structured result of a producer editorial query."""

    project: str
    query: str
    topic: str | None
    character: str | None
    status: str
    results: tuple[ProducerEvidenceItem, ...] = field(default_factory=tuple)
    topics_available: tuple[str, ...] = field(default_factory=lambda: TOPIC_FAMILIES)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def mapped(self) -> int:
        return sum(1 for item in self.results if item.excerpt_video_mapping_status == MAPPED_STATUS)

    @property
    def audio_only(self) -> int:
        return sum(
            1
            for item in self.results
            if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
        )


def query_producer_evidence(
    evidence_path: str | Path,
    query: str,
    character: str | None = None,
) -> ProducerEvidenceQueryResult:
    """Return proven producer evidence matching the topic query and optional character."""
    topic = resolve_topic(query)
    resolved_character = resolve_character(character) if character is not None else None

    if topic is None:
        return ProducerEvidenceQueryResult(
            project=PROJECT,
            query=query,
            topic=None,
            character=resolved_character,
            status=STATUS_UNSUPPORTED_TOPIC,
        )
    if character is not None and resolved_character is None:
        return ProducerEvidenceQueryResult(
            project=PROJECT,
            query=query,
            topic=topic,
            character=character,
            status=STATUS_UNSUPPORTED_CHARACTER,
        )

    records = load_evidence(evidence_path)
    selected = [
        record
        for record in records
        if record["topic"] == topic
        and (resolved_character is None or record["interview_subject"] == resolved_character)
    ]
    items = tuple(_evidence_item(record) for record in selected)
    status = STATUS_RESULTS if items else STATUS_NO_RESULTS
    return ProducerEvidenceQueryResult(
        project=PROJECT,
        query=query,
        topic=topic,
        character=resolved_character,
        status=status,
        results=items,
    )


def resolve_topic(query: str) -> str | None:
    """Map a query to a canonical topic family or None when unsupported."""
    if not isinstance(query, str) or not query.strip():
        raise ProducerQueryError("QUERY_REQUIRED")
    return _TOPIC_ALIASES.get(_normalize(query))


def resolve_character(character: str) -> str | None:
    """Map a character alias to its canonical interview name or None."""
    if not isinstance(character, str) or not character.strip():
        return None
    return _CHARACTER_CANONICAL.get(_normalize(character))


def load_evidence(evidence_path: str | Path) -> list[dict[str, Any]]:
    """Load the authoritative producer evidence records."""
    try:
        value = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
    except (OSError, TypeError, json.JSONDecodeError) as exc:
        raise ProducerQueryError("EVIDENCE_INPUT_INVALID") from exc
    if not isinstance(value, dict):
        raise ProducerQueryError("EVIDENCE_INPUT_INVALID")
    records = value.get("items")
    if not isinstance(records, list) or not all(isinstance(r, dict) for r in records):
        raise ProducerQueryError("EVIDENCE_ITEMS_REQUIRED")
    return records


def _evidence_item(record: dict[str, Any]) -> ProducerEvidenceItem:
    required = (
        "candidate_id",
        "interview_subject",
        "topic",
        "PRODUCER_CONTEXT_EXCERPT",
        "EXCERPT_AUDIO_START",
        "EXCERPT_AUDIO_END",
        "EXCERPT_VIDEO_MAPPING_STATUS",
        "video_clip",
        "EXCERPT_VIDEO_RELATIVE_START",
        "EXCERPT_VIDEO_RELATIVE_END",
        "SPEAKER_ATTRIBUTION",
        "EDITORIAL_NOTE",
    )
    if any(field_name not in record for field_name in required):
        raise ProducerQueryError("EVIDENCE_ITEM_FIELDS_REQUIRED")
    try:
        return ProducerEvidenceItem(
            candidate_id=str(record["candidate_id"]),
            interview_subject=str(record["interview_subject"]),
            topic=str(record["topic"]),
            producer_context_excerpt=str(record["PRODUCER_CONTEXT_EXCERPT"]),
            excerpt_audio_start=float(record["EXCERPT_AUDIO_START"]),
            excerpt_audio_end=float(record["EXCERPT_AUDIO_END"]),
            excerpt_video_mapping_status=str(record["EXCERPT_VIDEO_MAPPING_STATUS"]),
            video_clip=record["video_clip"],
            excerpt_video_relative_start=record["EXCERPT_VIDEO_RELATIVE_START"],
            excerpt_video_relative_end=record["EXCERPT_VIDEO_RELATIVE_END"],
            speaker_attribution=str(record["SPEAKER_ATTRIBUTION"]),
            editorial_note=str(record["EDITORIAL_NOTE"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ProducerQueryError("EVIDENCE_ITEM_FIELDS_INVALID") from exc


def build_evidence_navigation(
    item: ProducerEvidenceItem,
) -> dict[str, Any]:
    """Return a read-only navigation block for one producer evidence item.

    MAPPED items expose the exact V2 video clip and source-relative interval.
    AUDIO_ONLY items never invent video location and report a controlled
    unavailable-navigation state.
    """
    if item.excerpt_video_mapping_status == MAPPED_STATUS:
        if any(
            value is None
            for value in (
                item.video_clip,
                item.excerpt_video_relative_start,
                item.excerpt_video_relative_end,
            )
        ):
            raise ProducerQueryError("MAPPED_NAVIGATION_FIELDS_INVALID")
        return {
            "candidate_id": item.candidate_id,
            "navigation_status": NAVIGATION_AVAILABLE,
            "navigation_available": True,
            "navigation_reason": None,
            "video_clip": item.video_clip,
            "video_relative_start": item.excerpt_video_relative_start,
            "video_relative_end": item.excerpt_video_relative_end,
            "navigation_descriptor": (
                f"clip={item.video_clip}; "
                f"interval={item.excerpt_video_relative_start}-"
                f"{item.excerpt_video_relative_end}s"
            ),
        }
    if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS:
        return {
            "candidate_id": item.candidate_id,
            "navigation_status": NAVIGATION_UNAVAILABLE,
            "navigation_available": False,
            "navigation_reason": NAVIGATION_REASON_AUDIO_ONLY,
            "video_clip": None,
            "video_relative_start": None,
            "video_relative_end": None,
            "navigation_descriptor": None,
        }
    raise ProducerQueryError("EVIDENCE_ITEM_MAPPING_STATUS_UNKNOWN")


def resolve_navigation_by_candidate_id(
    result: ProducerEvidenceQueryResult,
    candidate_id: str,
) -> dict[str, Any]:
    """Resolve a navigation block for a given candidate_id within a query result."""
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ProducerQueryError("NAVIGATION_CANDIDATE_ID_REQUIRED")
    for item in result.results:
        if item.candidate_id == candidate_id:
            return build_evidence_navigation(item)
    return {
        "candidate_id": candidate_id,
        "navigation_status": NAVIGATION_UNAVAILABLE,
        "navigation_available": False,
        "navigation_reason": NAVIGATION_REASON_CANDIDATE_NOT_FOUND,
        "video_clip": None,
        "video_relative_start": None,
        "video_relative_end": None,
        "navigation_descriptor": None,
    }


def format_clock(seconds: float) -> str:
    """Format seconds as HH:MM:SS (fractional part dropped for readability)."""
    seconds = max(0.0, float(seconds))
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_clock_precise(seconds: float) -> str:
    """Format seconds as HH:MM:SS.m with one decimal for video navigation."""
    seconds = max(0.0, float(seconds))
    total = int(seconds)
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    tenths = int(round((seconds - total) * 10))
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{tenths}"


def render_producer_evidence(result: ProducerEvidenceQueryResult) -> str:
    """Render a producer-facing ASCII report (no speaker attribution claims)."""
    out: list[str] = []
    out.append("CID — Producer Editorial Evidence")
    out.append(f"Project: {result.project}")
    if result.status == STATUS_UNSUPPORTED_TOPIC:
        out.append(f"Query: {result.query}")
        out.append("TOPIC: UNSUPPORTED")
        out.append("NO_RESULTS — query is not an established topic.")
        out.append("Available topics: " + ", ".join(result.topics_available))
        return "\n".join(out) + "\n"
    if result.status == STATUS_UNSUPPORTED_CHARACTER:
        out.append(f"Query: {result.query} (topic: {result.topic})")
        out.append("CHARACTER: UNSUPPORTED")
        out.append("NO_RESULTS — character is not an established interview subject.")
        out.append("Available: Kiko Traza, Pruden")
        return "\n".join(out) + "\n"

    out.append(f"Topic: {result.topic}")
    if result.character is not None:
        out.append(f"Character filter: {result.character}")
    if result.status == STATUS_NO_RESULTS:
        out.append("NO_RESULTS — no proven evidence for this topic.")
        return "\n".join(out) + "\n"

    for item in result.results:
        out.append("")
        out.append(f"INTERVIEW: {item.interview_subject}")
        out.append("EXCERPT:")
        out.append(item.producer_context_excerpt)
        out.append("AUDIO:")
        out.append(f"{format_clock(item.excerpt_audio_start)}–{format_clock(item.excerpt_audio_end)}")
        if item.excerpt_video_mapping_status == MAPPED_STATUS:
            out.append("VIDEO:")
            out.append(f"{item.video_clip}")
            out.append(
                f"{format_clock_precise(item.excerpt_video_relative_start)}–"
                f"{format_clock_precise(item.excerpt_video_relative_end)}"
            )
        else:
            out.append("VIDEO:")
            out.append("UNMAPPED — audio evidence available")
        out.append(f"EDITORIAL NOTE: {item.editorial_note}")
    return "\n".join(out) + "\n"


__all__ = [
    "PROJECT",
    "SOURCE",
    "QUERY_TYPE",
    "STATUS_RESULTS",
    "STATUS_NO_RESULTS",
    "STATUS_UNSUPPORTED_TOPIC",
    "STATUS_UNSUPPORTED_CHARACTER",
    "AUDIO_ONLY_STATUS",
    "MAPPED_STATUS",
    "NAVIGATION_AVAILABLE",
    "NAVIGATION_UNAVAILABLE",
    "NAVIGATION_REASON_AUDIO_ONLY",
    "NAVIGATION_REASON_CANDIDATE_NOT_FOUND",
    "TOPIC_FAMILIES",
    "CHARACTER_ALIASES",
    "ProducerQueryError",
    "ProducerEvidenceItem",
    "ProducerEvidenceQueryResult",
    "query_producer_evidence",
    "resolve_topic",
    "resolve_character",
    "load_evidence",
    "build_evidence_navigation",
    "resolve_navigation_by_candidate_id",
    "format_clock",
    "format_clock_precise",
    "render_producer_evidence",
]
