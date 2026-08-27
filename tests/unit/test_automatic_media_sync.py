"""Focused tests for CID Automatic Media Sync engine.

Ordered occurrences, content matching, affine model, confidence,
retime decisions, manifest serialization, session assembly.
No real media fixtures.
"""

from __future__ import annotations

import tempfile
import wave
from pathlib import Path

import numpy as np
import pytest
import scripts.local_media_agent.automatic_media_sync as sync_module

from scripts.local_media_agent.automatic_media_sync import (
    COARSE_OFFSET_BOOTSTRAP_MIN_PHRASES,
    MIN_CONTENT_MATCHES,
    MIN_DRIFT_VALIDATION_INLIERS,
    RETIME_THRESHOLD_FRAMES,
    RETIME_FPS,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_UNRESOLVED,
    DRIFT_STATUS_RESOLVED,
    DRIFT_STATUS_UNRESOLVED,
    HYPOTHESIS_PLAUSIBLE,
    RETIME_CLASSIFICATION_AFFINE,
    RETIME_CLASSIFICATION_CONSTANT,
    RETIME_CLASSIFICATION_UNRESOLVED,
    RELATIONSHIP_SAME_EVENT,
    RELATIONSHIP_UNRESOLVED,
    SYNC_ENGINE_SCHEMA_VERSION,
    SESSION_SCHEMA_VERSION,
    AffineModel,
    ContentAnchor,
    LocalAlignmentAnchor,
    OffsetHypothesis,
    OrderedOccurrence,
    PairSyncResult,
    SyncEdge,
    SynchronizedClip,
    SessionSyncResult,
    _compute_confidence,
    _compute_uncertainty_ms,
    _build_temporal_candidates,
    _decide_retime,
    _refine_local_alignment_anchors,
    _is_distinctive,
    _is_video_file,
    _is_audio_file,
    _robust_outlier_filter,
    _normalize_token,
    _ols_fit,
    _r_squared,
    _residuals_ms,
    _session_id_from_path,
    _should_share_clock_model,
    _score_audio_for_master,
    _select_master_audio,
    build_ordered_occurrences,
    build_offset_hypotheses,
    build_evidence_verification_windows,
    build_local_alignment_anchors,
    build_sparse_local_alignment_anchors,
    assemble_project_sessions,
    discover_session_hypotheses,
    evaluate_hypothesis,
    fit_affine_model,
    long_form_minimum_span,
    match_content_anchors,
    project_audio_window_start,
    refine_local_acoustic_offset,
    reduce_candidates,
    select_verification_windows,
    select_speech_windows,
    group_into_sessions,
    assemble_session,
)


# =====================================================================
# ORDERED OCCURRENCES
# =====================================================================

class TestOrderedOccurrencesPreserved:
    def test_duplicate_tokens_produce_multiple_entries(self):
        segments = [
            {"text": "estamos listos para empezar", "start_seconds": 0.0,
             "end_seconds": 2.0, "source_start_seconds": 0.0,
             "source_end_seconds": 2.0},
            {"text": "creo que estamos listos ya", "start_seconds": 5.0,
             "end_seconds": 7.0, "source_start_seconds": 5.0,
             "source_end_seconds": 7.0},
        ]
        occs = build_ordered_occurrences(segments)
        estamos = [o for o in occs if o.token == "estamos"]
        assert len(estamos) == 2
        assert estamos[0].occurrence_index == 0
        assert estamos[1].occurrence_index == 1
        assert estamos[0].absolute_time < estamos[1].absolute_time


class TestNoOccurrenceOverwrite:
    def test_first_occurrence_wins_for_matching(self):
        segs_a = [
            {"text": "hola estamos bien", "start_seconds": 0.0, "end_seconds": 1.0,
             "source_start_seconds": 0.0, "source_end_seconds": 1.0},
            {"text": "otra vez estamos aqui", "start_seconds": 10.0,
             "end_seconds": 11.0, "source_start_seconds": 10.0,
             "source_end_seconds": 11.0},
        ]
        segs_b = [
            {"text": "hola que tal", "start_seconds": 0.0, "end_seconds": 1.0,
             "source_start_seconds": 0.0, "source_end_seconds": 1.0},
            {"text": "otra vez hola", "start_seconds": 10.0, "end_seconds": 11.0,
             "source_start_seconds": 10.0, "source_end_seconds": 11.0},
        ]
        occs_a = build_ordered_occurrences(segs_a)
        occs_b = build_ordered_occurrences(segs_b)
        anchors = match_content_anchors(occs_a, occs_b)
        hola_anchors = [a for a in anchors if a.video_token == "hola"]
        assert len(hola_anchors) == 1
        assert hola_anchors[0].video_time < 2.0
        assert hola_anchors[0].audio_time < 2.0


# =====================================================================
# CONTENT MATCHING
# =====================================================================

class TestContentAnchorMatching:
    def test_shared_distinctive_tokens_produce_anchors(self):
        v_segs = [
            {"text": "presidente duque hablo sobre economia", "start_seconds": 0.0,
             "end_seconds": 3.0, "source_start_seconds": 0.0,
             "source_end_seconds": 3.0},
        ]
        a_segs = [
            {"text": "el presidente duque hablo de economia hoy", "start_seconds": 5.0,
             "end_seconds": 8.0, "source_start_seconds": 5.0,
             "source_end_seconds": 8.0},
        ]
        v_occs = build_ordered_occurrences(v_segs)
        a_occs = build_ordered_occurrences(a_segs)
        anchors = match_content_anchors(v_occs, a_occs)
        tokens = {a.video_token for a in anchors}
        assert "presidente" in tokens
        assert "duque" in tokens
        assert "hablo" in tokens
        assert "economia" in tokens

    def test_stopwords_excluded(self):
        assert not _is_distinctive("el")
        assert not _is_distinctive("la")
        assert not _is_distinctive("the")
        assert _is_distinctive("presidente")
        assert _is_distinctive("economia")

    def test_short_tokens_excluded(self):
        assert not _is_distinctive("a")


class TestStopwordFalseMatchRejection:
    def test_only_stopwords_produce_no_anchors(self):
        v_segs = [{"text": "el la de en que es", "start_seconds": 0.0,
                   "end_seconds": 1.0, "source_start_seconds": 0.0,
                   "source_end_seconds": 1.0}]
        a_segs = [{"text": "de el en la que es", "start_seconds": 0.0,
                   "end_seconds": 1.0, "source_start_seconds": 0.0,
                   "source_end_seconds": 1.0}]
        v_occs = build_ordered_occurrences(v_segs)
        a_occs = build_ordered_occurrences(a_segs)
        anchors = match_content_anchors(v_occs, a_occs)
        assert len(anchors) == 0


# =====================================================================
# UNRELATED REJECTION
# =====================================================================

class TestUnrelatedRejection:
    def test_no_shared_tokens_no_anchors(self):
        v_segs = [{"text": "buenos dias senores", "start_seconds": 0.0,
                   "end_seconds": 2.0, "source_start_seconds": 0.0,
                   "source_end_seconds": 2.0}]
        a_segs = [{"text": "weather forecast today sunny", "start_seconds": 0.0,
                   "end_seconds": 2.0, "source_start_seconds": 0.0,
                   "source_end_seconds": 2.0}]
        v_occs = build_ordered_occurrences(v_segs)
        a_occs = build_ordered_occurrences(a_segs)
        anchors = match_content_anchors(v_occs, a_occs)
        assert len(anchors) < MIN_CONTENT_MATCHES

    def test_reduce_candidates_empty_when_no_inputs(self):
        assert reduce_candidates([]) == []

    def test_reduce_candidates_empty_when_no_audio(self):
        result = reduce_candidates([
            {"relative_path": "clip.mp4", "category": "video",
             "duration_seconds": 100.0},
        ])
        assert result == []

    def test_reduce_candidates_pairs_matchable_duration(self):
        result = reduce_candidates([
            {"relative_path": "clip.mp4", "category": "video",
             "duration_seconds": 100.0},
            {"relative_path": "mix.wav", "category": "audio",
             "duration_seconds": 110.0},
        ])
        assert len(result) == 1

    def test_reduce_candidates_rejects_huge_duration_ratio(self):
        result = reduce_candidates([
            {"relative_path": "clip.mp4", "category": "video",
             "duration_seconds": 10.0},
            {"relative_path": "long.wav", "category": "audio",
             "duration_seconds": 100.0},
        ])
        assert result == []


# =====================================================================
# AFFINE MODEL
# =====================================================================

class TestConstantOffsetModel:
    def test_perfect_constant_offset(self):
        anchors = [
            ContentAnchor("a", "a", 10.0, 15.0, 0, 0),
            ContentAnchor("b", "b", 200.0, 205.0, 0, 0),
            ContentAnchor("c", "c", 400.0, 405.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=500.0)
        assert abs(model.slope_b - 1.0) < 1e-6
        assert abs(model.intercept_a - 5.0) < 0.01
        assert model.drift_ms_per_hour == pytest.approx(0.0, abs=0.01)


class TestExternalAudioBeforeVideo:
    def test_negative_intercept(self):
        anchors = [
            ContentAnchor("a", "a", 10.0, 5.0, 0, 0),
            ContentAnchor("b", "b", 100.0, 95.0, 0, 0),
            ContentAnchor("c", "c", 300.0, 295.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=400.0)
        assert model.intercept_a < 0
        assert abs(model.slope_b - 1.0) < 1e-6


class TestExternalAudioAfterVideo:
    def test_positive_intercept(self):
        anchors = [
            ContentAnchor("a", "a", 10.0, 20.0, 0, 0),
            ContentAnchor("b", "b", 100.0, 110.0, 0, 0),
            ContentAnchor("c", "c", 300.0, 310.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=400.0)
        assert model.intercept_a > 0


class TestPositiveClockDrift:
    def test_slope_gt_1(self):
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 600.0, 600.3, 0, 0),
            ContentAnchor("c", "c", 1200.0, 1200.6, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=1500.0)
        assert model.slope_b > 1.0
        assert model.drift_ms_per_hour > 0


class TestNegativeClockDrift:
    def test_slope_lt_1(self):
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 600.0, 599.7, 0, 0),
            ContentAnchor("c", "c", 1200.0, 1199.4, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=1500.0)
        assert model.slope_b < 1.0
        assert model.drift_ms_per_hour < 0


# =====================================================================
# TEMPORAL SPAN
# =====================================================================

class TestInsufficientTemporalSpan:
    def test_drift_unresolved_when_span_too_short(self):
        anchors = [
            ContentAnchor("a", "a", 10.0, 10.0, 0, 0),
            ContentAnchor("b", "b", 20.0, 20.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=100.0)
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED

    def test_drift_resolved_when_span_sufficient(self):
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 500.0, 500.0, 0, 0),
            ContentAnchor("c", "c", 1000.0, 1000.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=1200.0)
        assert model.drift_status == DRIFT_STATUS_RESOLVED


# =====================================================================
# CONFIDENCE
# =====================================================================

class TestConfidenceModel:
    def test_confidence_low_with_few_matches(self):
        anchors = [ContentAnchor("a", "a", 10.0, 10.0, 0, 0)]
        model = fit_affine_model(anchors, video_duration=100.0)
        conf = _compute_confidence(model, n_matches=1)
        assert conf == CONFIDENCE_LOW

    def test_confidence_not_high_from_r_squared_alone(self):
        anchors = [
            ContentAnchor("x", "x", 10.0, 10.5, 0, 0),
            ContentAnchor("y", "y", 20.0, 20.5, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=100.0)
        conf = _compute_confidence(model, n_matches=2)
        assert conf != CONFIDENCE_HIGH

    def test_confidence_medium_with_good_matches_short_span(self):
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 50.0, 50.0, 0, 0),
            ContentAnchor("c", "c", 100.0, 100.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=200.0)
        conf = _compute_confidence(model, n_matches=3)
        assert conf == CONFIDENCE_MEDIUM

    def test_confidence_high_with_wide_span(self):
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 500.0, 500.0, 0, 0),
            ContentAnchor("c", "c", 1000.0, 1000.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=1200.0)
        conf = _compute_confidence(model, n_matches=3)
        assert conf == CONFIDENCE_HIGH

    def test_material_drift_does_not_lower_high_model_confidence(self):
        slope = 1.0 + 3.0 * (1000.0 / RETIME_FPS) / (3600.0 * 1000.0)
        anchors = [
            ContentAnchor(str(i), str(i), time, slope * time, i, i)
            for i, time in enumerate([0.0, 900.0, 1800.0, 2700.0, 3500.0])
        ]
        model = fit_affine_model(anchors, video_duration=3600.0)
        assert model.predicted_end_drift_frames == pytest.approx(3.0)
        assert _compute_confidence(model, n_matches=5) == CONFIDENCE_HIGH

    def test_large_drift_alone_does_not_reduce_confidence(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0001, r_squared=1.0,
            residual_std_ms=1.0, predicted_end_drift_ms=360.0,
            predicted_end_drift_frames=9.0, anchor_count=5,
            anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True, temporal_span_seconds=3500.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        assert _compute_confidence(model, n_matches=5) == CONFIDENCE_HIGH

    def test_high_residual_still_lowers_confidence(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0001, r_squared=0.99,
            residual_std_ms=201.0, predicted_end_drift_ms=360.0,
            predicted_end_drift_frames=9.0, anchor_count=5,
            anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True, temporal_span_seconds=3500.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        assert _compute_confidence(model, n_matches=5) == CONFIDENCE_MEDIUM


# =====================================================================
# RETIME POLICY
# =====================================================================

class TestRetimeHighConfidenceDrift:
    def test_retime_recommended_when_above_threshold(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0001,
            r_squared=0.9999, residual_std_ms=10.0,
            predicted_end_drift_ms=150.0, predicted_end_drift_frames=3.75,
            audio_speed_percent=100.01, anchor_count=5,
            anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True,
            temporal_span_seconds=3000.0, drift_status=DRIFT_STATUS_RESOLVED,
        )
        retime, classification = _decide_retime(model, CONFIDENCE_HIGH)
        assert retime is True
        assert classification == RETIME_CLASSIFICATION_AFFINE

    def test_sixty_minute_three_frame_drift_is_material(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0000333333,
            r_squared=0.9999, residual_std_ms=10.0,
            predicted_end_drift_ms=120.0, predicted_end_drift_frames=3.0,
            audio_speed_percent=100.003333, anchor_count=5,
            anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True, temporal_span_seconds=3500.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        assert _compute_confidence(model, n_matches=5) == CONFIDENCE_HIGH
        assert _decide_retime(model, CONFIDENCE_HIGH) == (
            True, RETIME_CLASSIFICATION_AFFINE
        )

    def test_sixty_minute_half_frame_drift_is_not_material(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0000055556,
            r_squared=0.9999, residual_std_ms=10.0,
            predicted_end_drift_ms=20.0, predicted_end_drift_frames=0.5,
            audio_speed_percent=100.000556, anchor_count=5,
            anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True, temporal_span_seconds=3500.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        assert _compute_confidence(model, n_matches=5) == CONFIDENCE_HIGH
        assert _decide_retime(model, CONFIDENCE_HIGH) == (
            False, RETIME_CLASSIFICATION_CONSTANT
        )

    def test_low_confidence_material_drift_does_not_retime(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.0001,
            r_squared=0.5, residual_std_ms=400.0,
            predicted_end_drift_ms=360.0, predicted_end_drift_frames=9.0,
            audio_speed_percent=100.01, anchor_count=2,
            anchor_count_input=5, anchor_count_inliers=2,
            anchor_count_rejected=3,
            consensus_valid=True, temporal_span_seconds=3500.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        confidence = _compute_confidence(model, n_matches=2)
        assert confidence == CONFIDENCE_LOW
        assert _decide_retime(model, confidence)[0] is False


class TestRetimeSubThreshold:
    def test_no_retime_when_below_threshold(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.00001,
            r_squared=0.999, residual_std_ms=50.0,
            predicted_end_drift_ms=15.0, predicted_end_drift_frames=0.375,
            audio_speed_percent=100.001, anchor_count=3,
            anchor_count_input=3, anchor_count_inliers=3,
            consensus_valid=True,
            temporal_span_seconds=2000.0, drift_status=DRIFT_STATUS_RESOLVED,
        )
        retime, classification = _decide_retime(model, CONFIDENCE_HIGH)
        assert retime is False
        assert classification == RETIME_CLASSIFICATION_CONSTANT


class TestRetimeUncertainSlope:
    def test_no_retime_when_drift_unresolved(self):
        model = AffineModel(
            intercept_a=0.0, slope_b=1.00005,
            r_squared=0.95, residual_std_ms=100.0,
            predicted_end_drift_ms=90.0, predicted_end_drift_frames=2.25,
            audio_speed_percent=100.005, anchor_count=3,
            anchor_count_input=3, anchor_count_inliers=3,
            consensus_valid=True,
            temporal_span_seconds=60.0, drift_status=DRIFT_STATUS_UNRESOLVED,
        )
        retime, classification = _decide_retime(model, CONFIDENCE_MEDIUM)
        assert retime is False
        assert classification == RETIME_CLASSIFICATION_CONSTANT


# =====================================================================
# UNCERTAINTY
# =====================================================================

class TestUncertaintyComputation:
    def test_minimum_uncertainty(self):
        model = AffineModel(intercept_a=0.0, slope_b=1.0, residual_std_ms=1.0)
        assert _compute_uncertainty_ms(model) >= 50.0

    def test_proportional_uncertainty(self):
        model = AffineModel(intercept_a=0.0, slope_b=1.0, residual_std_ms=50.0)
        assert _compute_uncertainty_ms(model) == pytest.approx(100.0)


# =====================================================================
# MANIFEST SERIALIZATION
# =====================================================================

class TestManifestSerialization:
    def test_to_manifest_entry_has_required_keys(self):
        result = PairSyncResult(
            video_path="test.mp4", audio_path="mix.wav",
            confidence=CONFIDENCE_HIGH, sync_status="RESOLVED",
            intercept_a=-5.0, slope_b=1.00003,
            retime_recommended=True,
            retime_classification=RETIME_CLASSIFICATION_AFFINE,
            audio_speed_percent=100.003,
        )
        entry = result.to_manifest_entry()
        assert "sync_method" in entry
        assert "offset_seconds" in entry
        assert "slope_b" in entry
        assert "confidence" in entry
        assert "retime_recommended" in entry
        assert "audio_speed_percent" in entry

    def test_to_dict_schema_version(self):
        result = PairSyncResult(video_path="x.mp4", audio_path="y.wav")
        d = result.to_dict()
        assert d["schema_version"] == SYNC_ENGINE_SCHEMA_VERSION


class TestConstantOffsetBackwardCompat:
    def test_manifest_when_no_drift(self):
        model = AffineModel(
            intercept_a=-12.0, slope_b=1.0,
            r_squared=1.0, residual_std_ms=1.0,
            drift_status=DRIFT_STATUS_RESOLVED,
            anchor_count=5, anchor_count_input=5, anchor_count_inliers=5,
            consensus_valid=True, temporal_span_seconds=3000.0,
        )
        retime, cls = _decide_retime(model, CONFIDENCE_HIGH)
        assert retime is False
        assert cls == RETIME_CLASSIFICATION_CONSTANT
        result = PairSyncResult(
            video_path="v.mp4", audio_path="a.wav",
            intercept_a=-12.0, slope_b=1.0,
            retime_recommended=retime, retime_classification=cls,
            audio_speed_percent=100.0,
        )
        entry = result.to_manifest_entry()
        assert entry["audio_speed_percent"] == 100.0
        assert entry["retime_recommended"] is False


# =====================================================================
# SPEECH WINDOWS
# =====================================================================

class TestSpeechWindowSelection:
    def test_short_clip_single_window(self):
        windows = select_speech_windows(15.0, has_scratch_audio=True)
        assert windows == [0.0]

    def test_long_clip_five_windows(self):
        windows = select_speech_windows(300.0, has_scratch_audio=True)
        assert len(windows) == 5
        assert windows[0] == 0.0
        assert windows[-1] > 250.0

    def test_windows_within_bounds(self):
        dur = 3600.0
        windows = select_speech_windows(dur)
        for w in windows:
            assert 0.0 <= w <= dur - 30.0


# =====================================================================
# AFFINE MODEL TO DICT
# =====================================================================

class TestAffineModelToDict:
    def test_affine_serialized_in_result(self):
        model = AffineModel(
            intercept_a=-11.8393, slope_b=1.00003398,
            r_squared=0.999999, residual_std_ms=3.0,
            drift_status=DRIFT_STATUS_RESOLVED,
            anchor_count=3, temporal_span_seconds=3000.0,
            drift_ms_per_hour=0.12,
        )
        result = PairSyncResult(
            video_path="v.mp4", audio_path="a.wav",
            intercept_a=-11.8393, slope_b=1.00003398,
            affine_model=model,
        )
        d = result.to_dict()
        assert "affine" in d
        assert d["affine"]["anchor_count"] == 3
        assert d["affine"]["drift_status"] == "RESOLVED"


# =====================================================================
# SESSION-LEVEL SYNTHETIC TESTS
# =====================================================================

class TestSessionGrouping:
    def test_group_into_sessions_by_directory(self):
        items = [
            {"relative_path": "event1/CAM_A.mp4", "category": "video",
             "duration_seconds": 100.0},
            {"relative_path": "event1/CAM_B.mp4", "category": "video",
             "duration_seconds": 80.0},
            {"relative_path": "event2/CAM_C.mp4", "category": "video",
             "duration_seconds": 60.0},
        ]
        sessions = group_into_sessions(items)
        assert len(sessions) == 2
        assert "event1" in sessions
        assert "event2" in sessions
        assert len(sessions["event1"]) == 2


class TestSessionIdFromPath:
    def test_extracts_parent_directory(self):
        assert _session_id_from_path("event1/CAM_A.mp4") == "event1"

    def test_falls_back_to_stem(self):
        assert _session_id_from_path("single_file.mp4") == "single_file"


class TestClockModelSharing:
    def test_share_when_consistent_slopes(self):
        pr1 = PairSyncResult(
            video_path="a.mp4", audio_path="mix.wav",
            affine_model=AffineModel(intercept_a=0.0, slope_b=1.00003, anchor_count=5,
                                     temporal_span_seconds=3000.0),
            confidence=CONFIDENCE_HIGH,
        )
        pr2 = PairSyncResult(
            video_path="b.mp4", audio_path="mix.wav",
            affine_model=AffineModel(intercept_a=0.0, slope_b=1.00004, anchor_count=4,
                                     temporal_span_seconds=2500.0),
            confidence=CONFIDENCE_HIGH,
        )
        shared, slope, drift = _should_share_clock_model([pr1, pr2])
        assert shared is True
        assert abs(slope - 1.000035) < 0.00001

    def test_no_share_when_inconsistent(self):
        pr1 = PairSyncResult(
            video_path="a.mp4", audio_path="mix.wav",
            affine_model=AffineModel(intercept_a=0.0, slope_b=1.10, anchor_count=5,
                                     temporal_span_seconds=3000.0),
            confidence=CONFIDENCE_HIGH,
        )
        pr2 = PairSyncResult(
            video_path="b.mp4", audio_path="mix.wav",
            affine_model=AffineModel(intercept_a=0.0, slope_b=0.90, anchor_count=4,
                                     temporal_span_seconds=2500.0),
            confidence=CONFIDENCE_HIGH,
        )
        shared, slope, drift = _should_share_clock_model([pr1, pr2])
        assert shared is False

    def test_no_share_with_insufficient_evidence(self):
        shared, slope, drift = _should_share_clock_model([])
        assert shared is False


class TestMasterAudioSelection:
    def test_selects_highest_quality_audio(self):
        items = [
            {"relative_path": "stereo_mix.wav", "category": "audio",
             "duration_seconds": 300.0,
             "audio": {"channel_count": 2, "sample_rate": 48000},
             "quality_summary": {"metrics": {"rms_db": -18.0, "silence_ratio": 0.01}}},
            {"relative_path": "iso_track1.wav", "category": "audio",
             "duration_seconds": 300.0,
             "audio": {"channel_count": 1, "sample_rate": 48000},
             "quality_summary": {"metrics": {"rms_db": -30.0, "silence_ratio": 0.15}}},
        ]
        master, reasons = _select_master_audio(items)
        assert master == "stereo_mix.wav"

    def test_no_master_when_no_audio(self):
        master, reasons = _select_master_audio([])
        assert master is None


class TestAudioScoring:
    def test_higher_rms_wins(self):
        a1 = {"quality_summary": {"metrics": {"rms_db": -15.0, "noise_db": -60.0,
               "clipping_ratio": 0.0, "silence_ratio": 0.01}},
              "audio": {"channel_count": 2, "sample_rate": 48000}}
        a2 = {"quality_summary": {"metrics": {"rms_db": -30.0, "noise_db": -55.0,
               "clipping_ratio": 0.0, "silence_ratio": 0.05}},
              "audio": {"channel_count": 1, "sample_rate": 44100}}
        assert _score_audio_for_master(a1) > _score_audio_for_master(a2)


class TestAssembleSessionEmpty:
    def test_empty_metadata(self):
        result = assemble_session([])
        assert result.session_id == "empty"

    def test_no_model_returns_unresolved(self):
        items = [
            {"relative_path": "clip.mp4", "category": "video",
             "duration_seconds": 100.0},
        ]
        result = assemble_session(items)
        assert len(result.unresolved_clips) == 1
        assert result.unresolved_clips[0] == "clip.mp4"


class TestAssembleSessionEdges:
    def test_resolved_pair_produces_edge(self):
        items = [
            {"relative_path": "clip.mp4", "category": "video",
             "duration_seconds": 1200.0},
            {"relative_path": "mix.wav", "category": "audio",
             "duration_seconds": 1210.0},
        ]
        pr = PairSyncResult(
            video_path="clip.mp4", audio_path="mix.wav",
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="RESOLVED",
            intercept_a=-11.8, slope_b=1.00003,
            confidence=CONFIDENCE_HIGH,
            retime_recommended=True,
            audio_speed_percent=100.003,
            predicted_end_drift_frames=2.8,
            affine_model=AffineModel(
                intercept_a=0.0, slope_b=1.00003, drift_status=DRIFT_STATUS_RESOLVED,
                temporal_span_seconds=3000.0,
            ),
        )
        result = assemble_session(items, model_local_path=None)
        manual_edges = []
        if pr.sync_status == "RESOLVED":
            edge = SyncEdge(
                source=pr.video_path, target=pr.audio_path,
                relationship=pr.relationship,
                intercept_a=pr.intercept_a, slope_b=pr.slope_b,
                confidence=pr.confidence,
            )
            manual_edges.append(edge)
        assert len(manual_edges) == 1
        assert manual_edges[0].relationship == RELATIONSHIP_SAME_EVENT


class TestSessionSyncResultSerialization:
    def test_session_dict_schema_version(self):
        result = SessionSyncResult(session_id="test_session")
        d = result.to_dict()
        assert d["schema_version"] == SESSION_SCHEMA_VERSION
        assert d["session_id"] == "test_session"

    def test_session_privacy_fields(self):
        result = SessionSyncResult(session_id="test")
        d = result.to_dict()
        assert d["privacy"]["source_media_modified"] is False
        assert d["privacy"]["network_used"] is False
        assert d["privacy"]["database_used"] is False


class TestMultipleVideoOneAudio:
    def test_two_clips_one_master(self):
        items = [
            {"relative_path": "cam1_part1.mp4", "category": "video",
             "duration_seconds": 600.0},
            {"relative_path": "cam1_part2.mp4", "category": "video",
             "duration_seconds": 600.0},
            {"relative_path": "mix.wav", "category": "audio",
             "duration_seconds": 1210.0},
        ]
        result = assemble_session(items)
        d = result.to_dict()
        assert d["session_id"] != "empty"
        assert d["master_audio"] is None or isinstance(d["master_audio"], str)


class TestTwoUnrelatedSessions:
    def test_separate_sessions(self):
        items = [
            {"relative_path": "event_A/CAM1.mp4", "category": "video",
             "duration_seconds": 100.0},
            {"relative_path": "event_B/CAM2.mp4", "category": "video",
             "duration_seconds": 100.0},
        ]
        sessions = group_into_sessions(items)
        assert len(sessions) == 2
        assert "event_A" in sessions
        assert "event_B" in sessions


class TestProjectSessionOrchestration:
    @staticmethod
    def _item(path, category, duration=600.0):
        return {
            "relative_path": path,
            "category": category,
            "duration_seconds": duration,
            "abs_path": path,
        }

    @staticmethod
    def _resolved_pair(video, audio):
        return PairSyncResult(
            video_path=video["relative_path"],
            audio_path=audio["relative_path"],
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="RESOLVED",
            intercept_a=-12.0,
            slope_b=1.00003,
            confidence=CONFIDENCE_HIGH,
            retime_recommended=True,
            audio_speed_percent=100.003,
            predicted_end_drift_frames=2.7,
            selected_match_count=8,
            temporal_span_seconds=500.0,
            affine_model=AffineModel(
                intercept_a=-12.0,
                slope_b=1.00003,
                r_squared=0.999,
                residual_std_ms=10.0,
                anchor_count=5,
                anchor_count_input=5,
                anchor_count_inliers=5,
                consensus_valid=True,
                temporal_span_seconds=500.0,
                drift_status=DRIFT_STATUS_RESOLVED,
            ),
        )

    def test_cross_directory_video_and_recorder_form_one_hypothesis(self):
        items = [
            self._item("camera_card/CLIP/A001.mp4", "video"),
            self._item("audio_recorder/SESSION_80/StereoMix.wav", "audio", 610.0),
        ]
        hypotheses, _groups, before, after = discover_session_hypotheses(items)
        assert len(hypotheses) == 1
        assert hypotheses[0].status == HYPOTHESIS_PLAUSIBLE
        assert hypotheses[0].context_groups[0] != hypotheses[0].context_groups[1]
        assert before == 1
        assert after == 1

    def test_two_logical_sessions_avoid_cross_session_edges(self, monkeypatch):
        items = [
            self._item("camera/A001.mp4", "video"),
            self._item("camera/B001.mp4", "video"),
            self._item("recorder/SESSION_1/mix.wav", "audio", 610.0),
            self._item("recorder/SESSION_2/mix.wav", "audio", 610.0),
        ]
        mapping = {
            "camera/A001.mp4": "recorder/SESSION_1/mix.wav",
            "camera/B001.mp4": "recorder/SESSION_2/mix.wav",
        }

        def fake_sync(video, audio, **_kwargs):
            if mapping.get(video["relative_path"]) == audio["relative_path"]:
                return self._resolved_pair(video, audio)
            return PairSyncResult(video["relative_path"], audio["relative_path"])

        monkeypatch.setattr(sync_module, "synchronize_pair", fake_sync)
        project = assemble_project_sessions(items, model_local_path="local")
        assert len(project.sessions) == 2
        assert all(len(session.edges) == 1 for session in project.sessions)
        assert project.global_cartesian_pairing_used is False
        assert project.pair_candidates_before_reduction == 4
        assert project.pair_candidates_after_reduction == 4

    def test_three_camera_groups_share_one_recorder_session(self, monkeypatch):
        videos = [
            self._item("camera_a/CLIP/A001.mp4", "video"),
            self._item("camera_a/CLIP/A002.mp4", "video"),
            self._item("camera_b/CLIP/B001.mp4", "video"),
            self._item("camera_c/CLIP/C001.mp4", "video"),
        ]
        audios = [
            self._item(f"recorder/SESSION_1/ISO{i}.wav", "audio", 610.0)
            for i in range(4)
        ]
        monkeypatch.setattr(
            sync_module, "synchronize_pair",
            lambda video, audio, **_kwargs: self._resolved_pair(video, audio),
        )
        project = assemble_project_sessions(videos + audios, model_local_path="local")
        assert len(project.sessions) == 1
        assert len(project.sessions[0].synchronized_clips) == 4
        assert len(project.sessions[0].alternate_audio) == 3

    def test_setup_material_remains_unresolved(self, monkeypatch):
        interview = self._item("camera/Interview.mp4", "video")
        setup = self._item("camera/Setup.mp4", "video")
        audio = self._item("recorder/SESSION_1/mix.wav", "audio", 610.0)

        def fake_sync(video, audio, **_kwargs):
            if video["relative_path"] == "camera/Interview.mp4":
                return self._resolved_pair(video, audio)
            return PairSyncResult(video["relative_path"], audio["relative_path"])

        monkeypatch.setattr(sync_module, "synchronize_pair", fake_sync)
        project = assemble_project_sessions([interview, setup, audio], model_local_path="local")
        assert project.sessions[0].synchronized_clips[0].video_path == "camera/Interview.mp4"
        assert "camera/Setup.mp4" in project.unresolved_media

    def test_multitrack_group_uses_one_representative_for_discovery(self, monkeypatch):
        video = self._item("camera/Interview.mp4", "video")
        audios = [
            self._item(f"recorder/SESSION_1/Track{i}.wav", "audio", 610.0)
            for i in range(4)
        ]
        calls = []

        def fake_sync(video, audio, **_kwargs):
            calls.append(audio["relative_path"])
            return self._resolved_pair(video, audio)

        monkeypatch.setattr(sync_module, "synchronize_pair", fake_sync)
        project = assemble_project_sessions([video, *audios], model_local_path="local")
        assert len(project.hypotheses) == 1
        assert len(calls) == 1
        assert len(project.sessions[0].alternate_audio) == 3

    def test_candidate_reduction_is_not_global_cartesian(self):
        videos = [self._item(f"camera_{i}/A{i}.mp4", "video") for i in range(3)]
        audios = [
            self._item(f"recorder/SESSION_{session}/Track{i}.wav", "audio", 610.0)
            for session in (1, 2) for i in range(10)
        ]
        hypotheses, _groups, before, after = discover_session_hypotheses(videos + audios)
        assert len(hypotheses) == 2
        assert before == 60
        assert after == 6
        assert after < before


class TestCameraClipNoExternalAudio:
    def test_video_only_unresolved(self):
        items = [
            {"relative_path": "orphan.mp4", "category": "video",
             "duration_seconds": 300.0},
        ]
        result = assemble_session(items)
        assert len(result.unresolved_clips) == 1
        assert result.edges == []


class TestIsVideoIsAudio:
    def test_video_category(self):
        assert _is_video_file({"category": "video", "relative_path": "x.mp4"})
        assert _is_audio_file({"category": "audio", "relative_path": "x.wav"})

    def test_video_extension(self):
        assert _is_video_file({"relative_path": "clip.mxf"})
        assert _is_audio_file({"relative_path": "clip.bwf"})


# =====================================================================
# OUTLIER FILTER
# =====================================================================

class TestRobustFilterCleanData:
    def test_preserves_clean_data(self):
        points = [(0.0, 0.0), (100.0, 100.0), (200.0, 200.0)]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert len(accepted) == 3
        assert rejected == 0

    def test_small_set_unfiltered(self):
        points = [(0.0, 0.0), (100.0, 100.0)]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert len(accepted) == 2
        assert rejected == 0


class TestRobustOutlierFilter:
    def test_filters_clear_outlier(self):
        points = [
            (0.0, 0.0), (100.0, 100.0), (200.0, 200.0),
            (300.0, 300.0), (400.0, 500.0),
        ]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert len(accepted) == 4
        assert rejected == 1
        for x, y in accepted:
            assert abs(y - x) < 50.0

    def test_theil_sen_resists_leverage_outlier(self):
        points = [
            (0.0, 0.0), (100.0, 100.0), (200.0, 200.0),
            (300.0, 300.0), (400.0, 400.0),
            (500.0, 300.0),
        ]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert rejected >= 1
        assert len(accepted) >= 4
        a, b = _ols_fit(accepted)
        assert abs(b - 1.0) < 0.01
        assert abs(a) < 5.0

    def test_noisy_anchors_with_outlier(self):
        import random
        rng = random.Random(42)
        base_intercept = -12.0
        base_slope = 1.00005
        good = [(t, base_intercept + base_slope * t + rng.uniform(-0.05, 0.05))
                for t in range(0, 3600, 300)]
        bad = [(1500.0, 1500.0 + 120.0)]
        all_pts = good + bad
        accepted, rejected, _ = _robust_outlier_filter(all_pts)
        assert rejected >= 1
        assert len(accepted) >= len(good) - 1
        a, b = _ols_fit(accepted)
        assert abs(b - base_slope) < 0.001
        assert abs(a - base_intercept) < 1.0

    def test_mad_zero_absolute_threshold(self):
        points = [
            (0.0, 0.0), (100.0, 100.0), (200.0, 200.0),
            (300.0, 300.0), (400.0, 500.0),
        ]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert len(accepted) >= 4
        assert rejected >= 1

    def test_all_coherent_no_rejection(self):
        points = [(i * 100.0, i * 100.0 + 5.0) for i in range(5)]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert rejected == 0
        assert len(accepted) == 5

    def test_two_points_passthrough(self):
        points = [(0.0, 0.0), (100.0, 100.0)]
        accepted, rejected, _ = _robust_outlier_filter(points)
        assert len(accepted) == 2
        assert rejected == 0


# =====================================================================
# PAIR SYNC RESULT CONTRACT
# =====================================================================

class TestPairSyncResultContract:
    def test_default_relationship_unresolved(self):
        r = PairSyncResult(video_path="a.mp4", audio_path="b.wav")
        assert r.relationship == RELATIONSHIP_UNRESOLVED
        assert r.sync_status == "UNRESOLVED"
        assert r.confidence == CONFIDENCE_UNRESOLVED

    def test_to_dict_contains_all_fields(self):
        r = PairSyncResult(
            video_path="v.mp4", audio_path="a.wav",
            relationship=RELATIONSHIP_SAME_EVENT,
            sync_status="RESOLVED",
            confidence=CONFIDENCE_HIGH,
        )
        d = r.to_dict()
        for key in ["video_path", "audio_path", "relationship",
                     "sync_status", "confidence", "intercept_a",
                     "slope_b", "retime_recommended",
                     "retime_classification", "audio_speed_percent",
                     "uncertainty_ms", "anchor_count"]:
            assert key in d, f"missing key: {key}"

    def test_manifest_entry_roundtrip(self):
        r = PairSyncResult(
            video_path="v.mp4", audio_path="a.wav",
            intercept_a=-5.0, slope_b=1.00003,
            confidence=CONFIDENCE_HIGH,
            retime_recommended=True,
            audio_speed_percent=100.003,
        )
        entry = r.to_manifest_entry()
        assert entry["offset_seconds"] == -5.0
        assert entry["slope_b"] == 1.00003
        assert entry["retime_recommended"] is True


# =====================================================================
# TEMPORAL OCCURRENCE SEQUENCES
# =====================================================================

class TestTemporalOccurrenceSequence:
    def test_kenya_like_sequence_rejects_distant_duplicates(self):
        phrases = ["alfauno", "betados", "gammatres", "deltafour", "epsilonfive"]
        video_times = [300.0, 900.0, 1500.0, 2400.0, 3300.0]
        video = [
            {"text": phrase, "source_start_seconds": time,
             "source_end_seconds": time + 1.0}
            for phrase, time in zip(phrases, video_times)
        ]
        audio = [
            {"text": phrase, "source_start_seconds": time - 12.0 + 0.00005 * time,
             "source_end_seconds": time - 11.0 + 0.00005 * time}
            for phrase, time in zip(phrases, video_times)
        ]
        audio.extend([
            {"text": "betados", "source_start_seconds": 100.0,
             "source_end_seconds": 101.0},
            {"text": "deltafour", "source_start_seconds": 3900.0,
             "source_end_seconds": 3901.0},
        ])
        anchors = match_content_anchors(
            build_ordered_occurrences(video),
            build_ordered_occurrences(audio),
        )
        assert len(anchors) == 5
        assert [a.video_time for a in anchors] == sorted(a.video_time for a in anchors)
        assert [a.audio_time for a in anchors] == sorted(a.audio_time for a in anchors)
        model = fit_affine_model(anchors, video_duration=3600.0)
        assert model.consensus_valid is True
        assert abs(model.intercept_a + 12.0) < 0.1
        assert abs(model.slope_b - 1.00005) < 0.0001

    def test_repeated_phrase_uses_sequence_context(self):
        video = [
            {"text": "phrasex", "source_start_seconds": 100.0,
             "source_end_seconds": 101.0},
            {"text": "phrasex", "source_start_seconds": 500.0,
             "source_end_seconds": 501.0},
        ]
        audio = [
            {"text": "phrasex", "source_start_seconds": 88.0,
             "source_end_seconds": 89.0},
            {"text": "phrasex", "source_start_seconds": 488.0,
             "source_end_seconds": 489.0},
            {"text": "phrasex", "source_start_seconds": 900.0,
             "source_end_seconds": 901.0},
        ]
        anchors = match_content_anchors(
            build_ordered_occurrences(video),
            build_ordered_occurrences(audio),
        )
        assert [(round(a.video_time), round(a.audio_time)) for a in anchors] == [
            (100, 88), (500, 488)
        ]

    def test_non_monotonic_false_matches_are_not_a_chain(self):
        video = [
            {"text": "firsttoken", "source_start_seconds": 100.0,
             "source_end_seconds": 101.0},
            {"text": "secondtoken", "source_start_seconds": 500.0,
             "source_end_seconds": 501.0},
        ]
        audio = [
            {"text": "firsttoken", "source_start_seconds": 900.0,
             "source_end_seconds": 901.0},
            {"text": "secondtoken", "source_start_seconds": 100.0,
             "source_end_seconds": 101.0},
        ]
        anchors = match_content_anchors(
            build_ordered_occurrences(video),
            build_ordered_occurrences(audio),
        )
        assert len(anchors) < 2

    def test_window_timestamp_origin_added_once(self, monkeypatch):
        def fake_extract(_media, _start, _duration, output_path, _ffmpeg=None):
            Path(output_path).touch()
            return True

        def fake_transcribe(_wav, _model, _language=None):
            return [{"text": "anchor", "start_seconds": 12.5,
                     "end_seconds": 13.5}]

        monkeypatch.setattr(sync_module, "_extract_window_to_wav", fake_extract)
        monkeypatch.setattr(sync_module, "_transcribe_window", fake_transcribe)
        segments = sync_module.transcribe_media_windows(
            "/unused", [600.0], "model", language_hint="es"
        )
        assert segments[0]["source_start_seconds"] == 612.5
        assert segments[0]["source_end_seconds"] == 613.5


class TestLongFormHypotheses:
    def test_retains_true_and_false_offset_families(self):
        video = [
            {"text": token, "source_start_seconds": time,
             "source_end_seconds": time + 1.0}
            for token, time in [("alphaone", 100.0), ("betatwo", 120.0),
                                ("gammathree", 140.0)]
        ]
        audio = [
            {"text": "alphaone", "source_start_seconds": 88.0,
             "source_end_seconds": 89.0},
            {"text": "betatwo", "source_start_seconds": 108.0,
             "source_end_seconds": 109.0},
            {"text": "gammathree", "source_start_seconds": 128.0,
             "source_end_seconds": 129.0},
            {"text": "alphaone", "source_start_seconds": 220.0,
             "source_end_seconds": 221.0},
            {"text": "betatwo", "source_start_seconds": 240.0,
             "source_end_seconds": 241.0},
            {"text": "gammathree", "source_start_seconds": 260.0,
             "source_end_seconds": 261.0},
        ]
        candidates = _build_temporal_candidates(
            build_ordered_occurrences(video), build_ordered_occurrences(audio)
        )
        hypotheses = build_offset_hypotheses(candidates)
        deltas = {round(h.median_delta) for h in hypotheses}
        assert -12 in deltas
        assert 120 in deltas

    def test_projected_audio_windows_do_not_use_audio_percentage(self):
        starts = select_verification_windows(3600.0)
        projected = [project_audio_window_start(start, -12.0, 3750.0)
                     for start in starts]
        assert projected[0] == starts[0] - 12.0
        assert projected[-1] == starts[-1] - 12.0
        assert projected[-1] != round(0.9 * (3750.0 - 30.0), 2)

    def test_long_form_span_is_duration_aware(self):
        assert long_form_minimum_span(600.0) == 120.0
        assert long_form_minimum_span(3600.0) == 1800.0

    def test_local_false_hypothesis_does_not_survive(self):
        hypothesis = OffsetHypothesis(
            median_delta=120.0, mad_delta=1.0, raw_support=4,
            unique_phrases=3, window_diversity=1,
            video_span_seconds=12.0, audio_span_seconds=12.0,
            initial_score=5.0,
        )
        anchors = [
            ContentAnchor("a", "a", 100.0, 220.0, 0, 0,
                          video_window_id="1", audio_window_id="1"),
            ContentAnchor("b", "b", 105.0, 225.0, 0, 0,
                          video_window_id="1", audio_window_id="1"),
            ContentAnchor("c", "c", 112.0, 232.0, 0, 0,
                          video_window_id="1", audio_window_id="1"),
        ]
        result = evaluate_hypothesis(hypothesis, anchors, 3600.0)
        assert result.survived is False

    def test_true_hypothesis_expands_to_long_baseline(self):
        hypothesis = OffsetHypothesis(
            median_delta=-12.0, mad_delta=0.2, raw_support=3,
            unique_phrases=3, window_diversity=3,
            video_span_seconds=120.0, audio_span_seconds=120.0,
            initial_score=8.0,
        )
        anchors = [
            ContentAnchor("a", "a", 300.0, 288.0, 0, 0,
                          video_window_id="1", audio_window_id="1"),
            ContentAnchor("b", "b", 1800.0, 1788.1, 0, 0,
                          video_window_id="2", audio_window_id="2"),
            ContentAnchor("c", "c", 3300.0, 3288.2, 0, 0,
                          video_window_id="3", audio_window_id="3"),
        ]
        result = evaluate_hypothesis(hypothesis, anchors, 3600.0)
        assert result.survived is True
        assert result.verification_windows_confirmed == 3


class TestIndependentLocalAlignment:
    def test_window_balancing_prevents_token_pseudoreplication(self):
        anchors = []
        window_specs = [(0.0, 30, 0.0), (900.0, 4, 0.036),
                        (1800.0, 5, 0.072), (2700.0, 3, 0.108),
                        (3300.0, 6, 0.132)]
        for window_index, (video_time, count, error) in enumerate(window_specs):
            for token_index in range(count):
                anchors.append(ContentAnchor(
                    f"p{window_index}_{token_index}",
                    f"p{window_index}_{token_index}",
                    video_time + token_index,
                    video_time - 12.0 + 1.00004 * token_index + error,
                    token_index,
                    token_index,
                    video_window_id=str(window_index),
                    audio_window_id=str(window_index),
                ))
        local = build_local_alignment_anchors(anchors)
        assert len(local) == 5
        model = fit_affine_model(local, video_duration=3600.0)
        assert abs(model.slope_b - 1.00004) < 0.0002
        assert model.anchor_count_input == 5

    def test_word_timestamps_override_segment_interpolation(self):
        segments = [{
            "text": "alpha beta",
            "source_start_seconds": 600.0,
            "source_end_seconds": 602.0,
            "window_id": "600",
            "words": [
                {"word": "alpha", "source_start_seconds": 600.1,
                 "source_end_seconds": 600.3},
                {"word": "beta", "source_start_seconds": 601.7,
                 "source_end_seconds": 601.9},
            ],
        }]
        occurrences = build_ordered_occurrences(segments)
        assert [o.absolute_time for o in occurrences] == [600.1, 601.7]

    def test_acoustic_unique_peak_refines_local_offset(self):
        import numpy as np
        reference = np.zeros(2000, dtype=np.float32)
        reference[700:760] = np.hanning(60)
        external = np.zeros(2000, dtype=np.float32)
        external[710:770] = np.hanning(60)
        refined, was_refined, peak, uniqueness = refine_local_acoustic_offset(
            reference, external, 1000, 0.0, search_radius_seconds=0.2
        )
        assert was_refined is True
        assert abs(refined - 0.01) < 0.002
        assert peak > 0.2
        assert uniqueness >= 0.02

    def test_acoustic_ambiguous_peak_keeps_text_offset(self):
        import numpy as np
        repeated = np.tile(np.array([1.0, -1.0], dtype=np.float32), 1000)
        refined, was_refined, _peak, _uniqueness = refine_local_acoustic_offset(
            repeated, repeated, 1000, -0.12, search_radius_seconds=0.2
        )
        assert was_refined is False
        assert refined == -0.12

    def _local_anchor(self):
        return LocalAlignmentAnchor(
            100.0, 88.15, -11.85, "100.000", 5, 5, 50.0, 0.9
        )

    def _hypothesis(self):
        return OffsetHypothesis(
            median_delta=-11.8, mad_delta=0.01, raw_support=10,
            unique_phrases=5, window_diversity=1, video_span_seconds=30.0,
            audio_span_seconds=30.0, initial_score=1.0,
        )

    def test_live_refinement_accepts_unique_stable_subregions(self, monkeypatch):
        monkeypatch.setattr(sync_module, "_extract_window_to_wav", lambda *args: True)
        monkeypatch.setattr(sync_module, "_read_pcm16_wav", lambda _path: np.ones(1000))
        monkeypatch.setattr(
            sync_module, "refine_local_acoustic_offset",
            lambda _v, _a, _rate, coarse: (coarse + 0.01, True, 0.8, 0.2),
        )
        refined = _refine_local_alignment_anchors(
            "video.mp4", "audio.wav", 3600.0, self._hypothesis(),
            [self._local_anchor()], None,
        )[0]
        assert refined.acoustic_refined is True
        assert abs(refined.acoustic_shift_ms - 10.0) < 0.01
        assert abs(refined.local_offset_seconds - (-11.84)) < 0.001

    def test_live_refinement_rejects_ambiguous_peak(self, monkeypatch):
        monkeypatch.setattr(sync_module, "_extract_window_to_wav", lambda *args: True)
        monkeypatch.setattr(sync_module, "_read_pcm16_wav", lambda _path: np.ones(1000))
        monkeypatch.setattr(
            sync_module, "refine_local_acoustic_offset",
            lambda _v, _a, _rate, coarse: (coarse, False, 0.7, 0.001),
        )
        refined = _refine_local_alignment_anchors(
            "video.mp4", "audio.wav", 3600.0, self._hypothesis(),
            [self._local_anchor()], None,
        )[0]
        assert refined.acoustic_refined is False
        assert refined.local_offset_seconds == -11.85

    def test_live_refinement_rejects_boundary_peak(self, monkeypatch):
        monkeypatch.setattr(sync_module, "_extract_window_to_wav", lambda *args: True)
        monkeypatch.setattr(sync_module, "_read_pcm16_wav", lambda _path: np.ones(1000))
        monkeypatch.setattr(
            sync_module, "refine_local_acoustic_offset",
            lambda _v, _a, _rate, coarse: (coarse + 0.2, True, 0.9, 0.3),
        )
        refined = _refine_local_alignment_anchors(
            "video.mp4", "audio.wav", 3600.0, self._hypothesis(),
            [self._local_anchor()], None,
        )[0]
        assert refined.acoustic_refined is False

    def test_live_refinement_rejects_unstable_subregions(self, monkeypatch):
        monkeypatch.setattr(sync_module, "_extract_window_to_wav", lambda *args: True)
        monkeypatch.setattr(sync_module, "_read_pcm16_wav", lambda _path: np.ones(1000))
        shifts = iter((0.01, 0.10))
        monkeypatch.setattr(
            sync_module, "refine_local_acoustic_offset",
            lambda _v, _a, _rate, coarse: (coarse + next(shifts), True, 0.8, 0.2),
        )
        refined = _refine_local_alignment_anchors(
            "video.mp4", "audio.wav", 3600.0, self._hypothesis(),
            [self._local_anchor()], None,
        )[0]
        assert refined.acoustic_refined is False
        assert refined.local_offset_seconds == -11.85

    def test_bad_refined_window_cannot_control_independent_global_fit(self):
        local = [
            LocalAlignmentAnchor(t, t - 12.0 + 0.00004 * t,
                                  -12.0 + 0.00004 * t, str(i), 5, 5,
                                  20.0, 0.9, True, 0.2, 0.8, 0.6, 10.0)
            for i, t in enumerate([300.0, 1200.0, 2100.0, 3000.0])
        ]
        local.append(LocalAlignmentAnchor(
            3300.0, 3600.0, 300.0, "bad", 5, 5, 20.0, 0.9,
            True, 0.2, 0.8, 0.6, 300000.0,
        ))
        model = fit_affine_model(local, video_duration=3600.0)
        assert model.anchor_count_rejected >= 1
        assert abs(model.slope_b - 1.00004) < 0.001

    def test_one_bad_local_window_is_rejected_by_global_fit(self):
        local = [
            LocalAlignmentAnchor(t, t - 12.0 + 0.00004 * t,
                                  -12.0 + 0.00004 * t, str(i), 4, 4,
                                  20.0, 0.8)
            for i, t in enumerate([300.0, 1200.0, 2100.0, 3000.0])
        ]
        local.append(LocalAlignmentAnchor(3300.0, 3600.0, 300.0, "bad",
                                          4, 4, 20.0, 0.8))
        model = fit_affine_model(local, video_duration=3600.0)
        assert model.anchor_count_rejected >= 1
        assert abs(model.slope_b - 1.00004) < 0.001

    def test_synthetic_clock_slope_stays_editorially_useful(self):
        local = [
            LocalAlignmentAnchor(t, -12.0 + 1.00004 * t,
                                  -12.0 + 0.00004 * t, str(i), 5, 5,
                                  15.0, 0.9)
            for i, t in enumerate([300.0, 1200.0, 2100.0, 3000.0, 3500.0])
        ]
        model = fit_affine_model(local, video_duration=3600.0)
        error_ms = abs((model.intercept_a + model.slope_b * 3600.0)
                       - (-12.0 + 1.00004 * 3600.0)) * 1000.0
        assert error_ms <= 80.0



# =====================================================================
# FAIL-SAFE: INSUFFICIENT CONSENSUS (v3)
# =====================================================================

class TestInsufficientConsensus:
    def test_contradictory_anchors_not_restored(self):
        """5 contradictory anchors -> insufficient consensus, no silent restore."""
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 100.0, 300.0, 0, 0),
            ContentAnchor("c", "c", 200.0, 50.0, 0, 0),
            ContentAnchor("d", "d", 300.0, 700.0, 0, 0),
            ContentAnchor("e", "e", 400.0, 200.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=500.0)
        assert model.consensus_valid is False
        assert model.anchor_count_inliers == 0
        assert model.anchor_count_rejected > 0
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED

    def test_two_points_computable_but_drift_unresolved(self):
        """2 perfectly aligned anchors -> line computable, drift unresolved."""
        anchors = [
            ContentAnchor("a", "a", 0.0, 5.0, 0, 0),
            ContentAnchor("b", "b", 500.0, 505.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=600.0)
        assert abs(model.intercept_a - 5.0) < 0.01
        assert abs(model.slope_b - 1.0) < 1e-6
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED
        assert model.consensus_valid is True

    def test_one_anchor_slope_unresolved(self):
        """1 anchor -> slope/drift unresolved."""
        anchors = [
            ContentAnchor("a", "a", 100.0, 105.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=200.0)
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED
        assert model.consensus_valid is False
        assert model.anchor_count_inliers == 1
        assert model.intercept_a == 105.0

    def test_zero_consensus_temporal_model_unresolved(self):
        """0 anchors -> temporal model unresolved."""
        model = fit_affine_model([], video_duration=200.0)
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED
        assert model.slope_b == 1.0
        assert model.intercept_a == 0.0

    def test_two_inliers_four_rejected_low_confidence(self):
        """2 inliers + 4 rejected cannot become HIGH confidence."""
        model = AffineModel(
            intercept_a=0.0,
            slope_b=1.0001,
            r_squared=1.0,
            residual_std_ms=1.0,
            predicted_end_drift_frames=10.0,
            anchor_count=2,
            anchor_count_input=6,
            anchor_count_inliers=2,
            anchor_count_rejected=4,
            consensus_valid=True,
            temporal_span_seconds=1000.0,
            drift_status=DRIFT_STATUS_UNRESOLVED,
        )
        assert model.consensus_valid is True
        assert model.anchor_count_inliers == 2
        assert model.anchor_count_rejected == 4
        conf = _compute_confidence(model, n_matches=6)
        assert conf != CONFIDENCE_HIGH
        retime, _ = _decide_retime(model, conf)
        assert retime is False

    def test_three_long_baseline_drift_valid(self):
        """3+ coherent long-baseline anchors -> drift may become valid."""
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 600.0, 600.0, 0, 0),
            ContentAnchor("c", "c", 1200.0, 1200.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=1500.0)
        assert model.drift_status == DRIFT_STATUS_RESOLVED
        assert model.consensus_valid is True

    def test_three_clustered_drift_unresolved(self):
        """3+ coherent but tightly clustered anchors -> drift unresolved."""
        anchors = [
            ContentAnchor("a", "a", 100.0, 100.0, 0, 0),
            ContentAnchor("b", "b", 105.0, 105.0, 0, 0),
            ContentAnchor("c", "c", 110.0, 110.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=200.0)
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED

    def test_high_rejection_ratio_lowers_confidence(self):
        """High rejection ratio reduces confidence."""
        model = AffineModel(
            intercept_a=0.0,
            slope_b=1.00001,
            r_squared=1.0,
            residual_std_ms=1.0,
            anchor_count=3,
            anchor_count_input=5,
            anchor_count_inliers=3,
            anchor_count_rejected=2,
            consensus_valid=True,
            temporal_span_seconds=1000.0,
            drift_status=DRIFT_STATUS_RESOLVED,
        )
        conf = _compute_confidence(model, n_matches=5)
        assert conf != CONFIDENCE_HIGH

    def test_leverage_outlier_excluded(self):
        """Distant bad anchor excluded, majority retained."""
        good = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 100.0, 100.0, 0, 0),
            ContentAnchor("c", "c", 200.0, 200.0, 0, 0),
            ContentAnchor("d", "d", 300.0, 300.0, 0, 0),
            ContentAnchor("e", "e", 400.0, 400.0, 0, 0),
        ]
        bad = [ContentAnchor("f", "f", 500.0, 300.0, 0, 0)]
        model = fit_affine_model(good + bad, video_duration=600.0)
        assert model.consensus_valid is True
        assert model.anchor_count_rejected >= 1
        assert abs(model.slope_b - 1.0) < 0.01

    def test_noisy_good_anchors_fit_correctly(self):
        """Noisy good anchors + outlier fit correctly."""
        import random
        rng = random.Random(42)
        good = [
            ContentAnchor(str(i), str(i), t,
                          -12.0 + 1.00005 * t + rng.uniform(-0.05, 0.05),
                          0, 0)
            for i, t in enumerate(range(0, 3600, 300))
        ]
        bad = [ContentAnchor("x", "x", 1500.0, 1620.0, 0, 0)]
        model = fit_affine_model(good + bad, video_duration=3600.0)
        assert model.consensus_valid is True
        assert model.anchor_count_rejected >= 1
        assert abs(model.slope_b - 1.00005) < 0.001
        assert abs(model.intercept_a - (-12.0)) < 1.0

    def test_consensus_valid_propagates_to_pair_sync(self):
        """Consensus failure produces unresolved pair."""
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 100.0, 300.0, 0, 0),
            ContentAnchor("c", "c", 200.0, 50.0, 0, 0),
            ContentAnchor("d", "d", 300.0, 700.0, 0, 0),
            ContentAnchor("e", "e", 400.0, 200.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=500.0)
        conf = _compute_confidence(model, n_matches=5)
        assert conf == CONFIDENCE_LOW
        retime, _ = _decide_retime(model, conf)
        assert retime is False

    def test_invalid_consensus_cannot_be_high_confidence(self):
        model = AffineModel(
            intercept_a=0.0,
            slope_b=1.0001,
            r_squared=1.0,
            residual_std_ms=0.1,
            anchor_count=0,
            anchor_count_input=5,
            anchor_count_inliers=0,
            anchor_count_rejected=5,
            consensus_valid=False,
            temporal_span_seconds=1000.0,
            drift_status=DRIFT_STATUS_UNRESOLVED,
        )
        assert _compute_confidence(model, n_matches=5) != CONFIDENCE_HIGH

    def test_invalid_consensus_cannot_trigger_retime(self):
        model = AffineModel(
            intercept_a=0.0,
            slope_b=1.0001,
            r_squared=1.0,
            residual_std_ms=0.1,
            predicted_end_drift_frames=10.0,
            anchor_count=0,
            anchor_count_input=5,
            anchor_count_inliers=0,
            anchor_count_rejected=5,
            consensus_valid=False,
            temporal_span_seconds=1000.0,
            drift_status=DRIFT_STATUS_UNRESOLVED,
        )
        retime, _ = _decide_retime(model, CONFIDENCE_HIGH)
        assert retime is False

    def test_drift_requires_minimum_inliers(self):
        """Drift requires MIN_DRIFT_VALIDATION_INLIERS, not just 2."""
        anchors = [
            ContentAnchor("a", "a", 0.0, 0.0, 0, 0),
            ContentAnchor("b", "b", 500.0, 500.0, 0, 0),
        ]
        model = fit_affine_model(anchors, video_duration=600.0)
        assert model.drift_status == DRIFT_STATUS_UNRESOLVED
        assert model.anchor_count_inliers == 2


# =====================================================================
# COARSE OFFSET BOOTSTRAP TESTS
# =====================================================================

_V_DUR = 3600.0
_A_DUR = 3600.0
_MODEL = "fake_model"
_WINDOW_SEC = 30.0


def _video_segs():
    return [
        {"text": "alpha1 beta1", "source_start_seconds": 5.0,
         "source_end_seconds": 7.0, "window_id": "0.000"},
        {"text": "beta1 gamma1", "source_start_seconds": 10.0,
         "source_end_seconds": 12.0, "window_id": "0.000"},
        {"text": "gamma1 delta1", "source_start_seconds": 910.0,
         "source_end_seconds": 912.0, "window_id": "900.000"},
        {"text": "delta1 epsilon1", "source_start_seconds": 1810.0,
         "source_end_seconds": 1812.0, "window_id": "1800.000"},
        {"text": "epsilon1 zeta1", "source_start_seconds": 2710.0,
         "source_end_seconds": 2712.0, "window_id": "2700.000"},
        {"text": "zeta1 eta1", "source_start_seconds": 3510.0,
         "source_end_seconds": 3512.0, "window_id": "3570.000"},
    ]


def _audio_segs(delta):
    shift = delta
    return [
        {"text": "alpha1 beta1", "source_start_seconds": 5.0 + shift,
         "source_end_seconds": 7.0 + shift, "window_id": "0.000"},
        {"text": "beta1 gamma1", "source_start_seconds": 10.0 + shift,
         "source_end_seconds": 12.0 + shift, "window_id": "0.000"},
        {"text": "gamma1 delta1", "source_start_seconds": 910.0 + shift,
         "source_end_seconds": 912.0 + shift, "window_id": "900.000"},
        {"text": "delta1 epsilon1", "source_start_seconds": 1810.0 + shift,
         "source_end_seconds": 1812.0 + shift, "window_id": "1800.000"},
        {"text": "epsilon1 zeta1", "source_start_seconds": 2710.0 + shift,
         "source_end_seconds": 2712.0 + shift, "window_id": "2700.000"},
        {"text": "zeta1 eta1", "source_start_seconds": 3510.0 + shift,
         "source_end_seconds": 3512.0 + shift, "window_id": "3570.000"},
    ]


def _content_at(start, tokens, wid):
    segs = []
    t = start
    for tok in tokens:
        segs.append({
            "text": tok, "source_start_seconds": t,
            "source_end_seconds": t + 1.0, "window_id": wid,
        })
        t += 2.0
    return segs


def _make_transcript_context(video_delta, bootstrap_delta=None):
    """Return a fake transcribe function that returns position-dependent content.

    video_delta: the true offset between audio and video (audio_time = video_time + delta)
    bootstrap_delta: if set, use this for bootstrap audio projection
    """
    video_content = {
        0.0: ["alpha1", "beta1"],
        900.0: ["gamma1", "delta1"],
        1800.0: ["delta1", "epsilon1"],
        2700.0: ["epsilon1", "zeta1"],
        3570.0: ["zeta1", "eta1"],
    }

    audio_content = {}
    delta = video_delta
    for vpos, toks in video_content.items():
        apos = vpos + delta
        audio_content[apos] = toks

    def fake_transcribe(wav_path, model, language=None):
        p = str(wav_path)
        if "cid_sync_" in p:
            is_video = "_video_" in p or "video.wav" in p
        else:
            is_video = False

        if is_video:
            for pos, toks in video_content.items():
                if pos >= 0:
                    return _content_at(pos, toks, f"{pos:.3f}")
        else:
            for pos, toks in audio_content.items():
                if pos >= 0:
                    return _content_at(pos, toks, f"{pos:.3f}")
        return []

    return fake_transcribe


class TestCoarseOffsetBootstrap:
    @staticmethod
    def _make_mock(delta, bucket_seconds=300.0):
        """Build a transcribe_media_windows mock for a given temporal offset.

        Uses continuous time-bucketing so matching tokens always produce
        the correct candidate delta regardless of window grid alignment.
        Each bucket has 3 tokens to satisfy the
        build_local_alignment_anchors >= 3-per-group threshold.
        """
        def factory(v_dur, a_dur):
            def fake_transcribe_media(media_path, windows, model, **kw):
                is_video = "cam" in str(media_path)
                segs = []
                for w in windows:
                    if is_video:
                        content_time = w
                    else:
                        content_time = w - delta
                    if content_time < -bucket_seconds or content_time > v_dur + bucket_seconds:
                        continue
                    bucket = max(0, int(content_time / bucket_seconds))
                    t = w
                    for suffix in ("a", "b", "c"):
                        tok = f"b{bucket}t{suffix}"
                        segs.append({"text": tok,
                                     "source_start_seconds": t,
                                     "source_end_seconds": t + 1.0,
                                     "window_id": f"{w:.3f}"})
                        t += 0.5
                return segs
            return fake_transcribe_media
        return factory

    def test_coarse_offset_hypotheses_from_candidates(self):
        video = [
            {"text": "alpha1", "source_start_seconds": 10.0,
             "source_end_seconds": 11.0},
            {"text": "beta1", "source_start_seconds": 100.0,
             "source_end_seconds": 101.0},
        ]
        audio = [
            {"text": "alpha1", "source_start_seconds": 55.0,
             "source_end_seconds": 56.0},
            {"text": "beta1", "source_end_seconds": 145.0,
             "source_end_seconds": 146.0, "source_start_seconds": 144.0},
        ]
        cands = _build_temporal_candidates(
            build_ordered_occurrences(video),
            build_ordered_occurrences(audio),
        )
        hyps = sync_module._compute_coarse_offset_hypotheses(cands, 3600, 3600)
        assert len(hyps) >= 1
        assert abs(hyps[0]["median_delta"] - 45.0) < 1.0
        assert hyps[0]["unique_phrases"] >= 2

    def test_bootstrap_resolves_camera_starting_before_recorder(self, monkeypatch):
        delta = 45.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT
        assert result.confidence in (CONFIDENCE_HIGH, CONFIDENCE_MEDIUM)

    def test_bootstrap_resolves_camera_starting_after_recorder(self, monkeypatch):
        delta = -60.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT

    def test_bootstrap_resolves_large_100s_offset(self, monkeypatch):
        delta = 100.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT

    def test_false_bootstrap_unrelated_no_sync(self, monkeypatch):
        def fake_unrelated(media_path, windows, model, **kw):
            prefix = "vid" if "cam" in str(media_path) else "aud"
            segs = []
            for w in windows:
                for j in range(3):
                    segs.append({"text": f"{prefix}{int(w)}t{j}",
                                 "source_start_seconds": w + j * 0.5,
                                 "source_end_seconds": w + j * 0.5 + 1.0,
                                 "window_id": f"{w:.3f}"})
            return segs
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            fake_unrelated)
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "UNRESOLVED"

    def test_multiple_hypotheses_only_correct_survives(self, monkeypatch):
        delta = 45.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT

    def test_short_clip_no_bootstrap(self, monkeypatch):
        def fake_transcribe_media(media_path, windows, model, **kw):
            return [{"text": "hello", "source_start_seconds": 0.0,
                     "source_end_seconds": 0.5, "window_id": "0.000"}]
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            fake_transcribe_media)
        v_meta = {"relative_path": "cam/test.mp4", "abs_path": "cam/test.mp4",
                  "duration_seconds": 0.96, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": 3600.0, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "UNRESOLVED"

    def test_partial_overlap_resolves(self, monkeypatch):
        v_dur = _V_DUR
        a_dur = _A_DUR
        delta = 20.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(v_dur, a_dur))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": v_dur, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": a_dur, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT

    def test_projected_early_window_outside_range_recovers(self, monkeypatch):
        delta = -40.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        assert result.sync_status == "RESOLVED"
        assert result.relationship == RELATIONSHIP_SAME_EVENT

    def test_three_cameras_same_session_different_offsets(self, monkeypatch):
        offsets = [-40.0, -90.0, -10.0]
        results = []
        for delta in offsets:
            monkeypatch.setattr(sync_module, "transcribe_media_windows",
                                self._make_mock(delta)(_V_DUR, _A_DUR))
            v_meta = {"relative_path": f"cam/delta{int(delta)}.mp4",
                      "abs_path": f"cam/delta{int(delta)}.mp4",
                      "duration_seconds": _V_DUR, "category": "video"}
            a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                      "duration_seconds": _A_DUR, "category": "audio"}
            r = sync_module.synchronize_pair(
                v_meta, a_meta, model_local_path=_MODEL)
            results.append(r)
        for r in results:
            assert r.sync_status == "RESOLVED", f"offset failed: {r.evidence}"
            assert r.relationship == RELATIONSHIP_SAME_EVENT

    def test_fragmented_clips_each_gets_own_offset(self, monkeypatch):
        offsets_and_starts = [(0.0, 30.0), (1800.0, -20.0)]
        results = []
        for v_start, delta in offsets_and_starts:
            monkeypatch.setattr(sync_module, "transcribe_media_windows",
                                self._make_mock(delta)(_A_DUR, _A_DUR))
            v_meta = {"relative_path": f"cam/frag_{int(v_start)}.mp4",
                      "abs_path": f"cam/frag_{int(v_start)}.mp4",
                      "duration_seconds": _A_DUR, "category": "video"}
            a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                      "duration_seconds": _A_DUR, "category": "audio"}
            r = sync_module.synchronize_pair(
                v_meta, a_meta, model_local_path=_MODEL)
            results.append(r)
        for r in results:
            assert r.sync_status == "RESOLVED", f"fragment failed: {r.evidence}"

    def test_bootstrap_tracks_diagnostics(self, monkeypatch):
        delta = 45.0
        monkeypatch.setattr(sync_module, "transcribe_media_windows",
                            self._make_mock(delta)(_V_DUR, _A_DUR))
        v_meta = {"relative_path": "cam/a.mp4", "abs_path": "cam/a.mp4",
                  "duration_seconds": _V_DUR, "category": "video"}
        a_meta = {"relative_path": "rec/mix.wav", "abs_path": "rec/mix.wav",
                  "duration_seconds": _A_DUR, "category": "audio"}
        result = sync_module.synchronize_pair(
            v_meta, a_meta, model_local_path=_MODEL)
        if result.sync_status == "RESOLVED":
            assert result.relationship == RELATIONSHIP_SAME_EVENT


# =====================================================================
# SPARSE-EVIDENCE VERIFICATION WINDOWS
# =====================================================================

def _tk(phrase, vt, at, distinctiveness=1.0):
    """Helper to build a TemporalCandidate."""
    return sync_module.TemporalCandidate(
        phrase_id=phrase, video_time=vt, audio_time=at,
        video_occurrence=0, audio_occurrence=0,
        lexical_score=1.0, distinctiveness_score=distinctiveness,
    )


class TestEvidenceVerificationWindows:
    def _candidates_with_delta(self, delta, regions):
        """Build candidates grouped in separated video regions at given delta."""
        idx = 0
        out = []
        for vr_start in regions:
            for off in (0.0, 3.0, 6.0):
                vt = vr_start + off
                at = vt + delta
                out.append(_tk(f"p{idx}", vt, at))
                idx += 1
        return out

    def test_repeated_phrase_does_not_inflate_support(self):
        c = [
            _tk("repetido", 10.0, 55.0),
            _tk("repetido", 11.0, 56.0),
            _tk("repetido", 12.0, 57.0),
            _tk("otro", 20.0, 65.0),
            _tk("otro", 21.0, 66.0),
        ]
        dedup = sync_module._dedupe_evidence_candidates(c, 45.0)
        phrases = {d.phrase_id for d in dedup}
        assert phrases == {"repetido", "otro"}

    def test_three_separated_regions_produce_three_windows(self):
        c = self._candidates_with_delta(45.0, [100.0, 900.0, 1800.0])
        windows = build_evidence_verification_windows(c, 45.0, 3600.0)
        assert len(windows) == 3
        assert all(w < 3570.0 for w in windows)

    def test_single_region_yields_insufficient_windows(self):
        c = self._candidates_with_delta(45.0, [100.0])
        windows = build_evidence_verification_windows(c, 45.0, 3600.0)
        assert len(windows) < 3

    def test_max_five_windows_capped(self):
        c = self._candidates_with_delta(45.0, [100.0, 800.0, 1600.0, 2400.0, 3200.0, 3500.0])
        windows = build_evidence_verification_windows(c, 45.0, 3600.0)
        assert len(windows) <= 5

    def test_out_of_tolerance_phrases_excluded(self):
        c = [
            _tk("buena", 100.0, 145.0),
            _tk("ruidosa", 100.0, 1000.0),
        ]
        dedup = sync_module._dedupe_evidence_candidates(c, 45.0)
        assert {d.phrase_id for d in dedup} == {"buena"}


class TestSparseLocalAlignmentAnchors:
    def _anchors(self, windows, delta=45.0):
        out = []
        idx = 0
        for wt in windows:
            for off in (0.0, 5.0):
                out.append(sync_module.ContentAnchor(
                    f"tok{idx}", f"tok{idx}",
                    wt + off, wt + off + delta, 0, 0,
                    video_window_id=f"w{int(wt)}",
                ))
                idx += 1
        return out

    def test_fewer_than_three_windows_returns_empty(self):
        anchors = self._anchors([100.0, 500.0])
        assert build_sparse_local_alignment_anchors(anchors) == []

    def test_three_windows_builds_one_anchor_each(self):
        anchors = self._anchors([100.0, 900.0, 1800.0])
        local = build_sparse_local_alignment_anchors(anchors)
        assert len(local) == 3
        window_ids = {a.window_id for a in local}
        assert len(window_ids) == 3

    def test_standard_requires_three_per_window(self):
        # 3 windows but only 2 tokens each -> standard aggregation drops all
        anchors = self._anchors([100.0, 900.0, 1800.0])
        assert build_local_alignment_anchors(anchors) == []
        # but sparse aggregation keeps all 3 independent windows
        assert len(build_sparse_local_alignment_anchors(anchors)) == 3
