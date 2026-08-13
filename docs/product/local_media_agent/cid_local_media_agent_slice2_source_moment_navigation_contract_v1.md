# CID Local Media Agent — Slice 2 Source-Moment Navigation Contract V1

## Purpose

This increment adds deterministic, human-readable source-moment metadata to the existing transcript browse and search serialization. It packages already-authoritative identity, source-relative timing, and safe timecode state without opening media or changing source files.

## Source-Moment Schema

Each existing browse/search result receives one additive `source_moment` object:

```json
{
  "asset_id": "synthetic-asset",
  "segment_ref": "synthetic-asset::0::1",
  "segment_index": 1,
  "source_start_seconds": 12.0,
  "source_end_seconds": 13.0,
  "source_timecode_status": "available",
  "source_start_timecode": "00:00:12:00",
  "source_end_timecode": "00:00:13:00",
  "source_fps": {"numerator": 24, "denominator": 1},
  "navigation_descriptor": "asset_id=synthetic-asset; segment_ref=synthetic-asset::0::1; interval=12.0-13.0s; timecode_status=available"
}
```

The optional timecode fields are included only when present in the canonical result timecode mapping. Existing result fields remain unchanged.

## Deterministic Descriptor Format

The descriptor is exactly:

`asset_id=<asset_id>; segment_ref=<segment_ref>; interval=<source_start_seconds>-<source_end_seconds>s; timecode_status=<source_timecode_status>`

It is a local textual identifier only. It is not a URI, player command, filesystem path, network address, or media mutation instruction.

## Field Semantics

`asset_id`, `segment_ref`, and `segment_index` are copied from `TranscriptBrowseResult`. Source-relative seconds are copied without recalculation, rounding, or approximation. Original transcript `text` remains authoritative and is not rewritten.

## Timecode Status and Degradation

The canonical `source_timecode.status` is preserved. `available`, `unavailable`, `absent`, and `unsupported` remain distinct. Optional canonical timecode values are emitted only when actually present. No timecode is fabricated or inferred from seconds.

## Browse/Search Compatibility

The existing `cid transcript browse` and `cid transcript search` commands remain unchanged in name, options, input contract, ordering, matching, bounds, and error behavior. Their serialized results receive only the additive `source_moment` field. The frozen `TranscriptBrowseResult` implementation is not modified.

## CLI Integration

Integration uses the existing browse/search result serialization in `cid_cli.py`; no competing CLI framework or new required command is introduced. Explicit local JSON input remains the only transcript input boundary.

## Local-Only and Privacy Boundary

The packaging layer performs no filesystem discovery, media access, network call, database access, provider call, source-media write, external-player launch, or DaVinci control. Errors continue to use sanitized CLI conventions.

## Language Neutrality and Future Compatibility

The descriptor does not inspect or transform transcript text. Spanish, English, mixed-language, and accented text remain unchanged. No language detection, translation, diarization, ConversationUnit, or multilingual index is introduced; future annotation and localized-view layers remain possible.

## Explicit Exclusions

This increment does not implement semantic retrieval, Autonomous Editorial QA, OpenAI/Qdrant/Ollama, SRT export, frontend expansion, durable transcript persistence/reload, pilot-flow-to-browse durable handoff, external-player launching, or DaVinci/NLE integration.
