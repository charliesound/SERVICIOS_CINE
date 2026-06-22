# CID Local Media Agent - FFprobe Controlled File Metadata Visible Report Renderer CLI Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.CONTRACT.V1`

## Objective

Define how a future local-only CLI should expose the already implemented pure renderer for controlled ffprobe metadata visible reports.

This is a CLI contract only.

No CLI runtime is implemented in this phase.

No renderer runtime implementation is modified in this phase.

## Source Stable State

HEAD:

`48b362b70aa3bb51a630b38f48b761cb9533146c`

## Source Phase

Previous closed phase:

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.IMPLEMENTATION.QA.GATE.V1`

Renderer implementation QA gate:

- `docs/product/local_media_agent/cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_implementation_qa_gate.py`

## Future CLI Command Contract

The future CLI should expose the renderer only as a local controlled metadata report command.

The future CLI must invoke only:

```python
render_controlled_ffprobe_metadata_visible_report(payload: dict) -> str
```

The pure renderer function is the only allowed rendering path.

## Allowed Input Contract

The future CLI may accept only an already-safe controlled metadata JSON payload.

The accepted payload must require:

- `input_policy` equal to `controlled_fixture_only`
- `ffprobe_command_kind` equal to `metadata_json`
- `input_path_redacted` as filename-only

Unsafe `input_path_redacted` values must be redacted or blocked.

## Forbidden Input Contract

The future CLI must reject:

- real media files as input
- arbitrary folders as input
- raw media path arguments
- folder arguments
- Windows paths
- `/mnt/c` paths
- UNC paths
- scanner execution flags
- ffprobe execution flags
- ffmpeg execution flags
- audio extraction flags
- sync flags
- transcription flags
- subtitle flags
- timeline export flags
- SaaS upload flags
- database write flags
- installer behavior flags
- client-facing readiness flags
- public demo readiness flags
- sales demo readiness flags
- production readiness flags

## Allowed Output Contract

The future CLI must support safe stdout rendering of deterministic report text.

The future CLI may support a later explicit output report path only inside a controlled output location.

Output must remain plain text or Markdown-safe text.

## Renderer Invocation Contract

The future CLI must parse the controlled metadata JSON payload and pass it to `render_controlled_ffprobe_metadata_visible_report(payload)`.

The future CLI must not use another rendering path.

## Blocked Path Behavior

Raw media paths, folder paths, Windows paths, `/mnt/c` paths, and unsafe `input_path_redacted` values must be rejected or replaced with a safe blocked report.

The future CLI must never pass real media files or folders to the renderer.

## Invalid Payload Behavior

Invalid payloads must exit safely with a blocked report.

Invalid `input_policy` values must produce a blocked report.

Invalid `ffprobe_command_kind` values must produce a blocked report.

The blocked report must include a human review required note and the next safe phase.

## Stdout Behavior

Safe stdout rendering is allowed.

Stdout must contain deterministic report text only.

Stdout must not contain full local paths, private material details, runtime internals, scanner output, media processing output, SaaS identifiers, or database identifiers.

## Controlled Output Behavior

A future explicit output report path is allowed only inside a controlled output location.

The future CLI must reject arbitrary output folders, repository paths, Windows paths, `/mnt/c` paths, UNC paths, and raw media folders as output targets.

## Explicit Non-Authorization Boundaries

This contract does not authorize:

- CLI runtime implementation
- real rodaje material
- real media files
- arbitrary folder input
- folder scanning
- scanner execution
- ffprobe execution
- ffmpeg execution
- audio extraction
- sync generation
- transcription generation
- subtitle generation
- timeline export
- SaaS upload
- database write
- installer behavior
- client-facing readiness
- public demo readiness
- sales demo readiness
- production readiness

## Acceptance Result

`LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_CONTRACT_PASS_READY_FOR_QA_GATE`

## Next Safe Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.CONTRACT.QA.GATE.V1`
