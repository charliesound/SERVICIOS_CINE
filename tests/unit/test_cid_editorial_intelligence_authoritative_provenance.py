from __future__ import annotations

import json
from dataclasses import replace

import pytest

from scripts.editorial_intelligence.authoritative_provenance import (
    AssetIdentityConflictError,
    ProvenanceArtifactCorruptError,
    ProvenanceInputError,
    ProvenanceTemporalMappingError,
    ProvenanceTranscriptBindingError,
    SourceProvenanceInput,
    TranscriptIdentity,
    create_provenance_artifact,
    load_provenance_artifact,
    register_or_load_asset,
    transcript_segments_from_provenance,
    validate_provenance_artifact,
)
from scripts.editorial_intelligence.authoritative_provenance.provenance_artifact import (
    AUTH_BINDING_PROJECTION_CONTRACT_VERSION,
    BindingProjection,
    BindingProjectionRecord,
    _canonicalize_segment_indexes,
    build_binding_projection,
    rehash_binding_projection,
)
from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    PHASE,
    TranscriptSegment,
)


IDENTITY = TranscriptIdentity("a" * 64, 1234, 2)


def payload() -> dict:
    return {
        "asset_id": None,
        "segments": [
            {"segment_index": 0, "start_seconds": 0.0, "end_seconds": 2.5, "text": "A"},
            {"segment_index": 1, "start_seconds": 3.0, "end_seconds": 4.0, "text": "B"},
        ],
    }


def mapping(origin: float = 0.0) -> SourceProvenanceInput:
    return SourceProvenanceInput(
        source_time_origin_seconds=origin,
        source_audio_stream_index=1,
        sanitized_label="clip.mp4",
        fps_numerator=25,
        fps_denominator=1,
        timebase_numerator=1,
        timebase_denominator=25000,
        evidence_references=("metadata-report",),
    )


def artifact(tmp_path, origin: float = 0.0):
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    return create_provenance_artifact(asset, IDENTITY, mapping(origin), payload(), created_at="2026-08-08T00:00:00Z")


def test_uuid4_registry_is_persistent_and_idempotent(tmp_path):
    path = tmp_path / "registry.json"
    first = register_or_load_asset("asset-registration-a", registry_path=path)
    second = register_or_load_asset("asset-registration-a", registry_path=path)
    assert first.asset_id == second.asset_id
    assert len(first.asset_id) == 36
    assert path.exists()


def test_registry_reload_and_conflict_fail_closed(tmp_path):
    path = tmp_path / "registry.json"
    register_or_load_asset("asset-registration-a", sanitized_label="a.mp4", registry_path=path)
    assert register_or_load_asset("asset-registration-a", registry_path=path).sanitized_label == "a.mp4"
    with pytest.raises(AssetIdentityConflictError):
        register_or_load_asset("asset-registration-a", sanitized_label="b.mp4", registry_path=path)


def test_corrupt_registry_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text("{bad", encoding="utf-8")
    with pytest.raises(ProvenanceArtifactCorruptError):
        register_or_load_asset("asset-registration-a", registry_path=path)


def test_artifact_derives_source_times_once_for_zero_and_nonzero_origin(tmp_path):
    zero = artifact(tmp_path, 0.0)
    shifted = artifact(tmp_path, 12.5)
    assert zero.segments[0]["source_start_seconds"] == 0.0
    assert zero.segments[1]["source_end_seconds"] == 4.0
    assert shifted.segments[0]["source_start_seconds"] == 12.5
    assert shifted.segments[1]["source_end_seconds"] == 16.5


def test_artifact_round_trip_and_transcript_segments(tmp_path):
    path = tmp_path / "artifact.json"
    value = artifact(tmp_path)
    path.write_text(json.dumps(value.to_dict()), encoding="utf-8")
    loaded = load_provenance_artifact(path, IDENTITY)
    segments = transcript_segments_from_provenance(payload(), IDENTITY, loaded)
    assert segments[0].asset_id == value.asset_id
    assert segments[0].segment_ref.endswith("::1::0")
    assert segments[1].source_start_seconds == 3.0


def test_transcript_binding_and_segment_mapping_mismatch_fail(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(ProvenanceTranscriptBindingError):
        validate_provenance_artifact(value, replace(IDENTITY, transcript_bytes=1235))
    altered = payload()
    altered["segments"][0]["start_seconds"] = 1.0
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(altered, IDENTITY, value)


def test_invalid_temporal_values_fail_closed(tmp_path):
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    with pytest.raises(ProvenanceTemporalMappingError):
        create_provenance_artifact(asset, IDENTITY, mapping(-1.0), payload(), created_at="now")
    invalid = payload()
    invalid["segments"][1]["end_seconds"] = 2.0
    invalid["segments"][1]["start_seconds"] = 3.0
    with pytest.raises(ProvenanceTemporalMappingError):
        create_provenance_artifact(asset, IDENTITY, mapping(), invalid, created_at="now")


def test_schema_corruption_and_path_registration_rejected(tmp_path):
    path = tmp_path / "artifact.json"
    path.write_text(json.dumps({"schema_version": "wrong"}), encoding="utf-8")
    with pytest.raises(ProvenanceArtifactCorruptError):
        load_provenance_artifact(path)
    with pytest.raises(ValueError):
        register_or_load_asset("/absolute/path", registry_path=tmp_path / "registry.json")


def test_asset_identity_is_independent_of_path_and_transcript():
    assert "path" not in "asset-registration-a"
    assert "transcript" not in "asset-registration-a"


def test_different_registration_keys_get_different_ids(tmp_path):
    path = tmp_path / "registry.json"
    first = register_or_load_asset("asset-registration-a", registry_path=path)
    second = register_or_load_asset("asset-registration-b", registry_path=path)
    assert first.asset_id != second.asset_id


def test_registry_schema_version_mismatch_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema_version": "old", "assets": {}}), encoding="utf-8")
    with pytest.raises(ProvenanceArtifactCorruptError):
        register_or_load_asset("asset-registration-a", registry_path=path)


def test_registry_invalid_asset_id_fails_closed(tmp_path):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"schema_version": "CID.MEDIA_ASSET_REGISTRY.V1", "assets": {"a": {"asset_id": "bad"}}}), encoding="utf-8")
    with pytest.raises(ProvenanceArtifactCorruptError):
        register_or_load_asset("a", registry_path=path)


def test_transcript_sha_mismatch_is_rejected(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(ProvenanceTranscriptBindingError):
        from scripts.editorial_intelligence.authoritative_provenance import validate_provenance_artifact
        validate_provenance_artifact(value, replace(IDENTITY, transcript_sha256="b" * 64))


def test_transcript_segment_count_mismatch_is_rejected(tmp_path):
    with pytest.raises(ProvenanceTranscriptBindingError):
        create_provenance_artifact(
            register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json"),
            replace(IDENTITY, transcript_segment_count=3), mapping(), payload(), created_at="now"
        )


def test_transcript_byte_count_must_be_positive(tmp_path):
    with pytest.raises(ProvenanceTranscriptBindingError):
        create_provenance_artifact(
            register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json"),
            replace(IDENTITY, transcript_bytes=0), mapping(), payload(), created_at="now"
        )


def test_missing_source_origin_is_rejected(tmp_path):
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    with pytest.raises(ProvenanceTemporalMappingError):
        create_provenance_artifact(asset, IDENTITY, replace(mapping(), source_time_origin_seconds=None), payload(), created_at="now")


def test_nan_source_origin_is_rejected(tmp_path):
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    with pytest.raises(ProvenanceTemporalMappingError):
        create_provenance_artifact(asset, IDENTITY, replace(mapping(), source_time_origin_seconds=float("nan")), payload(), created_at="now")


def test_non_finite_segment_time_is_rejected(tmp_path):
    invalid = payload()
    invalid["segments"][0]["start_seconds"] = float("inf")
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    with pytest.raises(ProvenanceTemporalMappingError):
        create_provenance_artifact(asset, IDENTITY, mapping(), invalid, created_at="now")


def test_invalid_timecode_status_is_rejected(tmp_path):
    asset = register_or_load_asset("asset-registration-a", registry_path=tmp_path / "registry.json")
    with pytest.raises(ValueError):
        create_provenance_artifact(asset, IDENTITY, replace(mapping(), timecode_status="present"), payload(), created_at="now")


def test_rational_fps_and_timebase_are_preserved(tmp_path):
    value = artifact(tmp_path)
    assert value.fps_numerator == 25
    assert value.fps_denominator == 1
    assert value.timebase_numerator == 1
    assert value.timebase_denominator == 25000
    assert value.timecode_status == "unavailable"


def test_segment_indexes_must_be_complete(tmp_path):
    value = artifact(tmp_path)
    broken = replace(value, segments=(value.segments[0], {**value.segments[1], "segment_index": 0}))
    with pytest.raises(ProvenanceArtifactCorruptError):
        from scripts.editorial_intelligence.authoritative_provenance import validate_provenance_artifact
        validate_provenance_artifact(broken, IDENTITY)


def test_source_mapping_inconsistency_is_rejected(tmp_path):
    value = artifact(tmp_path)
    broken = replace(value, segments=({**value.segments[0], "source_start_seconds": 9.0}, value.segments[1]))
    with pytest.raises(ProvenanceTemporalMappingError):
        from scripts.editorial_intelligence.authoritative_provenance import validate_provenance_artifact
        validate_provenance_artifact(broken, IDENTITY)


def test_artifact_asset_identity_is_not_replaced_on_reload(tmp_path):
    registry = tmp_path / "registry.json"
    asset = register_or_load_asset("asset-registration-a", registry_path=registry)
    artifact_value = artifact(tmp_path)
    assert artifact_value.asset_id == asset.asset_id


def test_transcript_segment_source_interval_is_publicly_usable(tmp_path):
    segments = transcript_segments_from_provenance(payload(), IDENTITY, artifact(tmp_path, 12.5))
    assert segments[0].source_start_seconds == 12.5
    assert segments[0].source_end_seconds == 15.0
    assert segments[0].source_timecode["available"] is False


def test_wrong_sha_same_shape_fails_before_segment_construction(tmp_path):
    value = artifact(tmp_path)
    wrong = replace(IDENTITY, transcript_sha256="b" * 64)
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(payload(), wrong, value)


def test_wrong_bytes_same_shape_fails_before_segment_construction(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(payload(), replace(IDENTITY, transcript_bytes=999), value)


def test_wrong_segment_count_fails_before_segment_construction(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(payload(), replace(IDENTITY, transcript_segment_count=3), value)


def test_compatible_timing_shape_cannot_replace_identity(tmp_path):
    value = artifact(tmp_path)
    compatible = {**payload(), "source_filename": "different-transcript.json"}
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(compatible, replace(IDENTITY, transcript_sha256="c" * 64), value)


def test_missing_identity_argument_has_no_two_argument_fallback(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(TypeError):
        transcript_segments_from_provenance(payload(), value)


def test_artifact_identity_cannot_supply_caller_identity(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(TypeError):
        transcript_segments_from_provenance(payload(), artifact=value)


def test_identity_mismatch_does_not_create_partial_segments(tmp_path):
    value = artifact(tmp_path)
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(payload(), replace(IDENTITY, transcript_bytes=1), value)


def test_all_three_identity_fields_are_required_for_acceptance(tmp_path):
    value = artifact(tmp_path)
    for identity in (
        replace(IDENTITY, transcript_sha256="d" * 64),
        replace(IDENTITY, transcript_bytes=1),
        replace(IDENTITY, transcript_segment_count=1),
    ):
        with pytest.raises(ProvenanceTranscriptBindingError):
            transcript_segments_from_provenance(payload(), identity, value)


def one_based_payload() -> dict:
    value = payload()
    value["segments"] = [
        {**value["segments"][0], "segment_index": 1},
        {**value["segments"][1], "segment_index": 2},
    ]
    return value


def test_one_based_indexes_are_canonicalized_without_payload_mutation(tmp_path):
    value = one_based_payload()
    snapshot = json.loads(json.dumps(value))
    identity = replace(IDENTITY, transcript_segment_count=2)
    artifact_value = create_provenance_artifact(
        register_or_load_asset("one-based", registry_path=tmp_path / "registry.json"),
        identity,
        mapping(12.5),
        value,
        created_at="now",
    )
    segments = transcript_segments_from_provenance(value, identity, artifact_value)
    assert [item["segment_index"] for item in artifact_value.segments] == [0, 1]
    assert [segment.segment_ref.rsplit("::", 1)[-1] for segment in segments] == ["0", "1"]
    assert value == snapshot


@pytest.mark.parametrize(
    "indexes",
    [[1, 2, 4], [0, 1, 3], [1, 1, 2], [0, 2, 1], [-1, 0, 1], [2, 3, 4], ["0", 1], [0.0, 1], [True, 1]],
)
def test_unsupported_segment_index_layouts_fail_closed(indexes):
    with pytest.raises(ValueError):
        _canonicalize_segment_indexes([{"segment_index": index} for index in indexes])


@pytest.mark.parametrize("indexes", [[0], [1]])
def test_single_segment_supported_for_both_bases(indexes):
    assert _canonicalize_segment_indexes([{"segment_index": indexes[0]}]) == [0]


def test_artifact_and_binding_share_one_based_interpretation(tmp_path):
    value = one_based_payload()
    identity = replace(IDENTITY, transcript_segment_count=2)
    artifact_value = create_provenance_artifact(
        register_or_load_asset("shared-rule", registry_path=tmp_path / "registry.json"),
        identity,
        mapping(),
        value,
        created_at="now",
    )
    segments = transcript_segments_from_provenance(value, identity, artifact_value)
    assert [item["segment_index"] for item in artifact_value.segments] == [segment.segment_index for segment in segments]


def test_wrong_identity_rejects_before_one_based_binding(tmp_path):
    value = one_based_payload()
    identity = replace(IDENTITY, transcript_segment_count=2)
    artifact_value = create_provenance_artifact(
        register_or_load_asset("identity-order", registry_path=tmp_path / "registry.json"),
        identity,
        mapping(),
        value,
        created_at="now",
    )
    with pytest.raises(ProvenanceTranscriptBindingError):
        transcript_segments_from_provenance(value, replace(identity, transcript_sha256="b" * 64), artifact_value)


def projection_segments() -> list[TranscriptSegment]:
    source_timecode = {"available": False, "status": "unavailable"}
    return [
        TranscriptSegment(
            phase=PHASE,
            asset_id="asset-synthetic",
            source_audio_stream_index=0,
            segment_index=2,
            text="Café\nfin",
            stt_start_seconds=1.25,
            stt_end_seconds=3.5,
            source_start_seconds=101.25,
            source_end_seconds=103.5,
            source_timecode=source_timecode,
            provenance={"asset_id": "asset-synthetic", "segment_index": 2, "source_audio_stream_index": 0},
            error=None,
            warnings=["synthetic-warning"],
        ),
        TranscriptSegment(
            phase=PHASE,
            asset_id="asset-synthetic",
            source_audio_stream_index=0,
            segment_index=1,
            text="Árbol  ",
            stt_start_seconds=0.0,
            stt_end_seconds=1.0,
            source_start_seconds=100.0,
            source_end_seconds=101.0,
            source_timecode=source_timecode,
            provenance={"asset_id": "asset-synthetic", "segment_index": 1, "source_audio_stream_index": 0},
            error=None,
            warnings=[],
        ),
    ]


def test_binding_projection_golden_vector_is_frozen():
    result = build_binding_projection(projection_segments())
    assert isinstance(result, BindingProjection)
    assert result.contract_version == AUTH_BINDING_PROJECTION_CONTRACT_VERSION
    assert result.canonical_byte_count == 1305
    assert result.sha256 == "6c0267f89e106b1a446e542265e4d6a28d163b26b898bd4aff5a6c433353a82c"
    assert result.canonical_bytes.endswith(b"\n")
    assert b"Caf\xc3\xa9" not in result.canonical_bytes
    assert b"asset-synthetic::0::1" in result.canonical_bytes


def test_binding_projection_is_input_order_independent():
    forward = build_binding_projection(projection_segments())
    reverse = build_binding_projection(list(reversed(projection_segments())))
    assert reverse.canonical_bytes == forward.canonical_bytes
    assert reverse.sha256 == forward.sha256


def test_binding_projection_types_are_immutable():
    result = build_binding_projection(projection_segments())
    assert isinstance(result.records[0], BindingProjectionRecord)
    with pytest.raises(AttributeError):
        result.records = ()
    with pytest.raises(AttributeError):
        result.records[0].asset_id = "changed"


def test_binding_projection_rehash_requires_only_canonical_bytes(tmp_path):
    result = build_binding_projection(projection_segments())
    path = tmp_path / "binding_projection_durable_reproducible_v1.json"
    path.write_bytes(result.canonical_bytes)
    reopened = path.read_bytes()
    assert rehash_binding_projection(reopened) == (1305, result.sha256)


def test_binding_projection_single_byte_mutation_changes_hash():
    result = build_binding_projection(projection_segments())
    mutated = bytearray(result.canonical_bytes)
    mutated[20] ^= 1
    assert rehash_binding_projection(bytes(mutated))[1] != result.sha256


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_binding_projection_nonfinite_times_fail_closed(value):
    with pytest.raises(ProvenanceTemporalMappingError):
        build_binding_projection([replace(projection_segments()[0], stt_start_seconds=value)])


def test_binding_projection_negative_zero_is_canonicalized():
    result = build_binding_projection([replace(projection_segments()[0], stt_start_seconds=-0.0)])
    assert result.records[0].stt_start_seconds == "0x0.0p+0"


def test_binding_projection_preserves_integer_like_float_representation():
    result = build_binding_projection(
        [replace(projection_segments()[0], stt_start_seconds=0.0, stt_end_seconds=1.0)]
    )
    assert result.records[0].stt_end_seconds == "0x1.0000000000000p+0"


def test_binding_projection_duplicate_identity_fails_closed():
    segments = projection_segments()
    duplicate = replace(segments[0], text="different")
    with pytest.raises(ProvenanceInputError):
        build_binding_projection([segments[0], duplicate])


def test_binding_projection_exact_segment_reference_and_asset_are_projected():
    result = build_binding_projection(projection_segments())
    assert [record.segment_ref for record in result.records] == [
        "asset-synthetic::0::1",
        "asset-synthetic::0::2",
    ]
    assert all(record.asset_id == "asset-synthetic" for record in result.records)


def test_binding_projection_rejects_invalid_segment_reference():
    segment = replace(projection_segments()[0], asset_id="bad/name")
    with pytest.raises(ProvenanceInputError):
        build_binding_projection([segment])


def test_binding_projection_preserves_text_newline_and_trailing_whitespace_in_digest():
    base = build_binding_projection([projection_segments()[0]])
    changed = build_binding_projection([replace(projection_segments()[0], text="Café\nfin ")])
    assert base.sha256 != changed.sha256
