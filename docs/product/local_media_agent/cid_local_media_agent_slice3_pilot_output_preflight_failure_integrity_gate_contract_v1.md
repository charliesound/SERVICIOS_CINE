# CID Local Media Agent Slice 3 Output Preflight Failure Integrity Gate V1

## Scope

`SLICE3-G001` adds a final integrity gate to the published local pilot flow.
The flow may return `PILOT_FLOW_COMPLETED` only when provenance output has been
serialized into a non-empty canonical `transcript_segments` list.

## Contract

- Empty or non-list transcript output returns
  `PILOT_FLOW_OUTPUT_INTEGRITY_FAILED` at `output_preflight` with
  `TRANSCRIPT_SEGMENTS_EMPTY`.
- Any serialized segment that is not a dictionary with exactly the
  `TranscriptSegment.to_dict()` field set returns
  `PILOT_FLOW_OUTPUT_INTEGRITY_FAILED` with
  `TRANSCRIPT_SEGMENTS_NOT_CANONICAL`.
- Unexpected scanner and media-probe orchestration exceptions return fixed,
  sanitized error codes: `SCAN_ORCHESTRATION_FAILED` and
  `MEDIA_PROBE_ORCHESTRATION_FAILED`.
- Exception text, tracebacks, and local paths are never included in the result.
- Existing successful output, downstream handoff contracts, and GAP-008 remain
  unchanged.

## Validation

The contract is covered by synthetic unit tests for empty provenance output and
unexpected scanner failure. Validation must use the authorized targeted pilot
flow contract test command only for this increment.
