from __future__ import annotations

from dataclasses import dataclass
import re


SCENE_HEADING_RE = re.compile(
    r"^\s*(?:\d{1,4}[\.:\)-]?\s+)?(?:INT\.?|INTERIOR|EXT\.?|EXTERIOR|INT/EXT\.?|I/E\.?)\s+.+$",
    re.IGNORECASE,
)
CHARACTER_CUE_RE = re.compile(
    r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ0-9 '\.-]{1,40}$"
)
FEATURE_SCRIPT_PHRASES = (
    "guion de largometraje",
    "guión de largometraje",
    "guion cinematografico",
    "guión cinematográfico",
    "feature screenplay",
    "feature script",
)
SCRIPT_KEYWORDS = (
    "guion",
    "guión",
    "screenplay",
    "script",
    "largometraje",
    "escena",
    "secuencia",
)
SCRIPT_CLASSIFICATION_THRESHOLD = 0.55


@dataclass(frozen=True)
class ScriptSignals:
    text_length: int
    scene_heading_count: int
    character_cue_count: int
    has_feature_script_phrase: bool
    has_script_keyword: bool


def extract_script_signals(text: str) -> ScriptSignals:
    source_text = text or ""
    normalized_text = source_text.lower()
    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    scene_heading_count = sum(1 for line in lines if SCENE_HEADING_RE.match(line))
    character_cue_count = sum(
        1
        for line in lines
        if CHARACTER_CUE_RE.match(line) and not SCENE_HEADING_RE.match(line)
    )
    return ScriptSignals(
        text_length=len(source_text),
        scene_heading_count=scene_heading_count,
        character_cue_count=character_cue_count,
        has_feature_script_phrase=any(
            phrase in normalized_text for phrase in FEATURE_SCRIPT_PHRASES
        ),
        has_script_keyword=any(keyword in normalized_text for keyword in SCRIPT_KEYWORDS),
    )


def screenplay_confidence(text: str) -> float:
    signals = extract_script_signals(text)
    if signals.text_length == 0:
        return 0.0

    score = 0.0
    if signals.has_feature_script_phrase:
        score += 0.38
    elif signals.has_script_keyword:
        score += 0.12

    if signals.scene_heading_count >= 5:
        score += 0.32
    elif signals.scene_heading_count >= 2:
        score += 0.28
    elif signals.scene_heading_count >= 1:
        score += 0.14

    if signals.character_cue_count >= 8:
        score += 0.18
    elif signals.character_cue_count >= 3:
        score += 0.14
    elif signals.character_cue_count >= 1:
        score += 0.08

    if signals.text_length >= 10000:
        score += 0.18
    elif signals.text_length >= 4000:
        score += 0.12
    elif signals.text_length >= 1500:
        score += 0.06

    return round(min(score, 0.98), 2)


def is_probable_screenplay(text: str) -> tuple[bool, float, ScriptSignals]:
    confidence = screenplay_confidence(text)
    signals = extract_script_signals(text)
    return confidence >= SCRIPT_CLASSIFICATION_THRESHOLD, confidence, signals
