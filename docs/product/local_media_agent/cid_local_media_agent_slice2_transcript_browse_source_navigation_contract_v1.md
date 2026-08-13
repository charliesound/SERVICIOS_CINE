# CID Local Media Agent — Slice 2 Transcript Browse and Source Navigation Contract V1

## Purpose

This contract defines the first bounded Slice-2 increment: deterministic ordered browsing and case-insensitive plain-text search over already-produced `TranscriptSegment` values.

## Non-goals

This increment does not perform scanning, probing, transcription, embeddings, semantic retrieval, generation, translation, diarization, ConversationUnit construction, frontend work, DaVinci/NLE integration, or SRT export.

## Authoritative transcript rule

The canonical `scripts.editorial_intelligence.transcript_provenance.transcript_segment.TranscriptSegment` is consumed directly. `TranscriptSegment.text` remains the authoritative original transcript text. Browse and search never rewrite returned text.

## Browse semantics

`browse_transcript(segments, offset=0, limit=20)` returns an ordered bounded projection of the input segments. Input order is preserved, inputs are not mutated, `offset` must be non-negative, and `limit` must be positive and no greater than `MAX_BROWSE_RESULTS` (`100`).

## Deterministic search semantics

`search_transcript(segments, query, limit=20)` performs `DETERMINISTIC_CASE_INSENSITIVE_SUBSTRING` matching using Python Unicode `casefold()` only for comparison. A query must be non-empty and non-whitespace. Matching occurs independently within each segment; segments are never concatenated, stemmed, fuzzily matched, or semantically retrieved.

## Result and source traceability

`TranscriptBrowseResult` preserves `asset_id`, `segment_ref`, `segment_index`, exact `text`, `source_start_seconds`, `source_end_seconds`, and the canonical `source_timecode` mapping. These fields identify the source moment without opening an external player or modifying source media.

## Source-relative timing and timecode degradation

Source-relative seconds are passed through from the canonical segment. Existing safe timecode semantics are preserved exactly. An unavailable or unsupported timecode is not fabricated; source-relative seconds remain available.

## Result limits

`MAX_BROWSE_RESULTS=100` and `MAX_SEARCH_RESULTS=100`. These bounds prevent unbounded terminal output and are independent of model or context limits.

## CLI integration

The existing dispatcher exposes explicit local operations:

```text
cid transcript browse --input TRANSCRIPT_JSON [--offset N] [--limit N]
cid transcript search --input TRANSCRIPT_JSON --query QUERY [--limit N]
```

The input must be explicitly selected JSON containing `transcript_segments` or a segment list. The CLI does not scan media, retranscribe, enumerate volumes, discover arbitrary files, or contact a service. Output is sanitized structured JSON.

## Privacy and local-only behavior

No network, upload, database, source-media write, external-player launch, or external application control is used or required. CLI failures emit sanitized argument errors rather than stack traces.

## Multilingual future compatibility

This contract introduces no language lock-in. It preserves original text and stable segment identity while leaving room for future per-turn language annotations, localized views, project editorial languages, speaker turns, conversation units, and multilingual indexes. Document-level language metadata is not treated as per-segment truth.

## Explicit exclusions

Semantic Search and vector retrieval are excluded. Autonomous Editorial QA and all generation providers are excluded. DaVinci/NLE integration and SRT export are excluded.
