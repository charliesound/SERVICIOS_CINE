# CID Local Media Agent - Real Preflight Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1`

## Purpose

Audit the completed real preflight contract before any real preflight implementation, real media scan, scanner integration, real report generation or runtime implementation.

This phase is documentation/test-only.

It does not execute real media, does not inspect real media streams, does not call ffprobe/ffmpeg on real files, does not implement the preflight, does not integrate the scanner, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `45ce7b6`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`.
- Target preflight contract: `docs/product/local_media_agent/cid_local_media_agent_real_preflight_contract_v1.md`.
- Target preflight contract test: `tests/unit/test_cid_local_media_agent_real_preflight_contract.py`.
- Input folder contract: `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md`.
- Input folder contract QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md`.
- Privacy safety gate: `docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## QA gate scope

Allowed files for this phase:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_contract_qa_gate.py`

Runtime files may be audited by tests but must not be modified.

## Required QA assertions

This QA gate must confirm that the real preflight contract:

- declares the correct phase and stable baseline;
- references the completed input folder contract QA gate;
- references the completed privacy safety gate;
- declares documentation/test-only status;
- blocks real media execution;
- blocks real media stream inspection;
- blocks ffprobe/ffmpeg execution on real files;
- blocks real preflight implementation;
- blocks scanner integration;
- blocks real report generation;
- blocks runtime implementation;
- defines the future preflight as a fail-closed safety check;
- limits the future preflight to local filesystem, counts, sizes, extensions, output separation and privacy-safe reporting readiness;
- forbids media decoding, media stream probing, frame extraction, thumbnails, waveforms, transcription, translation, sync, subtitles, NLE export and upload.

## Required input and acknowledgement assertions

This QA gate must confirm that the contract requires:

- input folder path;
- output folder path;
- local-only execution mode;
- explicit acknowledgement that selected media is internal test media owned or authorized by the developer;
- explicit acknowledgement that client material, confidential productions, original camera masters and whole-drive material are excluded;
- missing acknowledgements fail closed.

## Required folder and inventory assertions

This QA gate must confirm the future preflight checks:

- input folder is manually selected, existing, directory-based, local, readable and read-only;
- input folder is not drive root, user home root, system directory, hidden application/cache/temp directory, cloud-sync root or network share by default;
- input folder does not require elevated privileges;
- input folder does not contain symlink traversal by default;
- output folder is manually selected, local, existing unless later safe creation is authorized, writable and separated from input;
- output folder is not inside input and is not the same path as input;
- output folder does not require overwriting or copying source media;
- maximum file count: 25 media files;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3 directory levels;
- no whole-disk, user-profile, media-library or project-archive scan;
- no batch processing of multiple unrelated projects;
- no recursive traversal beyond configured depth;
- no following symlinks by default.

Any failed mandatory folder or inventory check must produce `PREFLIGHT_FAIL`.

## Required format and privacy assertions

This QA gate must confirm:

- video allowlist: `.mov`, `.mp4`, `.mxf`;
- audio allowlist: `.wav`, `.aif`, `.aiff`;
- all other extensions are ignored or rejected until a later explicit format-support gate exists;
- format support is never inferred by decoding media content in the first-test path;
- no full private paths in user-facing reports by default;
- no user home directory exposure by default;
- no client names or project names in logs by default;
- no telemetry containing file names, full paths, client names or project names;
- no upload, cloud sync or external API transmission;
- errors fail closed when path privacy cannot be guaranteed.

## Required result contract assertions

This QA gate must confirm the future preflight statuses:

- `PREFLIGHT_PASS` only when every mandatory check passes;
- `PREFLIGHT_FAIL` when any mandatory check fails;
- `PREFLIGHT_BLOCKED` when the operation is outside the authorized first-test scope.

This QA gate must confirm that the future preflight result includes only sanitized operational data:

- sanitized input folder label;
- sanitized output folder label;
- media file count;
- total selected media size bucket;
- maximum detected scan depth;
- accepted extension counts;
- ignored or rejected extension counts;
- failed check identifiers;
- human-readable remediation guidance without private full paths.

This QA gate must confirm that the future preflight result excludes full private paths, raw filenames, client names, project names, media hashes and media content.

## Required next-step assertions

This QA gate must confirm that additional gates are still required before real execution:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this QA gate

This QA gate does not authorize:

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

## QA decision

`REAL_PREFLIGHT_CONTRACT_QA_GATE_READY_FOR_IMPLEMENTATION_CONTRACT_WITH_RESTRICTIONS`

A future phase may define implementation boundaries. No real media execution is authorized by this QA gate.
