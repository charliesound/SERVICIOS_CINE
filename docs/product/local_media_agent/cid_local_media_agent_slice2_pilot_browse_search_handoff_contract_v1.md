# CID Local Media Agent — Pilot Browse/Search Handoff Contract V1

## Purpose

This bounded P0 increment closes GAP-003 by adapting the authoritative in-memory result returned by `run_pilot_flow` to the existing transcript browse, deterministic search, and source-moment serialization path.

## Handoff Input

The public entrypoint `handoff_pilot_transcript_segments` accepts either a completed pilot-flow result mapping containing `transcript_segments`, or the equivalent in-memory list of serialized segment dictionaries. It does not require a new intermediate JSON file and does not change `run_pilot_flow`.

## Canonical Reuse

The adapter reuses the existing serialized-segment deserialization, `browse_transcript`, and `search_transcript` contracts. It does not implement search, duplicate provenance models, or duplicate source-moment packaging. `cid_cli.py` reuses its existing result serialization, including the additive `source_moment` block.

## CLI Integration

`run_pilot_transcript_cli` is an additive same-process entrypoint in the existing CLI module. Existing `cid transcript browse --input ...` and `cid transcript search --input ...` commands and their explicit JSON input remain unchanged and supported.

## Output and Traceability

The handoff returns the existing browse/search result envelope. `asset_id`, `segment_ref`, `segment_index`, original text, source-relative start/end, canonical timecode state, and the existing deterministic source-moment descriptor remain unchanged.

## Determinism and Errors

Identical in-memory pilot results, operations, queries, offsets, and limits produce identical results and ordering. Invalid pilot result mappings, missing or non-list `transcript_segments`, invalid segment payloads, unsupported operations, and missing queries use sanitized `TranscriptBrowseInputError` codes.

## Local-Only Boundary

The adapter is pure in-memory packaging. It does not scan folders, inspect media, call ffprobe, transcribe, write transcript files, persist data, use the network/database/providers, or process source media.

## Language and Privacy

Transcript text is not inspected for language or rewritten. Spanish, English, mixed-language, and accented text remain authoritative. No translation, language detection, diarization, ConversationUnit, or multilingual index is introduced.

## Frozen Boundaries

`pilot_flow.py`, `transcript_browse.py`, `source_moment_navigation.py`, and the previously published tests and contract documents remain frozen. This increment changes only the new adapter, additive `cid_cli.py` integration, its focused test, and this contract document.

## Non-Goals

Durable persistence/reload, semantic retrieval, Autonomous Editorial QA, OpenAI/Qdrant/Ollama, translation, speaker diarization, ConversationUnit, multilingual editorial index, DaVinci/NLE, SRT, frontend expansion, DB/Alembic, Docker, SaaS changes, source-media writes, external-player launching, pilot-flow redesign, browse/search redesign, and source-moment redesign are excluded.
