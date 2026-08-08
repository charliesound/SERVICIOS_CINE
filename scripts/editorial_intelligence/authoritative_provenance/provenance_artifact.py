from __future__ import annotations

import json
import math
import os
import re
import tempfile
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
    TranscriptSegment,
    transcription_result_to_transcript_segments,
)


SCHEMA_VERSION = "CID.AUTHORITATIVE_PROVENANCE_ARTIFACT.V1"
REGISTRY_SCHEMA_VERSION = "CID.MEDIA_ASSET_REGISTRY.V1"
PROVENANCE_VERSION = "CID.LOCAL_MEDIA_AGENT.EDITORIAL_INTELLIGENCE.PROVENANCE.V1"
DEFAULT_REGISTRY_PATH = Path(
    "/home/harliesound/cid_benchmark_input/asset_registry/cid_media_assets_v1.json"
)
SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS = 1e-6
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class ProvenanceArtifactError(ValueError):
    pass


class AssetIdentityConflictError(ProvenanceArtifactError):
    pass


class ProvenanceArtifactCorruptError(ProvenanceArtifactError):
    pass


class ProvenanceTranscriptBindingError(ProvenanceArtifactError):
    pass


class ProvenanceInputError(ProvenanceArtifactError):
    pass


class ProvenanceTemporalMappingError(ProvenanceArtifactError):
    pass


@dataclass(frozen=True, slots=True)
class AssetIdentity:
    registration_key: str
    asset_id: str
    sanitized_label: str | None = None


@dataclass(frozen=True, slots=True)
class TranscriptIdentity:
    transcript_sha256: str
    transcript_bytes: int
    transcript_segment_count: int


@dataclass(frozen=True, slots=True)
class SourceProvenanceInput:
    source_time_origin_seconds: float
    source_audio_stream_index: int | None = None
    sanitized_label: str | None = None
    internal_reference_local_only: str | None = None
    fps_numerator: int | None = None
    fps_denominator: int | None = None
    timebase_numerator: int | None = None
    timebase_denominator: int | None = None
    timecode_status: str = "unavailable"
    evidence_references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AuthoritativeProvenanceArtifact:
    schema_version: str
    provenance_version: str
    registration_key: str
    asset_id: str
    asset_identity_method: str
    transcript_sha256: str
    transcript_bytes: int
    transcript_segment_count: int
    source_identity: dict[str, str | None]
    source_time_origin_seconds: float
    fps_numerator: int | None
    fps_denominator: int | None
    timebase_numerator: int | None
    timebase_denominator: int | None
    timecode_status: str
    segments: tuple[dict[str, Any], ...]
    creation_method: str
    created_at: str
    evidence_references: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["segments"] = [dict(segment) for segment in self.segments]
        value["evidence_references"] = list(self.evidence_references)
        return value


def register_or_load_asset(
    registration_key: str,
    *,
    sanitized_label: str | None = None,
    registry_path: str | Path = DEFAULT_REGISTRY_PATH,
) -> AssetIdentity:
    key = _validate_registration_key(registration_key)
    label = _sanitize_label(sanitized_label)
    path = Path(registry_path)
    registry = _load_registry(path)
    existing = registry["assets"].get(key)
    if existing is not None:
        asset_id = existing.get("asset_id")
        if not isinstance(asset_id, str) or not _is_uuid4(asset_id):
            raise ProvenanceArtifactCorruptError("asset registry identity is invalid")
        stored_label = existing.get("sanitized_label")
        if label is not None and stored_label not in (None, label):
            raise AssetIdentityConflictError("asset registration identity conflicts")
        return AssetIdentity(key, asset_id, stored_label or label)

    asset = AssetIdentity(key, str(uuid.uuid4()), label)
    registry["assets"][key] = {
        "asset_id": asset.asset_id,
        "sanitized_label": asset.sanitized_label,
    }
    _atomic_write_json(path, registry)
    return asset


def create_provenance_artifact(
    asset: AssetIdentity,
    transcript_identity: TranscriptIdentity,
    mapping: SourceProvenanceInput,
    transcript_payload: Mapping[str, Any],
    *,
    created_at: str,
) -> AuthoritativeProvenanceArtifact:
    _validate_asset(asset)
    _validate_transcript_identity(transcript_identity)
    if not isinstance(created_at, str) or not created_at.strip():
        raise ProvenanceInputError("created_at is required")
    segments_raw = transcript_payload.get("segments")
    if not isinstance(segments_raw, list):
        raise ProvenanceInputError("transcript segments are required")
    if len(segments_raw) != transcript_identity.transcript_segment_count:
        raise ProvenanceTranscriptBindingError("transcript segment count mismatch")
    _validate_source_input(mapping)
    canonical_indexes = _canonicalize_segment_indexes(segments_raw)
    segments: list[dict[str, Any]] = []
    for canonical_index, raw in zip(canonical_indexes, segments_raw):
        _, start, end = _local_interval(raw)
        segments.append(
            {
                "segment_index": canonical_index,
                "stt_start_seconds": start,
                "stt_end_seconds": end,
                "source_start_seconds": mapping.source_time_origin_seconds + start,
                "source_end_seconds": mapping.source_time_origin_seconds + end,
                "source_audio_stream_index": mapping.source_audio_stream_index,
            }
        )
    artifact = AuthoritativeProvenanceArtifact(
        schema_version=SCHEMA_VERSION,
        provenance_version=PROVENANCE_VERSION,
        registration_key=asset.registration_key,
        asset_id=asset.asset_id,
        asset_identity_method="CID_PERSISTED_ASSET",
        transcript_sha256=transcript_identity.transcript_sha256,
        transcript_bytes=transcript_identity.transcript_bytes,
        transcript_segment_count=transcript_identity.transcript_segment_count,
        source_identity={
            "sanitized_label": mapping.sanitized_label or asset.sanitized_label,
            "internal_reference_local_only": mapping.internal_reference_local_only,
        },
        source_time_origin_seconds=mapping.source_time_origin_seconds,
        fps_numerator=mapping.fps_numerator,
        fps_denominator=mapping.fps_denominator,
        timebase_numerator=mapping.timebase_numerator,
        timebase_denominator=mapping.timebase_denominator,
        timecode_status=mapping.timecode_status,
        segments=tuple(segments),
        creation_method="CID_AUTHORITATIVE_PROVENANCE_BINDING",
        created_at=created_at,
        evidence_references=tuple(mapping.evidence_references),
    )
    validate_provenance_artifact(artifact, transcript_identity)
    return artifact


def validate_provenance_artifact(
    artifact: AuthoritativeProvenanceArtifact,
    transcript_identity: TranscriptIdentity,
) -> None:
    if not isinstance(artifact, AuthoritativeProvenanceArtifact):
        raise ProvenanceArtifactCorruptError("invalid provenance artifact")
    if artifact.schema_version != SCHEMA_VERSION:
        raise ProvenanceArtifactCorruptError("unsupported provenance schema")
    _validate_asset_id(artifact.asset_id)
    if artifact.asset_identity_method != "CID_PERSISTED_ASSET":
        raise ProvenanceArtifactCorruptError("unsupported asset identity method")
    _validate_transcript_identity(transcript_identity)
    if (
        artifact.transcript_sha256 != transcript_identity.transcript_sha256
        or artifact.transcript_bytes != transcript_identity.transcript_bytes
        or artifact.transcript_segment_count != transcript_identity.transcript_segment_count
    ):
        raise ProvenanceTranscriptBindingError("provenance transcript binding mismatch")
    if not _finite_non_negative(artifact.source_time_origin_seconds):
        raise ProvenanceTemporalMappingError("source time origin is invalid")
    if artifact.timecode_status not in {"available", "unavailable", "unsupported"}:
        raise ProvenanceArtifactCorruptError("invalid timecode status")
    if len(artifact.segments) != artifact.transcript_segment_count:
        raise ProvenanceArtifactCorruptError("provenance segment count mismatch")
    indexes: set[int] = set()
    for segment in artifact.segments:
        index = segment.get("segment_index")
        if isinstance(index, bool) or not isinstance(index, int) or index in indexes:
            raise ProvenanceArtifactCorruptError("provenance segment index is invalid")
        indexes.add(index)
        start = segment.get("stt_start_seconds")
        end = segment.get("stt_end_seconds")
        source_start = segment.get("source_start_seconds")
        source_end = segment.get("source_end_seconds")
        if not all(_finite_non_negative(value) for value in (start, end, source_start, source_end)):
            raise ProvenanceTemporalMappingError("provenance temporal value is invalid")
        if end < start or source_end < source_start:
            raise ProvenanceTemporalMappingError("provenance interval is invalid")
        if abs(source_start - (artifact.source_time_origin_seconds + start)) > SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS:
            raise ProvenanceTemporalMappingError("source start mapping is inconsistent")
        if abs(source_end - (artifact.source_time_origin_seconds + end)) > SOURCE_RELATIVE_VERIFY_TOLERANCE_SECONDS:
            raise ProvenanceTemporalMappingError("source end mapping is inconsistent")
    if indexes != set(range(artifact.transcript_segment_count)):
        raise ProvenanceArtifactCorruptError("provenance segment indexes are incomplete")


def load_provenance_artifact(
    path: str | Path,
    transcript_identity: TranscriptIdentity | None = None,
) -> AuthoritativeProvenanceArtifact:
    try:
        with Path(path).open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ProvenanceArtifactCorruptError("provenance artifact cannot be loaded") from exc
    try:
        artifact = _artifact_from_dict(value)
    except (KeyError, TypeError, ValueError) as exc:
        raise ProvenanceArtifactCorruptError("provenance artifact fields are invalid") from exc
    if transcript_identity is not None:
        validate_provenance_artifact(artifact, transcript_identity)
    return artifact


def transcript_segments_from_provenance(
    transcript_payload: Mapping[str, Any],
    transcript_identity: TranscriptIdentity,
    artifact: AuthoritativeProvenanceArtifact,
) -> list[TranscriptSegment]:
    _validate_transcript_identity(transcript_identity)
    validate_provenance_artifact(artifact, transcript_identity)
    segments_by_index = {item["segment_index"]: item for item in artifact.segments}
    raw_segments = transcript_payload.get("segments")
    if not isinstance(raw_segments, list) or len(raw_segments) != artifact.transcript_segment_count:
        raise ProvenanceTranscriptBindingError("transcript segment count mismatch")
    canonical_indexes = _canonicalize_segment_indexes(raw_segments)
    enriched = dict(transcript_payload)
    enriched["asset_id"] = artifact.asset_id
    enriched["source_audio_stream_index"] = artifact.segments[0].get("source_audio_stream_index")
    enriched["segments"] = []
    for canonical_index, raw in zip(canonical_indexes, raw_segments):
        mapping = segments_by_index.get(canonical_index)
        if mapping is None or raw.get("start_seconds") != mapping["stt_start_seconds"] or raw.get("end_seconds") != mapping["stt_end_seconds"]:
            raise ProvenanceTranscriptBindingError("transcript segment mapping mismatch")
        enriched["segments"].append({
            **raw,
            "segment_index": canonical_index,
            "source_start_seconds": mapping["source_start_seconds"],
            "source_end_seconds": mapping["source_end_seconds"],
        })
    return transcription_result_to_transcript_segments(enriched, extraction_anchor_seconds=artifact.source_time_origin_seconds)


def _load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": REGISTRY_SCHEMA_VERSION, "assets": {}}
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
        if value.get("schema_version") != REGISTRY_SCHEMA_VERSION or not isinstance(value.get("assets"), dict):
            raise ValueError
        for key, item in value["assets"].items():
            if not isinstance(key, str) or not isinstance(item, dict) or not _is_uuid4(item.get("asset_id")):
                raise ValueError
        return value
    except (OSError, json.JSONDecodeError, AttributeError, TypeError, ValueError) as exc:
        raise ProvenanceArtifactCorruptError("asset registry is invalid") from exc


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise ProvenanceArtifactError("asset registry could not be persisted")


def _artifact_from_dict(value: Any) -> AuthoritativeProvenanceArtifact:
    if not isinstance(value, dict):
        raise TypeError
    segments = value["segments"]
    references = value["evidence_references"]
    if not isinstance(segments, list) or not isinstance(references, list):
        raise TypeError
    return AuthoritativeProvenanceArtifact(
        schema_version=value["schema_version"],
        provenance_version=value["provenance_version"],
        registration_key=value["registration_key"],
        asset_id=value["asset_id"],
        asset_identity_method=value["asset_identity_method"],
        transcript_sha256=value["transcript_sha256"],
        transcript_bytes=value["transcript_bytes"],
        transcript_segment_count=value["transcript_segment_count"],
        source_identity=value["source_identity"],
        source_time_origin_seconds=value["source_time_origin_seconds"],
        fps_numerator=value["fps_numerator"],
        fps_denominator=value["fps_denominator"],
        timebase_numerator=value["timebase_numerator"],
        timebase_denominator=value["timebase_denominator"],
        timecode_status=value["timecode_status"],
        segments=tuple(segments),
        creation_method=value["creation_method"],
        created_at=value["created_at"],
        evidence_references=tuple(references),
    )


def _validate_registration_key(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ProvenanceInputError("registration key is required")
    if value.startswith(("/", "\\")) or ":\\" in value or value.startswith("/mnt/"):
        raise ProvenanceInputError("registration key must not be a path")
    return value.strip()


def _sanitize_label(value: str | None) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ProvenanceInputError("source label is invalid")
    return Path(value).name


def _validate_asset(asset: AssetIdentity) -> None:
    if not isinstance(asset, AssetIdentity) or not _validate_registration_key(asset.registration_key):
        raise ProvenanceInputError("asset identity is invalid")
    _validate_asset_id(asset.asset_id)


def _validate_asset_id(value: Any) -> None:
    if not isinstance(value, str) or not _is_uuid4(value):
        raise ProvenanceInputError("asset_id must be a UUID4")


def _is_uuid4(value: Any) -> bool:
    return isinstance(value, str) and _UUID_PATTERN.fullmatch(value) is not None


def _validate_transcript_identity(identity: TranscriptIdentity) -> None:
    if not isinstance(identity, TranscriptIdentity) or not re.fullmatch(r"[0-9a-f]{64}", identity.transcript_sha256):
        raise ProvenanceTranscriptBindingError("transcript identity is invalid")
    if not isinstance(identity.transcript_bytes, int) or identity.transcript_bytes <= 0:
        raise ProvenanceTranscriptBindingError("transcript byte count is invalid")
    if not isinstance(identity.transcript_segment_count, int) or identity.transcript_segment_count <= 0:
        raise ProvenanceTranscriptBindingError("transcript segment count is invalid")


def _validate_source_input(mapping: SourceProvenanceInput) -> None:
    if not isinstance(mapping, SourceProvenanceInput) or not _finite_non_negative(mapping.source_time_origin_seconds):
        raise ProvenanceTemporalMappingError("source time origin is required")
    if mapping.timecode_status not in {"available", "unavailable", "unsupported"}:
        raise ProvenanceInputError("timecode status is invalid")
    for value in (mapping.fps_numerator, mapping.fps_denominator, mapping.timebase_numerator, mapping.timebase_denominator):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
            raise ProvenanceInputError("rational timebase is invalid")


def _canonicalize_segment_indexes(segments_raw: list[Any]) -> list[int]:
    raw_indexes: list[int] = []
    for raw in segments_raw:
        if not isinstance(raw, dict):
            raise ProvenanceInputError("transcript segment is invalid")
        index = raw.get("segment_index")
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            raise ProvenanceInputError("transcript segment index is invalid")
        raw_indexes.append(index)
    if raw_indexes not in (list(range(len(raw_indexes))), list(range(1, len(raw_indexes) + 1))):
        raise ProvenanceInputError("transcript segment indexes must be contiguous and zero- or one-based")
    return list(range(len(raw_indexes)))


def _local_interval(raw: Any) -> tuple[int, float, float]:
    if not isinstance(raw, dict):
        raise ProvenanceInputError("transcript segment is invalid")
    index = raw.get("segment_index")
    start = raw.get("start_seconds")
    end = raw.get("end_seconds")
    if isinstance(index, bool) or not isinstance(index, int) or index < 0:
        raise ProvenanceInputError("transcript segment index is invalid")
    if not _finite_non_negative(start) or not _finite_non_negative(end) or end < start:
        raise ProvenanceTemporalMappingError("transcript segment interval is invalid")
    return index, float(start), float(end)


def _finite_non_negative(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) and float(value) >= 0
