"""CID Local Media Agent -- Automatic Camera <-> External Audio Synchronization.

Architecture: two layers.

LAYER 1 -- Pairwise Synchronization Primitive
  synchronize_pair(video_clip, audio_source) -> PairSyncResult
  Produces affine model: audio_time = A + B * video_time

LAYER 2 -- Session-Level Sync Graph
  assemble_session(media_metadata, pairwise_results) -> SessionSyncResult
  Groups clips, selects master, maps timeline, shares clock-rate.

Everything is local, offline, and read-only on source media.

Time model: ``audio_time = A + B * video_time``
  A = audio timestamp at video time zero.
  B = external-audio seconds per video second.
  AUDIO_SPEED_PERCENT = 100 * B (for retiming external audio).
"""

from __future__ import annotations

import json
import math
import os
import re
import statistics
import subprocess
import tempfile
import time as _time
import unicodedata
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

# ------------------------------------------------------------------
# Schema / constants
# ------------------------------------------------------------------

SYNC_ENGINE_SCHEMA_VERSION = "cid.local_media_agent.auto_sync.v2"
SESSION_SCHEMA_VERSION = "cid.local_media_agent.session_sync.v1"

CONFIDENCE_HIGH = "HIGH"
CONFIDENCE_MEDIUM = "MEDIUM"
CONFIDENCE_LOW = "LOW"
CONFIDENCE_UNRESOLVED = "UNRESOLVED"

DRIFT_STATUS_RESOLVED = "RESOLVED"
DRIFT_STATUS_UNRESOLVED = "UNRESOLVED"

RETIME_CLASSIFICATION_CONSTANT = "CONSTANT_OFFSET"
RETIME_CLASSIFICATION_AFFINE = "OFFSET_PLUS_DRIFT"
RETIME_CLASSIFICATION_UNRESOLVED = "SYNC_UNRESOLVED"

RELATIONSHIP_SAME_EVENT = "SAME_EVENT"
RELATIONSHIP_SYNCED = "SYNCED_TO"
RELATIONSHIP_DUPLICATE = "DUPLICATE"
RELATIONSHIP_COMPLEMENTARY = "COMPLEMENTARY"
RELATIONSHIP_UNRELATED = "UNRELATED"
RELATIONSHIP_UNRESOLVED = "UNRESOLVED"

SPEECH_WINDOW_POSITIONS = [0.0, 0.25, 0.50, 0.75, 1.0]
SYNC_WINDOW_SECONDS = 30.0
SYNC_SAMPLE_RATE = 16000

MIN_CONTENT_MATCHES = 2
MIN_DRIFT_SPAN_SECONDS = 120.0
MIN_DRIFT_VALIDATION_INLIERS = 3
DELTA_CLUSTER_TOLERANCE_SECONDS = 15.0
LONG_FORM_DURATION_SECONDS = 1800.0
LONG_FORM_MIN_SPAN_FRACTION = 0.5
MAX_OFFSET_HYPOTHESES = 3
REACQUISITION_FRACTIONS = [0.10, 0.30, 0.50, 0.70, 0.90]
ACOUSTIC_SEARCH_RADIUS_SECONDS = 0.20
ACOUSTIC_SUBREGION_DISAGREEMENT_SECONDS = 0.04
ACOUSTIC_BOUNDARY_MARGIN_SECONDS = 1.0 / SYNC_SAMPLE_RATE
ACOUSTIC_MIN_PEAK_SCORE = 0.35
ACOUSTIC_MIN_PEAK_UNIQUENESS = 0.05
RETIME_THRESHOLD_FRAMES = 2.0
RETIME_FPS = 25.0
COARSE_OFFSET_BOOTSTRAP_MIN_PHRASES = 3
COARSE_OFFSET_MAX_CLUSTER_TOLERANCE = 20.0

_MIN_TOKEN_LENGTH = 2
_STOPWORD_TOKENS = frozenset({
    "el", "la", "los", "las", "un", "una", "uno", "de", "del", "en",
    "que", "es", "se", "no", "por", "con", "para", "al", "lo", "como",
    "su", "mas", "pero", "ya", "o", "e", "a", "y", "i", "u",
    "este", "esta", "esto", "ese", "esa", "eso",
    "the", "a", "an", "is", "it", "to", "in", "of", "and", "or",
    "that", "this", "for", "on", "at", "by", "we", "you", "i",
})


# ------------------------------------------------------------------
# Layer 1: Pairwise data classes
# ------------------------------------------------------------------

@dataclass
class OrderedOccurrence:
    token: str
    absolute_time: float
    segment_index: int
    occurrence_index: int
    window_id: str | None = None


@dataclass
class ContentAnchor:
    video_token: str
    audio_token: str
    video_time: float
    audio_time: float
    video_occurrence: int
    audio_occurrence: int
    match_score: float = 1.0
    distinctiveness_score: float = 1.0
    video_window_id: str | None = None
    audio_window_id: str | None = None


@dataclass
class TemporalCandidate:
    phrase_id: str
    video_time: float
    audio_time: float
    video_occurrence: int
    audio_occurrence: int
    lexical_score: float
    distinctiveness_score: float
    video_window_id: str | None = None
    audio_window_id: str | None = None

    @property
    def delta(self) -> float:
        return self.audio_time - self.video_time


@dataclass
class OffsetHypothesis:
    median_delta: float
    mad_delta: float
    raw_support: int
    unique_phrases: int
    window_diversity: int
    video_span_seconds: float
    audio_span_seconds: float
    initial_score: float
    verified_anchors: list[ContentAnchor] = field(default_factory=list)
    verification_windows_attempted: int = 0
    verification_windows_confirmed: int = 0
    survived: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "median_delta": round(self.median_delta, 4),
            "mad_delta": round(self.mad_delta, 4),
            "raw_support": self.raw_support,
            "unique_phrases": self.unique_phrases,
            "window_diversity": self.window_diversity,
            "video_span_seconds": round(self.video_span_seconds, 2),
            "audio_span_seconds": round(self.audio_span_seconds, 2),
            "initial_score": round(self.initial_score, 4),
            "verification_windows_attempted": self.verification_windows_attempted,
            "verification_windows_confirmed": self.verification_windows_confirmed,
            "survived": self.survived,
        }


@dataclass
class LocalAlignmentAnchor:
    video_reference_time: float
    audio_reference_time: float
    local_offset_seconds: float
    window_id: str
    matched_phrase_count: int
    matched_token_count: int
    local_uncertainty_ms: float
    lexical_confidence: float
    acoustic_refined: bool = False
    acoustic_peak_uniqueness: float | None = None
    acoustic_best_score: float | None = None
    acoustic_second_best_score: float | None = None
    acoustic_shift_ms: float = 0.0
    valid: bool = True

    @property
    def video_time(self) -> float:
        return self.video_reference_time

    @property
    def audio_time(self) -> float:
        return self.audio_reference_time


@dataclass
class AffineModel:
    intercept_a: float
    slope_b: float
    r_squared: float = 0.0
    residual_std_ms: float = 0.0
    max_residual_ms: float = 0.0
    drift_ms_per_hour: float = 0.0
    predicted_end_drift_ms: float = 0.0
    predicted_end_drift_frames: float = 0.0
    audio_speed_percent: float = 100.0
    anchor_count: int = 0
    anchor_count_input: int = 0
    anchor_count_inliers: int = 0
    anchor_count_rejected: int = 0
    consensus_valid: bool = False
    temporal_span_seconds: float = 0.0
    drift_status: str = DRIFT_STATUS_UNRESOLVED


@dataclass
class PairSyncResult:
    """Result of synchronizing one video clip to one audio source."""
    video_path: str
    audio_path: str
    relationship: str = RELATIONSHIP_UNRESOLVED
    sync_status: str = "UNRESOLVED"
    intercept_a: float | None = 0.0
    slope_b: float | None = 1.0
    drift_ms_per_hour: float | None = 0.0
    predicted_end_drift_ms: float | None = 0.0
    predicted_end_drift_frames: float | None = 0.0
    audio_speed_percent: float | None = 100.0
    confidence: str = CONFIDENCE_UNRESOLVED
    method: str = "content_affine"
    evidence: list[dict[str, Any]] = field(default_factory=list)
    uncertainty_ms: float = 0.0
    retime_recommended: bool = False
    retime_classification: str = RETIME_CLASSIFICATION_UNRESOLVED
    anchors: list[ContentAnchor] = field(default_factory=list)
    affine_model: AffineModel | None = None
    raw_match_count: int = 0
    selected_match_count: int = 0
    temporal_span_seconds: float = 0.0
    local_alignment_anchors: list[LocalAlignmentAnchor] = field(default_factory=list)

    @staticmethod
    def _rounded(value: float | None, digits: int) -> float | None:
        return round(value, digits) if value is not None else None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "schema_version": SYNC_ENGINE_SCHEMA_VERSION,
            "video_path": self.video_path,
            "audio_path": self.audio_path,
            "relationship": self.relationship,
            "sync_status": self.sync_status,
            "intercept_a": self._rounded(self.intercept_a, 6),
            "slope_b": self._rounded(self.slope_b, 10),
            "drift_ms_per_hour": self._rounded(self.drift_ms_per_hour, 4),
            "predicted_end_drift_ms": self._rounded(self.predicted_end_drift_ms, 2),
            "predicted_end_drift_frames": self._rounded(self.predicted_end_drift_frames, 2),
            "audio_speed_percent": self._rounded(self.audio_speed_percent, 6),
            "confidence": self.confidence,
            "method": self.method,
            "evidence": self.evidence,
            "uncertainty_ms": round(self.uncertainty_ms, 2),
            "retime_recommended": self.retime_recommended,
            "retime_classification": self.retime_classification,
            "anchor_count": len(self.anchors),
            "raw_match_count": self.raw_match_count,
            "selected_match_count": self.selected_match_count,
            "temporal_span_seconds": round(self.temporal_span_seconds, 2),
            "local_window_count": len(self.local_alignment_anchors),
            "valid_local_windows": sum(
                1 for anchor in self.local_alignment_anchors if anchor.valid
            ),
            "local_alignment": [
                {
                    "window_id": anchor.window_id,
                    "video_reference_time": round(anchor.video_reference_time, 3),
                    "text_local_offset_ms": round(
                        (anchor.audio_reference_time - anchor.video_reference_time) * 1000,
                        3,
                    ),
                    "acoustic_shift_ms": round(anchor.acoustic_shift_ms, 3),
                    "acoustic_refined": anchor.acoustic_refined,
                    "best_score": (
                        round(anchor.acoustic_best_score, 4)
                        if anchor.acoustic_best_score is not None else None
                    ),
                    "second_best_score": (
                        round(anchor.acoustic_second_best_score, 4)
                        if anchor.acoustic_second_best_score is not None else None
                    ),
                    "peak_uniqueness": (
                        round(anchor.acoustic_peak_uniqueness, 4)
                        if anchor.acoustic_peak_uniqueness is not None else None
                    ),
                    "local_uncertainty_ms": round(anchor.local_uncertainty_ms, 3),
                    "matched_word_count": anchor.matched_token_count,
                }
                for anchor in self.local_alignment_anchors
            ],
        }
        if self.affine_model:
            d["affine"] = {
                "diagnostic_intercept_a": round(self.affine_model.intercept_a, 6),
                "diagnostic_slope_b": round(self.affine_model.slope_b, 10),
                "r_squared": round(self.affine_model.r_squared, 6),
                "residual_std_ms": round(self.affine_model.residual_std_ms, 2),
                "anchor_count_input": self.affine_model.anchor_count_input,
                "anchor_count_inliers": self.affine_model.anchor_count_inliers,
                "anchor_count_rejected": self.affine_model.anchor_count_rejected,
                "consensus_valid": self.affine_model.consensus_valid,
                "drift_status": self.affine_model.drift_status,
                "anchor_count": self.affine_model.anchor_count,
            }
        return d

    def to_manifest_entry(self) -> dict[str, Any]:
        return {
            "sync_method": self.method,
            "offset_seconds": self._rounded(self.intercept_a, 3),
            "slope_b": self._rounded(self.slope_b, 10),
            "confidence": self.confidence,
            "sync_status": self.sync_status,
            "retime_recommended": self.retime_recommended,
            "audio_speed_percent": self._rounded(self.audio_speed_percent, 4),
            "retime_classification": self.retime_classification,
        }


# ------------------------------------------------------------------
# Layer 2: Session-level data classes
# ------------------------------------------------------------------

@dataclass
class SyncEdge:
    """An edge in the session sync graph."""
    source: str
    target: str
    relationship: str
    intercept_a: float = 0.0
    slope_b: float = 1.0
    confidence: str = CONFIDENCE_UNRESOLVED
    drift_status: str = DRIFT_STATUS_UNRESOLVED
    evidence: list[dict[str, Any]] = field(default_factory=list)
    temporal_span_seconds: float = 0.0
    retime_recommended: bool = False
    audio_speed_percent: float = 100.0
    predicted_end_drift_frames: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship,
            "intercept_a": round(self.intercept_a, 6),
            "slope_b": round(self.slope_b, 10),
            "confidence": self.confidence,
            "drift_status": self.drift_status,
            "temporal_span_seconds": round(self.temporal_span_seconds, 2),
            "retime_recommended": self.retime_recommended,
            "audio_speed_percent": round(self.audio_speed_percent, 4),
        }


@dataclass
class SynchronizedClip:
    """A video clip mapped to the session timeline."""
    video_path: str
    audio_reference: str
    session_position_seconds: float
    intercept_a: float
    slope_b: float
    confidence: str
    retime_recommended: bool = False
    audio_speed_percent: float = 100.0
    predicted_end_drift_frames: float = 0.0
    unresolved: bool = False


@dataclass
class SessionSyncResult:
    """Complete session-level synchronization result."""
    session_id: str
    master_audio: str | None = None
    alternate_audio: list[str] = field(default_factory=list)
    synchronized_clips: list[SynchronizedClip] = field(default_factory=list)
    unresolved_clips: list[str] = field(default_factory=list)
    edges: list[SyncEdge] = field(default_factory=list)
    clock_model_shared: bool = False
    shared_slope_b: float = 1.0
    shared_drift_status: str = DRIFT_STATUS_UNRESOLVED
    confidence: str = CONFIDENCE_UNRESOLVED
    processing_seconds: float = 0.0
    privacy: dict[str, bool] = field(default_factory=lambda: {
        "source_media_modified": False,
        "network_used": False,
        "database_used": False,
    })

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SESSION_SCHEMA_VERSION,
            "session_id": self.session_id,
            "master_audio": self.master_audio,
            "alternate_audio": self.alternate_audio,
            "synchronized_clips": [
                {
                    "video_path": c.video_path,
                    "audio_reference": c.audio_reference,
                    "session_position_seconds": round(c.session_position_seconds, 4),
                    "intercept_a": round(c.intercept_a, 6),
                    "slope_b": round(c.slope_b, 10),
                    "confidence": c.confidence,
                    "retime_recommended": c.retime_recommended,
                    "audio_speed_percent": round(c.audio_speed_percent, 4),
                    "unresolved": c.unresolved,
                }
                for c in self.synchronized_clips
            ],
            "unresolved_clips": self.unresolved_clips,
            "edges": [e.to_dict() for e in self.edges],
            "clock_model_shared": self.clock_model_shared,
            "shared_slope_b": round(self.shared_slope_b, 10),
            "shared_drift_status": self.shared_drift_status,
            "confidence": self.confidence,
            "processing_seconds": round(self.processing_seconds, 2),
            "privacy": self.privacy,
        }


HYPOTHESIS_PLAUSIBLE = "PLAUSIBLE"
HYPOTHESIS_CONFIRMED = "CONFIRMED"
HYPOTHESIS_REJECTED = "REJECTED"
HYPOTHESIS_UNRESOLVED = "UNRESOLVED"


@dataclass
class SessionHypothesis:
    """Bounded logical-session hypothesis built from physical media groups."""

    hypothesis_id: str
    video_candidates: list[dict[str, Any]] = field(default_factory=list)
    audio_candidates: list[dict[str, Any]] = field(default_factory=list)
    context_groups: list[str] = field(default_factory=list)
    cheap_evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: str = CONFIDENCE_LOW
    status: str = HYPOTHESIS_PLAUSIBLE
    representative_audio: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id": self.hypothesis_id,
            "video_candidates": [
                item.get("relative_path", "") for item in self.video_candidates
            ],
            "audio_candidates": [
                item.get("relative_path", "") for item in self.audio_candidates
            ],
            "context_groups": list(self.context_groups),
            "cheap_evidence": self.cheap_evidence,
            "confidence": self.confidence,
            "status": self.status,
            "representative_audio": (
                self.representative_audio.get("relative_path", "")
                if self.representative_audio else None
            ),
        }


@dataclass
class ProjectSyncResult:
    """Project-level collection of isolated logical-session results."""

    sessions: list[SessionSyncResult] = field(default_factory=list)
    hypotheses: list[SessionHypothesis] = field(default_factory=list)
    physical_groups: dict[str, list[str]] = field(default_factory=dict)
    unresolved_media: list[str] = field(default_factory=list)
    pair_candidates_before_reduction: int = 0
    pair_candidates_after_reduction: int = 0
    pair_syncs_executed: int = 0
    global_cartesian_pairing_used: bool = False
    processing_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "sessions": [session.to_dict() for session in self.sessions],
            "hypotheses": [hypothesis.to_dict() for hypothesis in self.hypotheses],
            "physical_groups": self.physical_groups,
            "unresolved_media": list(self.unresolved_media),
            "pair_candidates_before_reduction": self.pair_candidates_before_reduction,
            "pair_candidates_after_reduction": self.pair_candidates_after_reduction,
            "pair_syncs_executed": self.pair_syncs_executed,
            "global_cartesian_pairing_used": self.global_cartesian_pairing_used,
            "processing_seconds": round(self.processing_seconds, 2),
            "privacy": {
                "source_media_modified": False,
                "network_used": False,
                "database_used": False,
            },
        }


# =====================================================================
# LAYER 1: Text normalization, ordered occurrences, content matching
# =====================================================================

def _normalize_token(token: str) -> str:
    t = token.lower().strip()
    t = "".join(
        c for c in unicodedata.normalize("NFD", t)
        if unicodedata.category(c) != "Mn"
    )
    t = re.sub(r"[^a-z0-9]", "", t)
    return t


def _is_distinctive(token: str) -> bool:
    t = _normalize_token(token)
    if len(t) < _MIN_TOKEN_LENGTH:
        return False
    if t in _STOPWORD_TOKENS:
        return False
    return True


def build_ordered_occurrences(
    segments: list[dict[str, Any]],
) -> list[OrderedOccurrence]:
    """Build ordered occurrences, filtering stopwords. Each duplicate token
    is an independent entry with its own absolute_time and occurrence_index."""
    occurrences: list[OrderedOccurrence] = []
    token_counts: dict[str, int] = {}
    for seg_idx, seg in enumerate(segments):
        text = seg.get("text", "")
        start = float(seg.get("source_start_seconds", seg.get("start_seconds", 0.0)))
        words = seg.get("words") or []
        if words:
            for raw_word in words:
                raw_token = raw_word.get("word", "")
                norm = _normalize_token(raw_token)
                if not _is_distinctive(raw_token):
                    continue
                word_start = float(raw_word.get(
                    "source_start_seconds",
                    raw_word.get("start_seconds", start),
                ))
                occ_idx = token_counts.get(norm, 0)
                token_counts[norm] = occ_idx + 1
                occurrences.append(OrderedOccurrence(
                    token=norm,
                    absolute_time=round(word_start, 4),
                    segment_index=seg_idx,
                    occurrence_index=occ_idx,
                    window_id=seg.get("window_id"),
                ))
            continue
        tokens = text.split()
        seg_end = float(seg.get("source_end_seconds", seg.get("end_seconds", start + 1.0)))
        seg_duration = seg_end - start
        n_tokens = len(tokens)
        for tok_idx, raw_token in enumerate(tokens):
            norm = _normalize_token(raw_token)
            if not norm or len(norm) < _MIN_TOKEN_LENGTH:
                continue
            if not _is_distinctive(raw_token):
                continue
            if n_tokens > 1:
                frac = tok_idx / (n_tokens - 1)
            else:
                frac = 0.5
            abs_time = start + frac * seg_duration
            occ_idx = token_counts.get(norm, 0)
            token_counts[norm] = occ_idx + 1
            occurrences.append(OrderedOccurrence(
                token=norm,
                absolute_time=round(abs_time, 4),
                segment_index=seg_idx,
                occurrence_index=occ_idx,
                window_id=seg.get("window_id"),
            ))
    return occurrences


def match_content_anchors(
    video_occurrences: list[OrderedOccurrence],
    audio_occurrences: list[OrderedOccurrence],
) -> list[ContentAnchor]:
    """Select a globally coherent monotonic chain of content occurrences."""
    candidates = _build_temporal_candidates(video_occurrences, audio_occurrences)
    return _select_monotonic_anchor_chain(candidates)


def _build_temporal_candidates(
    video_occurrences: list[OrderedOccurrence],
    audio_occurrences: list[OrderedOccurrence],
) -> list[TemporalCandidate]:
    video_by_token: dict[str, list[OrderedOccurrence]] = {}
    audio_by_token: dict[str, list[OrderedOccurrence]] = {}
    frequencies: dict[str, int] = {}
    for occurrence in video_occurrences:
        video_by_token.setdefault(occurrence.token, []).append(occurrence)
        frequencies[occurrence.token] = frequencies.get(occurrence.token, 0) + 1
    for occurrence in audio_occurrences:
        audio_by_token.setdefault(occurrence.token, []).append(occurrence)
        frequencies[occurrence.token] = frequencies.get(occurrence.token, 0) + 1

    candidates: list[TemporalCandidate] = []
    for token in sorted(set(video_by_token) & set(audio_by_token)):
        frequency = frequencies[token]
        distinctiveness = min(1.0, len(token) / 10.0) + 1.0 / frequency
        for video in video_by_token[token]:
            for audio in audio_by_token[token]:
                candidates.append(TemporalCandidate(
                    phrase_id=token,
                    video_time=video.absolute_time,
                    audio_time=audio.absolute_time,
                    video_occurrence=video.occurrence_index,
                    audio_occurrence=audio.occurrence_index,
                    lexical_score=1.0,
                    distinctiveness_score=distinctiveness,
                    video_window_id=video.window_id,
                    audio_window_id=audio.window_id,
                ))
    return candidates


def build_offset_hypotheses(
    candidates: list[TemporalCandidate],
    max_hypotheses: int = MAX_OFFSET_HYPOTHESES,
) -> list[OffsetHypothesis]:
    """Build several offset families without selecting a final winner."""
    if not candidates:
        return []
    raw_hypotheses: list[OffsetHypothesis] = []
    for center in candidates:
        members = [
            candidate for candidate in candidates
            if abs(candidate.delta - center.delta) <= DELTA_CLUSTER_TOLERANCE_SECONDS
        ]
        unique_phrases = len({candidate.phrase_id for candidate in members})
        if unique_phrases < 2:
            continue
        deltas = sorted(candidate.delta for candidate in members)
        median_delta = deltas[len(deltas) // 2]
        mad = statistics.median(abs(delta - median_delta) for delta in deltas)
        video_times = [candidate.video_time for candidate in members]
        audio_times = [candidate.audio_time for candidate in members]
        video_span = max(video_times) - min(video_times)
        audio_span = max(audio_times) - min(audio_times)
        windows = {
            (candidate.video_window_id, candidate.audio_window_id)
            for candidate in members
        }
        score = (
            unique_phrases * 3.0
            + min(len(windows), 5) * 0.5
            + min(video_span / 600.0, 3.0)
            - min(mad, DELTA_CLUSTER_TOLERANCE_SECONDS) / 15.0
        )
        hypothesis = OffsetHypothesis(
            median_delta=median_delta,
            mad_delta=mad,
            raw_support=len(members),
            unique_phrases=unique_phrases,
            window_diversity=len(windows),
            video_span_seconds=video_span,
            audio_span_seconds=audio_span,
            initial_score=score,
        )
        if any(
            abs(hypothesis.median_delta - existing.median_delta)
            <= DELTA_CLUSTER_TOLERANCE_SECONDS
            for existing in raw_hypotheses
        ):
            continue
        raw_hypotheses.append(hypothesis)
    raw_hypotheses.sort(key=lambda hypothesis: hypothesis.initial_score, reverse=True)
    return raw_hypotheses[:max_hypotheses]


def _compute_coarse_offset_hypotheses(
    raw_candidates: list[TemporalCandidate],
    video_duration_seconds: float,
    audio_duration_seconds: float,
) -> list[dict[str, Any]]:
    """Extract provisional delta hypotheses from raw content matches.

    Returns a list of candidate offset dictionaries sorted by support.
    Each contains median_delta, support, unique_phrases, video_span,
    audio_span.  Used only as a bootstrap seed — never as final evidence.
    """
    if not raw_candidates:
        return []
    deltas = [c.delta for c in raw_candidates]
    if not deltas:
        return []
    hypotheses: list[dict[str, Any]] = []
    seen_centers: list[float] = []
    for candidate in raw_candidates:
        center = candidate.delta
        if any(abs(center - s) <= COARSE_OFFSET_MAX_CLUSTER_TOLERANCE for s in seen_centers):
            continue
        members = [
            c for c in raw_candidates
            if abs(c.delta - center) <= COARSE_OFFSET_MAX_CLUSTER_TOLERANCE
        ]
        unique_phrases = len({c.phrase_id for c in members})
        if unique_phrases < 2:
            continue
        member_deltas = sorted(c.delta for c in members)
        median_delta = member_deltas[len(member_deltas) // 2]
        mad = statistics.median(abs(d - median_delta) for d in member_deltas)
        video_times = [c.video_time for c in members]
        audio_times = [c.audio_time for c in members]
        video_span = max(video_times) - min(video_times) if len(video_times) >= 2 else 0.0
        audio_span = max(audio_times) - min(audio_times) if len(audio_times) >= 2 else 0.0
        score = unique_phrases * 3.0 + min(video_span / 600.0, 3.0) - min(mad, 20.0) / 20.0
        hypotheses.append({
            "median_delta": median_delta,
            "support": len(members),
            "unique_phrases": unique_phrases,
            "video_span": video_span,
            "audio_span": audio_span,
            "mad": mad,
            "score": score,
        })
        seen_centers.append(center)
    hypotheses.sort(key=lambda h: (h["unique_phrases"], h["score"]), reverse=True)
    return hypotheses


def select_verification_windows(
    duration_seconds: float,
    window_seconds: float = SYNC_WINDOW_SECONDS,
) -> list[float]:
    """Select separated video windows for long-form hypothesis testing."""
    if duration_seconds <= window_seconds:
        return [0.0]
    return [
        round(fraction * (duration_seconds - window_seconds), 2)
        for fraction in REACQUISITION_FRACTIONS
    ]


def project_audio_window_start(
    video_start_seconds: float,
    hypothesis_delta: float,
    audio_duration_seconds: float,
    window_seconds: float = SYNC_WINDOW_SECONDS,
) -> float:
    """Project a video window onto the audio timeline using a hypothesis."""
    maximum_start = max(0.0, audio_duration_seconds - window_seconds)
    return round(max(0.0, min(
        video_start_seconds + hypothesis_delta,
        maximum_start,
    )), 2)


def _dedupe_evidence_candidates(
    candidates: list[TemporalCandidate],
    hypothesis_delta: float,
) -> list[TemporalCandidate]:
    """Return one candidate per distinct phrase evidence, within tolerance.

    Repeated occurrences of the same phrase (or near-identical evidence) must
    not inflate independent support counts.  For each phrase_id we keep only
    the highest-distinctiveness candidate that agrees with the hypothesized
    delta within the cluster tolerance.
    """
    tolerance = max(
        DELTA_CLUSTER_TOLERANCE_SECONDS,
        COARSE_OFFSET_MAX_CLUSTER_TOLERANCE,
    )
    best: dict[str, TemporalCandidate] = {}
    for candidate in candidates:
        if abs(candidate.delta - hypothesis_delta) > tolerance:
            continue
        prev = best.get(candidate.phrase_id)
        if prev is None or candidate.distinctiveness_score > prev.distinctiveness_score:
            best[candidate.phrase_id] = candidate
    return list(best.values())


def _cluster_evidence_regions(
    deduped: list[TemporalCandidate],
    min_separation_seconds: float = SYNC_WINDOW_SECONDS,
) -> list[float]:
    """Cluster deduped evidence into temporally separated video regions.

    Returns the representative video time of each independent region,
    sorted ascending.  Regions separated by at least min_separation represent
    independent evidence rather than a single inflated event.
    """
    if not deduped:
        return []
    times = sorted(c.video_time for c in deduped)
    clusters: list[list[float]] = [[times[0]]]
    for t in times[1:]:
        if t - clusters[-1][-1] <= min_separation_seconds:
            clusters[-1].append(t)
        else:
            clusters.append([t])
    return [sum(c) / len(c) for c in clusters]


def build_evidence_verification_windows(
    raw_candidates: list[TemporalCandidate],
    hypothesis_delta: float,
    video_duration_seconds: float,
    max_windows: int = 5,
    min_window_seconds: float = SYNC_WINDOW_SECONDS,
) -> list[float]:
    """Select verification windows from actual evidence-supported regions.

    Instead of probing arbitrary fractions of the timeline, this derives
    window positions from where matching evidence actually exists, so sparse
    long-form clips with camera start-time offsets are tested where the
    content match genuinely occurs.

    Only 3 or more independent regions can ever support a resolution; 1-2
    regions yield fewer windows, which the downstream cardinality gate then
    treats as insufficient evidence.
    """
    deduped = _dedupe_evidence_candidates(raw_candidates, hypothesis_delta)
    regions = _cluster_evidence_regions(deduped)
    windows: list[float] = []
    for region_time in regions[:max_windows]:
        start = max(0.0, min(
            region_time - min_window_seconds / 2.0,
            max(0.0, video_duration_seconds - min_window_seconds),
        ))
        windows.append(round(start, 2))
    return windows


def long_form_minimum_span(video_duration_seconds: float) -> float:
    """Return the duration-aware minimum authoritative anchor span."""
    if video_duration_seconds < LONG_FORM_DURATION_SECONDS:
        return MIN_DRIFT_SPAN_SECONDS
    return max(
        MIN_DRIFT_SPAN_SECONDS,
        video_duration_seconds * LONG_FORM_MIN_SPAN_FRACTION,
    )


def evaluate_hypothesis(
    hypothesis: OffsetHypothesis,
    anchors: list[ContentAnchor],
    video_duration_seconds: float,
) -> OffsetHypothesis:
    """Apply independent-window and long-form survival requirements."""
    hypothesis.verified_anchors = anchors
    hypothesis.verification_windows_confirmed = len({
        anchor.video_window_id for anchor in anchors if anchor.video_window_id is not None
    })
    span = 0.0
    if anchors:
        span = max(anchor.video_time for anchor in anchors) - min(
            anchor.video_time for anchor in anchors
        )
    hypothesis.survived = (
        len(anchors) >= MIN_DRIFT_VALIDATION_INLIERS
        and hypothesis.verification_windows_confirmed >= 3
        and span >= long_form_minimum_span(video_duration_seconds)
    )
    return hypothesis


def build_local_alignment_anchors(
    anchors: list[ContentAnchor],
) -> list[LocalAlignmentAnchor]:
    """Collapse token evidence into one robust timing point per window."""
    grouped: dict[str, list[ContentAnchor]] = {}
    for anchor in anchors:
        window_id = anchor.video_window_id or f"segment:{anchor.video_time:.3f}"
        grouped.setdefault(window_id, []).append(anchor)
    local: list[LocalAlignmentAnchor] = []
    for window_id, window_anchors in sorted(grouped.items()):
        if len(window_anchors) < 3:
            continue
        deltas = [anchor.audio_time - anchor.video_time for anchor in window_anchors]
        offset = statistics.median(deltas)
        mad = statistics.median(abs(delta - offset) for delta in deltas)
        video_reference = statistics.median(
            anchor.video_time for anchor in window_anchors
        )
        audio_reference = video_reference + offset
        local.append(LocalAlignmentAnchor(
            video_reference_time=video_reference,
            audio_reference_time=audio_reference,
            local_offset_seconds=offset,
            window_id=window_id,
            matched_phrase_count=len({a.video_token for a in window_anchors}),
            matched_token_count=len(window_anchors),
            local_uncertainty_ms=max(50.0, mad * 1000.0),
            lexical_confidence=min(1.0, len(window_anchors) / 8.0),
            valid=True,
        ))
    return local


def build_sparse_local_alignment_anchors(
    anchors: list[ContentAnchor],
) -> list[LocalAlignmentAnchor]:
    """Build one robust timing point per independent window for sparse evidence.

    Unlike build_local_alignment_anchors (which requires >=3 tokens per
    window), this tolerates windows with a single agreed token.  It is only
    used in the coarse-offset bootstrap path, where sparse long-form clips may
    have few tokens per window but still provide several genuinely independent
    windows spread across the timeline.

    Safety: output is produced only when at least 3 independent windows exist,
    matching the bootstrap ``>=3 independent confirmed evidence`` rule.
    """
    grouped: dict[str, list[ContentAnchor]] = {}
    for anchor in anchors:
        window_id = anchor.video_window_id or f"segment:{anchor.video_time:.3f}"
        grouped.setdefault(window_id, []).append(anchor)
    local: list[LocalAlignmentAnchor] = []
    for window_id, window_anchors in sorted(grouped.items()):
        deltas = [anchor.audio_time - anchor.video_time for anchor in window_anchors]
        offset = statistics.median(deltas)
        mad = statistics.median(abs(delta - offset) for delta in deltas)
        video_reference = statistics.median(
            anchor.video_time for anchor in window_anchors
        )
        audio_reference = video_reference + offset
        local.append(LocalAlignmentAnchor(
            video_reference_time=video_reference,
            audio_reference_time=audio_reference,
            local_offset_seconds=offset,
            window_id=window_id,
            matched_phrase_count=len({a.video_token for a in window_anchors}),
            matched_token_count=len(window_anchors),
            local_uncertainty_ms=max(50.0, mad * 1000.0),
            lexical_confidence=min(1.0, len(window_anchors) / 8.0),
            valid=True,
        ))
    if len(local) < 3:
        return []
    return local


def refine_local_acoustic_offset(
    reference_samples: Any,
    external_samples: Any,
    sample_rate: int,
    coarse_offset_seconds: float,
    search_radius_seconds: float = ACOUSTIC_SEARCH_RADIUS_SECONDS,
) -> tuple[float, bool, float, float]:
    """Refine a text offset only when a nearby correlation peak is unique."""
    import numpy as np

    reference = np.asarray(reference_samples, dtype=np.float32)
    external = np.asarray(external_samples, dtype=np.float32)
    radius = max(1, int(search_radius_seconds * sample_rate))
    if reference.size < 2 or external.size < 2:
        return coarse_offset_seconds, False, 0.0, 0.0

    scores: list[tuple[int, float]] = []
    for shift in range(-radius, radius + 1):
        if shift >= 0:
            length = min(reference.size, external.size - shift)
            if length < 2:
                continue
            left, right = reference[:length], external[shift:shift + length]
        else:
            offset = -shift
            length = min(reference.size - offset, external.size)
            if length < 2:
                continue
            left, right = reference[offset:offset + length], external[:length]
        left = left - left.mean()
        right = right - right.mean()
        denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
        score = float(np.dot(left, right) / denominator) if denominator else 0.0
        scores.append((shift, score))
    if not scores:
        return coarse_offset_seconds, False, 0.0, 0.0
    scores.sort(key=lambda item: item[1], reverse=True)
    best_shift, best_score = scores[0]
    exclusion_radius = max(2, int(0.005 * sample_rate))
    secondary_peaks = [
        score for shift, score in scores
        if abs(shift - best_shift) > exclusion_radius
    ]
    second_score = max(secondary_peaks, default=0.0)
    uniqueness = best_score - second_score
    refined = coarse_offset_seconds + best_shift / sample_rate
    unique = (
        best_score >= ACOUSTIC_MIN_PEAK_SCORE
        and uniqueness >= ACOUSTIC_MIN_PEAK_UNIQUENESS
    )
    return refined if unique else coarse_offset_seconds, unique, best_score, uniqueness


def _read_pcm16_wav(path: Path) -> Any:
    import wave
    import numpy as np

    with wave.open(str(path), "rb") as wav:
        if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
            raise ValueError("acoustic refinement requires mono PCM16 WAV")
        return np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(
            np.float32
        ) / 32768.0


def _refine_local_alignment_anchors(
    video_path: str,
    audio_path: str,
    audio_duration_seconds: float,
    hypothesis: OffsetHypothesis,
    local_anchors: list[LocalAlignmentAnchor],
    ffmpeg_path: str | None,
) -> list[LocalAlignmentAnchor]:
    """Apply bounded, two-subregion acoustic refinement after lexical matching."""
    refined_anchors: list[LocalAlignmentAnchor] = []
    attempted_window_seconds = SYNC_WINDOW_SECONDS
    for anchor in local_anchors:
        try:
            video_start = float(anchor.window_id)
        except (TypeError, ValueError):
            refined_anchors.append(anchor)
            continue
        audio_start = project_audio_window_start(
            video_start, hypothesis.median_delta, audio_duration_seconds
        )
        with tempfile.TemporaryDirectory(prefix="cid_acoustic_fine_") as td:
            video_wav = Path(td) / "video.wav"
            audio_wav = Path(td) / "audio.wav"
            if not _extract_window_to_wav(
                video_path, video_start, attempted_window_seconds,
                video_wav, ffmpeg_path,
            ) or not _extract_window_to_wav(
                audio_path, audio_start, attempted_window_seconds,
                audio_wav, ffmpeg_path,
            ):
                refined_anchors.append(anchor)
                continue
            try:
                video_signal = _read_pcm16_wav(video_wav)
                audio_signal = _read_pcm16_wav(audio_wav)
                text_relative_offset = (
                    anchor.local_offset_seconds - hypothesis.median_delta
                )
                midpoint = min(video_signal.size, audio_signal.size) // 2
                subregions = [
                    (video_signal[:midpoint], audio_signal[:midpoint]),
                    (video_signal[midpoint:], audio_signal[midpoint:]),
                ]
                results = [
                    refine_local_acoustic_offset(
                        video_part, audio_part, SYNC_SAMPLE_RATE,
                        text_relative_offset,
                    )
                    for video_part, audio_part in subregions
                ]
            except (OSError, ValueError, ImportError):
                refined_anchors.append(anchor)
                continue

        usable = [result for result in results if result[1]]
        diagnostic_best = min(result[2] for result in results)
        diagnostic_uniqueness = min(result[3] for result in results)
        diagnostic_second = diagnostic_best - diagnostic_uniqueness

        def rejected_anchor() -> LocalAlignmentAnchor:
            return replace(
                anchor,
                acoustic_best_score=diagnostic_best,
                acoustic_second_best_score=diagnostic_second,
                acoustic_peak_uniqueness=diagnostic_uniqueness,
            )

        if len(usable) != len(results):
            refined_anchors.append(rejected_anchor())
            continue
        relative_shifts = [result[0] for result in usable]
        if max(relative_shifts) - min(relative_shifts) > ACOUSTIC_SUBREGION_DISAGREEMENT_SECONDS:
            refined_anchors.append(rejected_anchor())
            continue
        if any(
            abs(result[0] - text_relative_offset)
            >= ACOUSTIC_SEARCH_RADIUS_SECONDS - ACOUSTIC_BOUNDARY_MARGIN_SECONDS
            for result in usable
        ):
            refined_anchors.append(rejected_anchor())
            continue

        final_offset = hypothesis.median_delta + statistics.median(relative_shifts)
        best_score = min(result[2] for result in usable)
        uniqueness = min(result[3] for result in usable)
        second_score = best_score - uniqueness
        refined_anchors.append(replace(
            anchor,
            audio_reference_time=anchor.video_reference_time + final_offset,
            local_offset_seconds=final_offset,
            local_uncertainty_ms=max(
                20.0,
                (max(relative_shifts) - min(relative_shifts)) * 1000.0,
            ),
            acoustic_refined=True,
            acoustic_peak_uniqueness=uniqueness,
            acoustic_best_score=best_score,
            acoustic_second_best_score=second_score,
            acoustic_shift_ms=(final_offset - anchor.local_offset_seconds) * 1000.0,
        ))
    return refined_anchors


def _chain_score(chain: list[TemporalCandidate]) -> tuple[float, float, float, float]:
    if not chain:
        return (0.0, 0.0, 0.0, 0.0)
    span = chain[-1].video_time - chain[0].video_time
    score = sum(c.lexical_score + c.distinctiveness_score for c in chain)
    distinct_phrases = len({c.phrase_id for c in chain})
    # Distinctive lexical support outranks repeated ASR hallucinations; span
    # then breaks ties between equally supported candidate families.
    return (float(distinct_phrases), span, float(len(chain)), score)


def _best_monotonic_chain(candidates: list[TemporalCandidate]) -> list[TemporalCandidate]:
    ordered = sorted(candidates, key=lambda c: (c.video_time, c.audio_time, c.phrase_id))
    if not ordered:
        return []
    best: list[list[TemporalCandidate]] = [[candidate] for candidate in ordered]
    for index, candidate in enumerate(ordered):
        for previous in range(index):
            prior = ordered[previous]
            if prior.video_time >= candidate.video_time or prior.audio_time >= candidate.audio_time:
                continue
            duplicate_window_use = any(
                item.phrase_id == candidate.phrase_id
                and item.video_window_id is not None
                and item.video_window_id == candidate.video_window_id
                and item.audio_window_id == candidate.audio_window_id
                for item in best[previous]
            )
            if duplicate_window_use:
                continue
            proposed = best[previous] + [candidate]
            if _chain_score(proposed) > _chain_score(best[index]):
                best[index] = proposed
    return max(best, key=_chain_score)


def _select_monotonic_anchor_chain(
    candidates: list[TemporalCandidate],
) -> list[ContentAnchor]:
    if not candidates:
        return []

    neighborhoods: list[list[TemporalCandidate]] = []
    for center in candidates:
        neighborhood = [
            candidate for candidate in candidates
            if abs(candidate.delta - center.delta) <= DELTA_CLUSTER_TOLERANCE_SECONDS
        ]
        if len({candidate.phrase_id for candidate in neighborhood}) >= 2:
            neighborhoods.append(neighborhood)
    if not neighborhoods:
        neighborhoods = [candidates]

    chain = max(
        (_best_monotonic_chain(neighborhood) for neighborhood in neighborhoods),
        key=_chain_score,
    )
    return [ContentAnchor(
        video_token=item.phrase_id,
        audio_token=item.phrase_id,
        video_time=item.video_time,
        audio_time=item.audio_time,
        video_occurrence=item.video_occurrence,
        audio_occurrence=item.audio_occurrence,
        match_score=item.lexical_score,
        distinctiveness_score=item.distinctiveness_score,
        video_window_id=item.video_window_id,
        audio_window_id=item.audio_window_id,
    ) for item in chain]


# =====================================================================
# LAYER 1: Robust affine model fitting
# =====================================================================

def _ols_fit(points):
    n = len(points)
    if n < 2:
        return (0.0, 1.0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_m = sum(xs) / n
    y_m = sum(ys) / n
    ss_xy = sum((x - x_m) * (y - y_m) for x, y in zip(xs, ys))
    ss_xx = sum((x - x_m) ** 2 for x in xs)
    if ss_xx < 1e-15:
        return (y_m, 1.0)
    b = ss_xy / ss_xx
    a = y_m - b * x_m
    return (a, b)


def _theil_sen_estimate(points):
    """Theil-Sen robust slope via median of pairwise slopes."""
    n = len(points)
    if n < 2:
        return (0.0, 1.0)
    if n == 2:
        return _ols_fit(points)
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            if abs(dx) < 1e-15:
                continue
            slopes.append((points[j][1] - points[i][1]) / dx)
    if not slopes:
        return _ols_fit(points)
    slopes.sort()
    robust_b = slopes[len(slopes) // 2]
    intercepts = [y - robust_b * x for x, y in points]
    intercepts.sort()
    robust_a = intercepts[len(intercepts) // 2]
    return (robust_a, robust_b)


def _r_squared(points, a, b):
    n = len(points)
    if n < 2:
        return 0.0
    ys = [p[1] for p in points]
    y_m = sum(ys) / n
    ss_tot = sum((y - y_m) ** 2 for y in ys)
    if ss_tot < 1e-15:
        return 1.0
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in points)
    return max(0.0, 1.0 - ss_res / ss_tot)


def _residuals_ms(points, a, b):
    return [(y - (a + b * x)) * 1000.0 for x, y in points]


def _robust_outlier_filter(points, max_residual_ms=500.0):
    """Theil-Sen + MAD residual filter with MAD-zero fallback.

    Returns (accepted_points, rejected_count, consensus_valid).

    When consensus is insufficient (< 2 coherent inliers from >= 3 input),
    returns empty list with rejected=n and consensus_valid=False.
    Never silently restores rejected points.
    """
    n_input = len(points)
    if n_input < 3:
        consensus = n_input >= 2
        return list(points), 0, consensus

    a0, b0 = _theil_sen_estimate(points)
    abs_residuals = [abs(y - (a0 + b0 * x)) * 1000.0 for x, y in points]
    med = sorted(abs_residuals)[len(abs_residuals) // 2]
    abs_deviations = sorted([abs(r - med) for r in abs_residuals])
    mad = abs_deviations[len(abs_deviations) // 2]

    if mad >= 1.0:
        filtered = []
        rejected = 0
        for (x, y), res in zip(points, abs_residuals):
            z = abs(res - med) / mad
            if z < 3.5 and res < max_residual_ms:
                filtered.append((x, y))
            else:
                rejected += 1
        if len(filtered) >= 2:
            return filtered, rejected, True
        return [], n_input, False

    a_ols, b_ols = _ols_fit(points)
    ols_residuals = [abs(y - (a_ols + b_ols * x)) * 1000.0 for x, y in points]
    if not ols_residuals:
        return [], n_input, False
    median_ols_resid = sorted(ols_residuals)[len(ols_residuals) // 2]
    threshold = max(median_ols_resid * 3.0, 50.0, min(max_residual_ms, 200.0))
    if threshold > max_residual_ms:
        threshold = max_residual_ms
    filtered = []
    rejected = 0
    for (x, y), res in zip(points, abs_residuals):
        if res < threshold:
            filtered.append((x, y))
        else:
            rejected += 1
    if len(filtered) >= 2:
        return filtered, rejected, True
    return [], n_input, False

def fit_affine_model(anchors, video_duration):
    if not anchors:
        return AffineModel(intercept_a=0.0, slope_b=1.0)
    points = [(a.video_time, a.audio_time) for a in anchors]
    n_input = len(points)
    accepted, n_rejected, consensus_valid = _robust_outlier_filter(points)
    if not accepted or not consensus_valid:
        if len(points) == 1:
            a_fallback, b_fallback = points[0][1], 1.0
            inliers = 1
        else:
            a_fallback, b_fallback = _ols_fit(points) if points else (0.0, 1.0)
            inliers = 0
        v_times = [anc.video_time for anc in anchors]
        span = max(v_times) - min(v_times) if len(v_times) >= 2 else 0.0
        return AffineModel(
            intercept_a=a_fallback, slope_b=b_fallback,
            anchor_count=inliers,
            anchor_count_input=n_input,
            anchor_count_inliers=inliers,
            anchor_count_rejected=n_rejected,
            consensus_valid=False,
            temporal_span_seconds=round(span, 2),
            drift_status=DRIFT_STATUS_UNRESOLVED,
        )
    a, b = _ols_fit(accepted)
    r2 = _r_squared(accepted, a, b)
    resids = _residuals_ms(accepted, a, b)
    res_std = (sum(r ** 2 for r in resids) / len(resids)) ** 0.5 if resids else 0.0
    res_max = max((abs(r) for r in resids), default=0.0)
    v_times = [anc.video_time for anc in anchors]
    span = max(v_times) - min(v_times) if len(v_times) >= 2 else 0.0
    drift_rate = (b - 1.0) * 3600000.0
    end_drift_ms = drift_rate * video_duration / 3600.0 if video_duration > 0 else 0.0
    end_drift_frames = end_drift_ms / (1000.0 / RETIME_FPS) if end_drift_ms else 0.0
    audio_speed = 100.0 * b
    drift_status = DRIFT_STATUS_UNRESOLVED
    if (span >= MIN_DRIFT_SPAN_SECONDS
            and len(accepted) >= MIN_DRIFT_VALIDATION_INLIERS):
        drift_status = DRIFT_STATUS_RESOLVED
    return AffineModel(
        intercept_a=a, slope_b=b, r_squared=r2,
        residual_std_ms=round(res_std, 2),
        max_residual_ms=round(res_max, 2),
        drift_ms_per_hour=round(drift_rate, 4),
        predicted_end_drift_ms=round(end_drift_ms, 2),
        predicted_end_drift_frames=round(end_drift_frames, 2),
        audio_speed_percent=round(audio_speed, 6),
        anchor_count=len(accepted),
        anchor_count_input=n_input,
        anchor_count_inliers=len(accepted),
        anchor_count_rejected=n_rejected,
        consensus_valid=True,
        temporal_span_seconds=round(span, 2),
        drift_status=drift_status,
    )

# =====================================================================
# LAYER 1: Confidence + retime decision
# =====================================================================

def _compute_confidence(model, n_matches):
    if model.anchor_count_inliers < MIN_CONTENT_MATCHES:
        return CONFIDENCE_LOW
    if not model.consensus_valid:
        return CONFIDENCE_LOW
    if model.anchor_count_input > 0:
        rejection_ratio = model.anchor_count_rejected / model.anchor_count_input
        if rejection_ratio >= 0.25:
            return CONFIDENCE_LOW
    if model.r_squared < 0.95:
        return CONFIDENCE_MEDIUM
    if model.residual_std_ms > 200.0:
        return CONFIDENCE_MEDIUM
    if model.drift_status != DRIFT_STATUS_RESOLVED:
        return CONFIDENCE_MEDIUM
    if (model.anchor_count_inliers >= MIN_DRIFT_VALIDATION_INLIERS
            and model.temporal_span_seconds >= MIN_DRIFT_SPAN_SECONDS):
        return CONFIDENCE_HIGH
    if model.anchor_count_inliers >= 2:
        return CONFIDENCE_MEDIUM
    return CONFIDENCE_LOW

def _decide_retime(model, confidence):
    if confidence in (CONFIDENCE_LOW, CONFIDENCE_UNRESOLVED):
        return False, RETIME_CLASSIFICATION_UNRESOLVED
    if (confidence != CONFIDENCE_HIGH
            or not model.consensus_valid
            or model.anchor_count_inliers < MIN_DRIFT_VALIDATION_INLIERS
            or model.temporal_span_seconds < MIN_DRIFT_SPAN_SECONDS
            or model.drift_status != DRIFT_STATUS_RESOLVED):
        return False, RETIME_CLASSIFICATION_CONSTANT
    abs_drift = abs(model.predicted_end_drift_frames)
    if abs_drift < 0.2:
        return False, RETIME_CLASSIFICATION_CONSTANT
    if abs_drift < RETIME_THRESHOLD_FRAMES:
        return False, RETIME_CLASSIFICATION_CONSTANT
    if confidence in (CONFIDENCE_HIGH, CONFIDENCE_MEDIUM):
        return True, RETIME_CLASSIFICATION_AFFINE
    return False, RETIME_CLASSIFICATION_UNRESOLVED


def _compute_uncertainty_ms(model):
    return max(model.residual_std_ms * 2.0, 50.0)


# =====================================================================
# LAYER 1: Candidate reduction
# =====================================================================

def _is_video_file(meta):
    cat = meta.get("category", "")
    if cat == "video":
        return True
    rel = meta.get("relative_path", "")
    return bool(re.search(r"\.(mp4|mov|mxf|mkv|avi|mts|m2ts|webm)$", rel, re.I))


def _is_audio_file(meta):
    cat = meta.get("category", "")
    if cat == "audio":
        return True
    rel = meta.get("relative_path", "")
    return bool(re.search(r"\.(wav|bwf|aif|aiff|mp3|m4a|aac|flac|ogg)$", rel, re.I))


def _duration_seconds(meta):
    return float(meta.get("duration_seconds") or 0.0)


def reduce_candidates(metadata_results):
    """Produce candidate (video, audio) pairs from metadata."""
    videos = [m for m in metadata_results if _is_video_file(m)]
    audios = [m for m in metadata_results if _is_audio_file(m)]
    if not videos or not audios:
        return []
    pairs = []
    for v in videos:
        vd = _duration_seconds(v)
        for a in audios:
            ad = _duration_seconds(a)
            if vd <= 0 or ad <= 0:
                continue
            ratio = ad / vd if vd > 0 else 999.0
            if ratio < 0.3 or ratio > 3.0:
                continue
            pairs.append((v, a))
    return pairs


# =====================================================================
# LAYER 1: Speech window selection
# =====================================================================

def select_speech_windows(duration_seconds, has_scratch_audio=True,
                          window_seconds=SYNC_WINDOW_SECONDS):
    if duration_seconds <= window_seconds:
        return [0.0]
    positions = []
    for frac in SPEECH_WINDOW_POSITIONS:
        t = frac * (duration_seconds - window_seconds)
        t = max(0.0, min(t, duration_seconds - window_seconds))
        positions.append(round(t, 2))
    return sorted(set(positions))


# =====================================================================
# LAYER 1: Window transcription helpers
# =====================================================================

def _windows_no_console_kwargs():
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if os.name == "nt" and flags:
        return {"creationflags": flags}
    return {}


def _extract_window_to_wav(media_path, start_seconds, duration_seconds,
                           output_path, ffmpeg_path=None):
    tool = ffmpeg_path or os.environ.get("CID_FFMPEG_PATH") or "ffmpeg"
    cmd = [
        tool, "-v", "error", "-y",
        "-ss", f"{start_seconds:.3f}",
        "-t", f"{duration_seconds:.3f}",
        "-i", str(media_path),
        "-vn", "-ac", "1", "-ar", str(SYNC_SAMPLE_RATE),
        "-c:a", "pcm_s16le", str(output_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=120,
                              **_windows_no_console_kwargs())
        return proc.returncode == 0 and Path(output_path).is_file()
    except Exception:
        return False


def _transcribe_window(wav_path, model_local_path, language_hint=None):
    from scripts.editorial_intelligence.transcription.transcription import (
        FasterWhisperTranscriptionBackend, TranscriptionRequest, transcribe,
    )
    backend = FasterWhisperTranscriptionBackend(
        model_local_path=model_local_path, device="cpu", compute_type="int8",
        word_timestamps=True,
    )
    request = TranscriptionRequest(
        asset_id="sync_window", temporary_audio_path=str(wav_path),
        language_hint=language_hint, model_local_path=model_local_path, device="cpu",
    )
    result = transcribe(request, backend)
    return result.segments


def transcribe_media_windows(media_path, windows, model_local_path, *,
                             language_hint=None, ffmpeg_path=None,
                             window_seconds=SYNC_WINDOW_SECONDS):
    all_segments = []
    for start in windows:
        with tempfile.TemporaryDirectory(prefix="cid_sync_") as td:
            wav = Path(td) / "window.wav"
            if not _extract_window_to_wav(media_path, start, window_seconds, wav, ffmpeg_path):
                continue
            try:
                segs = _transcribe_window(wav, model_local_path, language_hint)
                for seg in segs:
                    seg["source_start_seconds"] = float(seg.get("start_seconds", 0.0)) + start
                    seg["source_end_seconds"] = float(seg.get("end_seconds", 0.0)) + start
                    seg["window_id"] = f"{start:.3f}"
                    for word in seg.get("words", []):
                        word["source_start_seconds"] = float(
                            word.get("start_seconds", 0.0)
                        ) + start
                        word["source_end_seconds"] = float(
                            word.get("end_seconds", 0.0)
                        ) + start
                all_segments.extend(segs)
            except Exception:
                continue
    return all_segments


def _reacquire_hypothesis(
    video_path: str,
    audio_path: str,
    video_duration_seconds: float,
    audio_duration_seconds: float,
    hypothesis: OffsetHypothesis,
    model_local_path: str,
    language_hint: str | None,
    ffmpeg_path: str | None,
    evidence_candidates: list[TemporalCandidate] | None = None,
) -> OffsetHypothesis:
    """Verify one offset family using projected, separated audio windows.

    Verification window positions come from evidence-supported regions when
    raw candidates are provided (sparse long-form case); otherwise a fixed
    fraction grid is used as a fallback.
    """
    if evidence_candidates:
        video_windows = build_evidence_verification_windows(
            evidence_candidates,
            hypothesis.median_delta,
            video_duration_seconds,
        )
        if len(video_windows) < 3:
            # Too few independent evidence regions from screening to verify.
            # Fall back to a dense probe of the timeline so content that the
            # coarse screening missed can still be discovered and confirmed.
            video_windows = select_verification_windows(video_duration_seconds)
    else:
        video_windows = select_verification_windows(video_duration_seconds)
    audio_windows = [
        project_audio_window_start(
            video_start, hypothesis.median_delta, audio_duration_seconds
        )
        for video_start in video_windows
    ]
    video_segments = transcribe_media_windows(
        video_path, video_windows, model_local_path,
        language_hint=language_hint, ffmpeg_path=ffmpeg_path,
    )
    audio_segments = transcribe_media_windows(
        audio_path, audio_windows, model_local_path,
        language_hint=language_hint, ffmpeg_path=ffmpeg_path,
    )
    video_occurrences = build_ordered_occurrences(video_segments)
    audio_occurrences = build_ordered_occurrences(audio_segments)
    candidates = _build_temporal_candidates(video_occurrences, audio_occurrences)
    tolerance = max(
        DELTA_CLUSTER_TOLERANCE_SECONDS,
        hypothesis.mad_delta * 3.0,
    )
    projected = [
        candidate for candidate in candidates
        if abs(candidate.delta - hypothesis.median_delta) <= tolerance
    ]
    anchors = _select_monotonic_anchor_chain(projected)
    hypothesis.verification_windows_attempted = len(video_windows)
    return evaluate_hypothesis(hypothesis, anchors, video_duration_seconds)


# =====================================================================
# LAYER 1: synchronize_pair (the fundamental primitive)
# =====================================================================

def synchronize_pair(video_metadata, audio_metadata, *,
                     media_root=None, model_local_path=None,
                     ffmpeg_path=None, language_hint=None,
                     progress_callback=None):
    """Synchronize one video clip to one audio source.

    Returns PairSyncResult. The fundamental primitive.
    Both valid SAME_EVENT and unrelated results are legitimate outputs.
    This function must NOT reject a valid SAME_EVENT merely because
    another audio source is higher quality.
    """
    started = _time.monotonic()
    v_rel = video_metadata.get("relative_path", "")
    a_rel = audio_metadata.get("relative_path", "")
    if media_root:
        v_abs = str(Path(media_root) / v_rel)
        a_abs = str(Path(media_root) / a_rel)
    else:
        v_abs = video_metadata.get("abs_path", v_rel)
        a_abs = audio_metadata.get("abs_path", a_rel)
    v_dur = _duration_seconds(video_metadata)
    a_dur = _duration_seconds(audio_metadata)
    if v_dur <= 0 or a_dur <= 0 or not model_local_path:
        return PairSyncResult(video_path=v_rel, audio_path=a_rel)

    v_windows = select_speech_windows(v_dur)
    a_windows = select_speech_windows(a_dur)

    v_segs = transcribe_media_windows(v_abs, v_windows, model_local_path,
                                      language_hint=language_hint, ffmpeg_path=ffmpeg_path)
    a_segs = transcribe_media_windows(a_abs, a_windows, model_local_path,
                                      language_hint=language_hint, ffmpeg_path=ffmpeg_path)

    v_occs = build_ordered_occurrences(v_segs)
    a_occs = build_ordered_occurrences(a_segs)
    raw_candidates = _build_temporal_candidates(v_occs, a_occs)
    anchors = _select_monotonic_anchor_chain(raw_candidates)

    if not raw_candidates:
        return PairSyncResult(video_path=v_rel, audio_path=a_rel)

    hypotheses = build_offset_hypotheses(raw_candidates)
    selected_hypothesis = None
    if v_dur >= LONG_FORM_DURATION_SECONDS and hypotheses:
        verified_hypotheses = [
            _reacquire_hypothesis(
                v_abs, a_abs, v_dur, a_dur, hypothesis,
                model_local_path, language_hint, ffmpeg_path,
                evidence_candidates=raw_candidates,
            )
            for hypothesis in hypotheses
        ]
        survivors = [hypothesis for hypothesis in verified_hypotheses if hypothesis.survived]
        if survivors:
            selected_hypothesis = max(
                survivors,
                key=lambda hypothesis: (
                    len(hypothesis.verified_anchors),
                    max((a.video_time for a in hypothesis.verified_anchors), default=0.0)
                    - min((a.video_time for a in hypothesis.verified_anchors), default=0.0),
                    hypothesis.initial_score,
                ),
            )
            anchors = selected_hypothesis.verified_anchors
        else:
            return PairSyncResult(
                video_path=v_rel,
                audio_path=a_rel,
                relationship=RELATIONSHIP_SAME_EVENT,
                sync_status="UNRESOLVED",
                confidence=CONFIDENCE_MEDIUM,
                evidence=[{
                    "type": "offset_hypotheses",
                    "hypotheses": [hypothesis.to_dict() for hypothesis in verified_hypotheses],
                    "reason": "NO_LONG_FORM_HYPOTHESIS_SURVIVED",
                }],
                raw_match_count=len(raw_candidates),
                selected_match_count=len(anchors),
                temporal_span_seconds=0.0,
            )

    n_matches = len(anchors)
    if n_matches < MIN_CONTENT_MATCHES:
        return PairSyncResult(
            video_path=v_rel,
            audio_path=a_rel,
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="UNRESOLVED",
            confidence=CONFIDENCE_LOW,
            evidence=[{
                "type": "content_candidates",
                "count": len(raw_candidates),
                "hypotheses": [hypothesis.to_dict() for hypothesis in hypotheses],
            }],
            raw_match_count=len(raw_candidates),
            selected_match_count=n_matches,
        )

    local_alignment_anchors = build_local_alignment_anchors(anchors)
    bootstrap_used = False
    bootstrap_hypotheses: list[dict[str, Any]] = []
    if v_dur >= LONG_FORM_DURATION_SECONDS and len(local_alignment_anchors) < 3:
        unique_phrases_raw = len({c.phrase_id for c in raw_candidates})
        if unique_phrases_raw >= COARSE_OFFSET_BOOTSTRAP_MIN_PHRASES:
            coarse_hyps = _compute_coarse_offset_hypotheses(
                raw_candidates, v_dur, a_dur,
            )
            bootstrap_hypotheses = coarse_hyps
            for coarse in coarse_hyps[:MAX_OFFSET_HYPOTHESES]:
                boot_hyp = OffsetHypothesis(
                    median_delta=coarse["median_delta"],
                    mad_delta=coarse["mad"],
                    raw_support=coarse["support"],
                    unique_phrases=coarse["unique_phrases"],
                    window_diversity=0,
                    video_span_seconds=coarse["video_span"],
                    audio_span_seconds=coarse["audio_span"],
                    initial_score=coarse["score"],
                )
                boot_hyp = _reacquire_hypothesis(
                    v_abs, a_abs, v_dur, a_dur, boot_hyp,
                    model_local_path, language_hint, ffmpeg_path,
                    evidence_candidates=raw_candidates,
                )
                # Surface the reacquisition outcome (survival, verified window
                # counts) in the diagnostic evidence for traceability.
                bootstrap_hypotheses = [
                    h if h.get("median_delta") != boot_hyp.median_delta
                    else boot_hyp.to_dict()
                    for h in bootstrap_hypotheses
                ]
                if boot_hyp.survived:
                    anchors = boot_hyp.verified_anchors
                    local_alignment_anchors = (
                        build_sparse_local_alignment_anchors(anchors)
                        or build_local_alignment_anchors(anchors)
                    )
                    selected_hypothesis = boot_hyp
                    bootstrap_used = True
                    break
    if v_dur >= LONG_FORM_DURATION_SECONDS and len(local_alignment_anchors) < 3:
        return PairSyncResult(
            video_path=v_rel,
            audio_path=a_rel,
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="UNRESOLVED",
            confidence=CONFIDENCE_LOW,
            evidence=[{
                "type": "local_alignment",
                "reason": "INSUFFICIENT_INDEPENDENT_WINDOWS",
                "window_count": len(local_alignment_anchors),
                "bootstrap_attempted": bootstrap_used,
                "bootstrap_hypotheses": bootstrap_hypotheses,
            }],
            raw_match_count=len(raw_candidates),
            selected_match_count=n_matches,
        )
    if selected_hypothesis is not None:
        local_alignment_anchors = _refine_local_alignment_anchors(
            v_abs, a_abs, a_dur, selected_hypothesis,
            local_alignment_anchors, ffmpeg_path,
        )
    model = fit_affine_model(local_alignment_anchors or anchors, v_dur)
    confidence = _compute_confidence(model, n_matches)
    retime, classification = _decide_retime(model, confidence)

    span = model.temporal_span_seconds

    if (not model.consensus_valid
            or model.drift_status != DRIFT_STATUS_RESOLVED):
        return PairSyncResult(
            video_path=v_rel,
            audio_path=a_rel,
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="UNRESOLVED",
            intercept_a=None,
            slope_b=None,
            drift_ms_per_hour=None,
            predicted_end_drift_ms=None,
            predicted_end_drift_frames=None,
            audio_speed_percent=None,
            confidence=confidence,
            method="content_affine",
            evidence=[{
                "type": "content_anchors",
                "raw_count": len(raw_candidates),
                "selected_count": n_matches,
                "tokens": [a.video_token for a in anchors[:10]],
            }],
            uncertainty_ms=_compute_uncertainty_ms(model),
            retime_recommended=False,
            retime_classification=RETIME_CLASSIFICATION_UNRESOLVED,
            anchors=anchors,
            affine_model=model,
            raw_match_count=len(raw_candidates),
            selected_match_count=n_matches,
            temporal_span_seconds=span,
            local_alignment_anchors=local_alignment_anchors,
        )

    return PairSyncResult(
        video_path=v_rel, audio_path=a_rel,
        relationship=RELATIONSHIP_SAME_EVENT,
        sync_status="RESOLVED",
        intercept_a=model.intercept_a,
        slope_b=model.slope_b,
        drift_ms_per_hour=model.drift_ms_per_hour,
        predicted_end_drift_ms=model.predicted_end_drift_ms,
        predicted_end_drift_frames=model.predicted_end_drift_frames,
        audio_speed_percent=model.audio_speed_percent,
        confidence=confidence,
        method="content_affine",
        evidence=[{"type": "content_anchors", "count": n_matches,
                   "tokens": [a.video_token for a in anchors[:10]]}],
        uncertainty_ms=_compute_uncertainty_ms(model),
        retime_recommended=retime,
        retime_classification=classification,
        anchors=anchors,
        affine_model=model,
        raw_match_count=len(raw_candidates),
        selected_match_count=n_matches,
        temporal_span_seconds=span,
        local_alignment_anchors=local_alignment_anchors,
    )


# =====================================================================
# LAYER 2: Session grouping
# =====================================================================

def _video_context_group(relative_path: str) -> str:
    parts = Path(relative_path).parts
    if "PRIVATE" in parts:
        private_index = parts.index("PRIVATE")
        if private_index > 0:
            return "/".join(parts[:private_index])
    return "/".join(parts[:-1]) or Path(relative_path).stem


def _audio_context_group(relative_path: str) -> str:
    parts = Path(relative_path).parts
    return "/".join(parts[:-1]) or Path(relative_path).stem


def _context_group_for_media(meta: dict[str, Any]) -> str:
    relative_path = meta.get("relative_path", "")
    if _is_video_file(meta):
        return _video_context_group(relative_path)
    return _audio_context_group(relative_path)


def discover_session_hypotheses(
    metadata_results: list[dict[str, Any]],
) -> tuple[list[SessionHypothesis], dict[str, list[str]], int, int]:
    """Build bounded logical-session hypotheses from physical media groups.

    Physical directory context narrows the search, but only pairwise content
    evidence can promote a hypothesis beyond ``PLAUSIBLE``.
    """
    videos = [item for item in metadata_results if _is_video_file(item)]
    audios = [item for item in metadata_results if _is_audio_file(item)]
    video_groups: dict[str, list[dict[str, Any]]] = {}
    audio_groups: dict[str, list[dict[str, Any]]] = {}
    physical_groups: dict[str, list[str]] = {}
    for item in videos:
        group = _context_group_for_media(item)
        video_groups.setdefault(group, []).append(item)
        physical_groups.setdefault(group, []).append(item.get("relative_path", ""))
    for item in audios:
        group = _context_group_for_media(item)
        audio_groups.setdefault(group, []).append(item)
        physical_groups.setdefault(group, []).append(item.get("relative_path", ""))

    hypotheses: list[SessionHypothesis] = []
    for audio_group, group_audios in sorted(audio_groups.items()):
        audio_duration = max((_duration_seconds(item) for item in group_audios), default=0.0)
        if audio_duration <= 0:
            continue
        compatible_videos: list[dict[str, Any]] = []
        context_groups = [audio_group]
        evidence: list[dict[str, Any]] = []
        for video_group, group_videos in sorted(video_groups.items()):
            video_duration = max(
                (_duration_seconds(item) for item in group_videos), default=0.0
            )
            if video_duration <= 0:
                continue
            ratio = audio_duration / video_duration
            if ratio < 0.3 or ratio > 3.0:
                continue
            compatible_videos.extend(group_videos)
            context_groups.append(video_group)
            evidence.append({
                "type": "duration_compatibility",
                "video_group": video_group,
                "audio_group": audio_group,
                "duration_ratio": round(ratio, 4),
                "cross_directory": video_group != audio_group,
            })
        if not compatible_videos:
            continue
        representative = max(
            group_audios,
            key=lambda item: (
                _score_audio_for_master(item),
                -len(item.get("relative_path", "")),
            ),
        )
        hypothesis_id = f"logical_session_{len(hypotheses) + 1:03d}"
        hypotheses.append(SessionHypothesis(
            hypothesis_id=hypothesis_id,
            video_candidates=sorted(
                compatible_videos, key=lambda item: item.get("relative_path", "")
            ),
            audio_candidates=sorted(
                group_audios, key=lambda item: item.get("relative_path", "")
            ),
            context_groups=context_groups,
            cheap_evidence=evidence,
            confidence=CONFIDENCE_MEDIUM,
            status=HYPOTHESIS_PLAUSIBLE,
            representative_audio=representative,
        ))
    global_count = len(videos) * len(audios)
    reduced_count = sum(len(hypothesis.video_candidates) for hypothesis in hypotheses)
    return hypotheses, physical_groups, global_count, reduced_count


def _session_id_from_path(relative_path):
    parts = Path(relative_path).parts
    if len(parts) >= 2:
        return parts[-2]
    return Path(relative_path).stem or "unknown"


def group_into_sessions(metadata_results):
    """Group metadata into recording/event sessions by directory context.

    Returns dict[session_id, list[metadata]].
    """
    by_session = {}
    for meta in metadata_results:
        sid = _session_id_from_path(meta.get("relative_path", ""))
        by_session.setdefault(sid, []).append(meta)
    return by_session


# =====================================================================
# LAYER 2: Clock model sharing across clips from same device
# =====================================================================

def _should_share_clock_model(pairwise_results, min_consistent=2):
    """Decide whether clips share a camera device clock model.

    Returns (should_share, shared_slope, drift_status).
    Only share when evidence from multiple clips is consistent.
    """
    slopes = []
    for pr in pairwise_results:
        if pr.affine_model and pr.confidence in (CONFIDENCE_HIGH, CONFIDENCE_MEDIUM):
            slopes.append(pr.affine_model.slope_b)
    if len(slopes) < min_consistent:
        return False, 1.0, DRIFT_STATUS_UNRESOLVED
    mean_slope = sum(slopes) / len(slopes)
    spread = max(slopes) - min(slopes)
    if spread < 0.0001:
        return True, mean_slope, DRIFT_STATUS_RESOLVED
    cv = abs(spread / mean_slope) if abs(mean_slope) > 1e-10 else 0.0
    if cv < 0.05:
        return True, mean_slope, DRIFT_STATUS_RESOLVED
    return False, 1.0, DRIFT_STATUS_UNRESOLVED


# =====================================================================
# LAYER 2: Audio master selection
# =====================================================================

def _score_audio_for_master(meta):
    """Score an audio source for suitability as edit master.

    Higher = better. Uses quality metrics and channel count.
    This is independent of pair confidence.
    """
    q = meta.get("quality_summary", {})
    m = q.get("metrics", {}) if isinstance(q, dict) else {}
    rms = m.get("rms_db") or -80.0
    noise = m.get("noise_db") or -80.0
    clip = m.get("clipping_ratio") or 0.0
    silence = m.get("silence_ratio") or 0.0
    audio_info = meta.get("audio", {}) if isinstance(meta.get("audio"), dict) else {}
    ch = audio_info.get("channel_count", 1)
    sr = audio_info.get("sample_rate", 48000)
    score = rms
    score += 3.0 * (ch - 1)
    score += 2.0 * min(sr / 48000.0, 2.0)
    score -= 5.0 * clip
    score -= 10.0 * silence
    score -= max(0, (noise + 60)) * 0.1
    return score


def _select_master_audio(audio_results, pairwise_by_audio=None):
    """Select best audio master by quality evidence.

    Returns (master_path, reasons).
    """
    if not audio_results:
        return None, []
    scored = []
    for meta in audio_results:
        s = _score_audio_for_master(meta)
        scored.append((s, meta))
    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0][1]
    best_rel = best.get("relative_path", "")
    reasons = [{"type": "quality_score", "score": round(scored[0][0], 2)}]
    if len(scored) > 1:
        reasons.append({
            "type": "alternates_available",
            "count": len(scored) - 1,
            "alternates": [s[1].get("relative_path", "") for s in scored[1:]],
        })
    return best_rel, reasons


# =====================================================================
# LAYER 2: Session assembly
# =====================================================================

def assemble_session(metadata_results, *,
                     model_local_path=None, ffmpeg_path=None,
                     language_hint=None, progress_callback=None,
                     transient_dir=None,
                     pairwise_results: list[PairSyncResult] | None = None,
                     session_id: str | None = None):
    """Assemble a session-level sync graph from a set of media metadata.

    This is the main Layer 2 entry point.

    1. Accept media already assigned to one logical session
    2. For that session, run bounded pairwise sync when requested
    3. Build sync graph (nodes + edges)
    4. Select master audio using quality evidence
    5. Optionally share clock-rate model across clips from same device
    6. Map each clip to session timeline

    Returns SessionSyncResult.
    """
    started = _time.monotonic()

    if not metadata_results:
        return SessionSyncResult(session_id="empty")

    session_id = session_id or _session_id_from_path(
        metadata_results[0].get("relative_path", "")
    )
    session_items = metadata_results

    videos = [m for m in session_items if _is_video_file(m)]
    audios = [m for m in session_items if _is_audio_file(m)]

    if not videos:
        return SessionSyncResult(session_id=session_id)

    candidates = reduce_candidates(session_items)

    run_pairwise = pairwise_results is None
    if pairwise_results is None:
        pairwise_results = []
    if run_pairwise and model_local_path:
        for v, a in candidates:
            pr = synchronize_pair(
                v, a,
                media_root=None,
                model_local_path=model_local_path,
                ffmpeg_path=ffmpeg_path,
                language_hint=language_hint,
                progress_callback=progress_callback,
            )
            pairwise_results.append(pr)

    edges = []
    by_audio = {}
    for pr in pairwise_results:
        if pr.sync_status == "RESOLVED":
            edge = SyncEdge(
                source=pr.video_path,
                target=pr.audio_path,
                relationship=pr.relationship,
                intercept_a=pr.intercept_a,
                slope_b=pr.slope_b,
                confidence=pr.confidence,
                drift_status=pr.affine_model.drift_status if pr.affine_model else DRIFT_STATUS_UNRESOLVED,
                evidence=pr.evidence,
                temporal_span_seconds=pr.affine_model.temporal_span_seconds if pr.affine_model else 0.0,
                retime_recommended=pr.retime_recommended,
                audio_speed_percent=pr.audio_speed_percent,
                predicted_end_drift_frames=pr.predicted_end_drift_frames,
            )
            edges.append(edge)
            by_audio.setdefault(pr.audio_path, []).append(pr)

    master_audio, master_reasons = _select_master_audio(audios, by_audio)

    all_audio_paths = [a.get("relative_path", "") for a in audios]
    alternate_audio = [p for p in all_audio_paths if p and p != master_audio]

    shared, shared_slope, shared_drift = _should_share_clock_model(pairwise_results)

    synchronized_clips = []
    unresolved_clips = []
    for v in videos:
        v_rel = v.get("relative_path", "")
        best_pr = None
        for pr in pairwise_results:
            if pr.video_path == v_rel and pr.sync_status == "RESOLVED":
                if best_pr is None or pr.confidence == CONFIDENCE_HIGH:
                    best_pr = pr
                elif pr.confidence == CONFIDENCE_MEDIUM and best_pr.confidence != CONFIDENCE_HIGH:
                    best_pr = pr
        if best_pr is None:
            unresolved_clips.append(v_rel)
            continue
        pos = best_pr.intercept_a
        if shared and shared_drift == DRIFT_STATUS_RESOLVED:
            slope = shared_slope
        else:
            slope = best_pr.slope_b
        synchronized_clips.append(SynchronizedClip(
            video_path=best_pr.video_path,
            audio_reference=best_pr.audio_path,
            session_position_seconds=round(pos, 4),
            intercept_a=best_pr.intercept_a,
            slope_b=slope,
            confidence=best_pr.confidence,
            retime_recommended=best_pr.retime_recommended,
            audio_speed_percent=best_pr.audio_speed_percent,
            predicted_end_drift_frames=best_pr.predicted_end_drift_frames,
            unresolved=False,
        ))

    all_confidences = [c.confidence for c in synchronized_clips]
    if CONFIDENCE_HIGH in all_confidences:
        session_conf = CONFIDENCE_HIGH
    elif CONFIDENCE_MEDIUM in all_confidences:
        session_conf = CONFIDENCE_MEDIUM
    elif all_confidences:
        session_conf = CONFIDENCE_LOW
    else:
        session_conf = CONFIDENCE_UNRESOLVED

    elapsed = _time.monotonic() - started

    return SessionSyncResult(
        session_id=session_id,
        master_audio=master_audio,
        alternate_audio=alternate_audio,
        synchronized_clips=synchronized_clips,
        unresolved_clips=unresolved_clips,
        edges=edges,
        clock_model_shared=shared,
        shared_slope_b=shared_slope,
        shared_drift_status=shared_drift,
        confidence=session_conf,
        processing_seconds=round(elapsed, 2),
    )


def assemble_project_sessions(
    metadata_results: list[dict[str, Any]],
    *,
    model_local_path: str | None = None,
    ffmpeg_path: str | None = None,
    language_hint: str | None = None,
    progress_callback: Callable[..., Any] | None = None,
) -> ProjectSyncResult:
    """Discover and assemble isolated logical sessions for a project root."""
    started = _time.monotonic()
    hypotheses, physical_groups, global_count, reduced_count = (
        discover_session_hypotheses(metadata_results)
    )
    project = ProjectSyncResult(
        hypotheses=hypotheses,
        physical_groups=physical_groups,
        pair_candidates_before_reduction=global_count,
        pair_candidates_after_reduction=reduced_count,
        global_cartesian_pairing_used=False,
    )
    if not model_local_path:
        project.unresolved_media = [
            item.get("relative_path", "")
            for item in metadata_results
            if _is_video_file(item) or _is_audio_file(item)
        ]
        project.processing_seconds = round(_time.monotonic() - started, 2)
        return project

    pair_results_by_hypothesis: dict[str, list[PairSyncResult]] = {}
    best_for_video: dict[str, tuple[tuple[int, float, float], str]] = {}
    confidence_rank = {
        CONFIDENCE_HIGH: 3,
        CONFIDENCE_MEDIUM: 2,
        CONFIDENCE_LOW: 1,
        CONFIDENCE_UNRESOLVED: 0,
    }
    for hypothesis in hypotheses:
        representative = hypothesis.representative_audio
        if representative is None:
            hypothesis.status = HYPOTHESIS_REJECTED
            continue
        results: list[PairSyncResult] = []
        for video in hypothesis.video_candidates:
            result = synchronize_pair(
                video,
                representative,
                model_local_path=model_local_path,
                ffmpeg_path=ffmpeg_path,
                language_hint=language_hint,
                progress_callback=progress_callback,
            )
            results.append(result)
            project.pair_syncs_executed += 1
            if result.sync_status != "RESOLVED":
                continue
            score = (
                confidence_rank.get(result.confidence, 0),
                result.temporal_span_seconds,
                result.selected_match_count,
            )
            video_path = result.video_path
            current = best_for_video.get(video_path)
            if current is None or score > current[0]:
                best_for_video[video_path] = (score, hypothesis.hypothesis_id)
        pair_results_by_hypothesis[hypothesis.hypothesis_id] = results

    assigned_audio: set[str] = set()
    for hypothesis in hypotheses:
        hypothesis_results = pair_results_by_hypothesis.get(
            hypothesis.hypothesis_id, []
        )
        selected_results = [
            result for result in hypothesis_results
            if result.sync_status == "RESOLVED"
            and best_for_video.get(result.video_path, (None, None))[1]
            == hypothesis.hypothesis_id
        ]
        if not selected_results:
            hypothesis.status = (
                HYPOTHESIS_REJECTED if hypothesis_results else HYPOTHESIS_UNRESOLVED
            )
            continue
        hypothesis.status = HYPOTHESIS_CONFIRMED
        session_videos = [
            video for video in hypothesis.video_candidates
            if video.get("relative_path", "") in {
                result.video_path for result in selected_results
            }
        ]
        session_items = session_videos + hypothesis.audio_candidates
        project.sessions.append(assemble_session(
            session_items,
            pairwise_results=selected_results,
            session_id=hypothesis.hypothesis_id,
        ))
        assigned_audio.update(
            item.get("relative_path", "") for item in hypothesis.audio_candidates
        )

    assigned_videos = {
        clip.video_path
        for session in project.sessions
        for clip in session.synchronized_clips
    }
    project.unresolved_media = [
        item.get("relative_path", "")
        for item in metadata_results
        if (
            _is_video_file(item)
            and item.get("relative_path", "") not in assigned_videos
        ) or (
            _is_audio_file(item)
            and item.get("relative_path", "") not in assigned_audio
        )
    ]
    project.processing_seconds = round(_time.monotonic() - started, 2)
    return project
