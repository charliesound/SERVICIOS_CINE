# CID Local Media Agent - Real Preflight Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`

## Purpose

Define the mandatory contract for a future real preflight before any real media scan, real ffprobe/ffmpeg use, scanner integration, real report generation or runtime implementation.

This phase is documentation/test-only.

It does not execute real media, does not inspect real media streams, does not call ffprobe/ffmpeg on real files, does not implement the preflight, does not integrate the scanner, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `e42c575`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1`.
- Input folder contract: `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md`.
- Input folder contract QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md`.
- Privacy safety gate: `docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md`.
- Real test scope contract: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md`.
- Real test scope QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## Contract scope

The future real preflight must be a fail-closed safety check that runs before any real scan or report generation.

The future real preflight may only validate local filesystem conditions, counts, sizes, extensions, output separation and privacy-safe reporting readiness.

The future real preflight must not decode media, probe media streams, extract frames, create thumbnails, create waveforms, transcribe, translate, sync, subtitle, export to NLE or upload anything.

## Required preflight inputs

A future real preflight must require explicit user-provided values for:

- input folder path;
- output folder path;
- local-only execution mode;
- explicit acknowledgement that the selected media is internal test media owned or authorized by the developer;
- explicit acknowledgement that client material, confidential productions, original camera masters and whole-drive material are excluded.

Missing acknowledgements must fail closed.

## Required input folder checks

A future real preflight must confirm that the input folder:

- is manually selected by the user;
- exists before execution;
- is a directory, not a file;
- is local to the machine running the tool;
- is not a drive root;
- is not the user home directory root;
- is not a system directory;
- is not a hidden application/cache/temp directory;
- is not a cloud-sync root by default;
- is not a network share by default;
- is readable by the current user;
- is treated as read-only input by CID Local Media Agent;
- does not require elevated privileges;
- does not contain symlink traversal by default.

Any failed input folder check must produce `PREFLIGHT_FAIL`.

## Required output folder checks

A future real preflight must confirm that the output folder:

- is manually selected by the user;
- is local to the machine running the tool;
- exists before execution unless a later explicit implementation phase authorizes safe creation;
- is writable by the current user;
- is separated from the input folder by default;
- is not inside the input folder by default;
- is not the same path as the input folder;
- does not require overwriting source media;
- does not require copying source media by default;
- is suitable for future metadata/report artifacts only.

Any failed output folder check must produce `PREFLIGHT_FAIL`.

## Required file inventory checks

A future real preflight may enumerate files only far enough to validate limits and extensions.

The future real preflight must enforce:

- maximum file count: 25 media files;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3 directory levels;
- no automatic scan of a whole disk, user profile, media library or project archive;
- no batch processing of multiple unrelated projects;
- no recursive traversal beyond the configured depth;
- no following symlinks by default.

Any failed inventory check must produce `PREFLIGHT_FAIL`.

## Required extension allowlist checks

A future real preflight must allow only these first-test media extensions:

- video: `.mov`, `.mp4`, `.mxf`;
- audio: `.wav`, `.aif`, `.aiff`.

All other extensions must be ignored or rejected until a later explicit format-support gate exists.

A future real preflight must never infer format support by decoding media content in this first-test path.

## Required privacy checks

A future real preflight must verify that future user-facing output can preserve path privacy:

- no full private paths in user-facing reports by default;
- no user home directory exposure by default;
- no client names or project names in logs by default;
- no telemetry containing file names, full paths, client names or project names;
- no upload, cloud sync or external API transmission;
- errors must fail closed when path privacy cannot be guaranteed.

## Required preflight result contract

A future real preflight must return one of these final statuses:

- `PREFLIGHT_PASS` only when every mandatory check passes;
- `PREFLIGHT_FAIL` when any mandatory check fails;
- `PREFLIGHT_BLOCKED` when the operation is outside the authorized first-test scope.

A future real preflight result must include:

- sanitized input folder label;
- sanitized output folder label;
- media file count;
- total selected media size bucket;
- maximum detected scan depth;
- accepted extension counts;
- ignored or rejected extension counts;
- failed check identifiers;
- human-readable remediation guidance without private full paths.

A future real preflight result must not include full private paths, raw filenames, client names, project names, media hashes or media content.

## Required future gates before execution

This real preflight contract does not authorize real execution. Before any first real execution, the following phases are still required:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this phase

This real preflight contract does not authorize:

- real media execution;
- ffprobe or ffmpeg execution on real files;
- media stream probing;
- media decoding;
- real preflight implementation;
- scanner integration;
- real report generation;
- thumbnail, waveform or frame extraction;
- sync;
- transcription;
- translation;
- subtitle generation;
- NLE export;
- runtime implementation;
- packaging implementation;
- installable entry point;
- shell launcher;
- desktop app;
- licensing;
- client delivery;
- SaaS/backend/frontend/database/Docker/Alembic work;
- Stripe, AI Jobs, credits or ledger work.

## Contract decision

`REAL_PREFLIGHT_CONTRACT_READY_FOR_QA_GATE_WITH_RESTRICTIONS`

A future phase may audit this preflight contract. No real media execution is authorized by this document.
