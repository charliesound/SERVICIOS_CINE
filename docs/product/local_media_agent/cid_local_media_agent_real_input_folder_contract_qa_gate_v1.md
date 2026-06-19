# CID Local Media Agent - Real Input Folder Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.QA.GATE.V1`

## Purpose

Audit the completed real input-folder contract before any real preflight contract, real preflight implementation, scanner integration or real media execution.

This phase is documentation/test-only.

It does not execute real media, does not call ffprobe/ffmpeg on real files, does not implement real preflight, does not implement scanner integration, does not generate a real report, and does not modify runtime code.

## Stable baseline

- Stable HEAD before this phase: `efd347f`.
- Previous completed phase: `CID.LOCAL_MEDIA_AGENT.REAL.INPUT.FOLDER.CONTRACT.V1`.
- Target input folder contract: `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_v1.md`.
- Target input folder contract test: `tests/unit/test_cid_local_media_agent_real_input_folder_contract.py`.
- Privacy safety gate: `docs/product/local_media_agent/cid_local_media_agent_real_media_privacy_safety_gate_v1.md`.
- Real test scope contract: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_v1.md`.
- Real test scope QA gate: `docs/product/local_media_agent/cid_local_media_agent_real_test_scope_contract_qa_gate_v1.md`.
- Current synthetic wrapper: `scripts/cid_local_media_agent_synthetic_visible_report_cli.py`.
- Current synthetic preflight helper: `scripts/cid_local_media_agent_synthetic_visible_report_preflight_check.py`.
- Current synthetic renderer: `scripts/cid_local_media_agent_synthetic_visible_report_renderer.py`.
- Current scanner remains out of this phase: `scripts/cid_media_agent_scan.py`.

## QA gate scope

Allowed files for this phase:

- `docs/product/local_media_agent/cid_local_media_agent_real_input_folder_contract_qa_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_real_input_folder_contract_qa_gate.py`

Runtime files may be audited by tests but must not be modified.

## Required QA assertions

This QA gate must confirm that the real input-folder contract:

- declares the correct phase and stable baseline;
- references the completed privacy safety gate;
- declares documentation/test-only status;
- blocks real media execution in the current phase;
- blocks ffprobe/ffmpeg execution on real files;
- blocks real preflight implementation;
- blocks scanner integration;
- blocks real report generation;
- blocks runtime implementation;
- defines the input folder as manually selected and local-only;
- requires copied test media owned or explicitly authorized by the developer;
- excludes client material, confidential productions, original camera masters and whole-drive material;
- requires the input folder to exist before execution;
- requires the input folder to be a directory, not a file;
- rejects drive roots, user home root, system directories and hidden application/cache/temp directories;
- rejects cloud-sync roots and network shares by default;
- treats input as read-only;
- requires path privacy by default.

## Required limit assertions

This QA gate must confirm that the first real input-folder contract keeps the test intentionally small:

- maximum file count: 25 media files;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3 directory levels;
- no automatic scan of a whole disk, user profile, media library or project archive;
- no batch processing of multiple unrelated projects;
- limits may change only through a later explicit capacity gate.

## Required format assertions

This QA gate must confirm the first real input-folder extension allowlist:

- video: `.mov`, `.mp4`, `.mxf`;
- audio: `.wav`, `.aif`, `.aiff`;
- all other extensions are ignored or rejected until a later explicit format-support gate exists.

## Required output assertions

This QA gate must confirm output-folder separation:

- manually selected local output folder;
- separated from input folder by default;
- no overwrite of source media;
- no copy of source media by default;
- output contains only future metadata/report artifacts, never modified source media.

## Required next-step assertions

This QA gate must confirm that the contract still requires additional gates before real execution:

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.CONTRACT.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.SCAN.MINIMAL.IMPLEMENTATION.V1`
5. `CID.LOCAL_MEDIA_AGENT.REAL.TEST.EXECUTION.READINESS.GATE.V1`

## Explicitly blocked in this QA gate

This QA gate does not authorize:

- real media execution;
- ffprobe or ffmpeg execution on real files;
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

`REAL_INPUT_FOLDER_CONTRACT_QA_GATE_READY_FOR_REAL_PREFLIGHT_CONTRACT_WITH_RESTRICTIONS`

A future phase may define the real preflight contract. No real media execution is authorized by this QA gate.
